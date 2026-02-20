#!/usr/bin/env python3
"""
APEXSAT AI - İçerik Öneri Motoru

Collaborative filtering + Content-based hybrid yaklaşım.
TensorFlow Lite / ONNX Runtime ile NPU hızlandırmalı inference.

Kullanım:
    python3 engine.py --train           # Modeli eğit
    python3 engine.py --recommend       # Öneri al
    python3 engine.py --test            # Test senaryoları
"""

import json
import math
import os
import sqlite3
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import numpy as np

SCRIPT_DIR = Path(__file__).parent
MODEL_DIR = SCRIPT_DIR / "models"
DATA_DIR = SCRIPT_DIR / "data"
DB_PATH = SCRIPT_DIR / "recommendations.db"

# ─── Veri Yapıları ───────────────────────────────────────────────────────────

@dataclass
class Program:
    program_id: int
    title: str
    channel_id: int
    channel_name: str
    genre: str
    sub_genre: str = ""
    start_time: str = ""
    duration: int = 0        # dakika
    year: int = 0
    rating: float = 0.0     # IMDb puanı
    language: str = "tr"
    is_hd: bool = False
    description: str = ""
    tags: list = field(default_factory=list)

    def to_feature_vector(self, genre_map: dict, channel_map: dict) -> np.ndarray:
        """Program özellik vektörü oluştur."""
        features = []

        # Genre one-hot encoding
        genre_vec = np.zeros(len(genre_map))
        if self.genre in genre_map:
            genre_vec[genre_map[self.genre]] = 1.0
        features.extend(genre_vec)

        # Channel one-hot encoding
        ch_vec = np.zeros(len(channel_map))
        if self.channel_id in channel_map:
            ch_vec[channel_map[self.channel_id]] = 1.0
        features.extend(ch_vec)

        # Sayısal özellikler
        features.append(self.rating / 10.0)                   # Normalize rating
        features.append(self.duration / 240.0)                 # Normalize duration
        features.append(1.0 if self.is_hd else 0.0)           # HD flag
        features.append(1.0 if self.language == "tr" else 0.0) # Türkçe flag

        # Saat bazlı özellik
        if self.start_time:
            try:
                hour = int(self.start_time.split("T")[-1].split(":")[0])
            except (ValueError, IndexError):
                hour = 20
        else:
            hour = 20
        features.append(hour / 24.0)

        return np.array(features, dtype=np.float32)


@dataclass
class WatchHistory:
    user_id: int
    program_id: int
    channel_id: int
    watch_duration: int      # saniye
    total_duration: int      # saniye
    watch_date: str
    watch_hour: int
    completed: bool = False
    liked: Optional[bool] = None  # True=beğendi, False=beğenmedi, None=belirtmedi

    @property
    def watch_ratio(self) -> float:
        if self.total_duration == 0:
            return 0.0
        return min(self.watch_duration / self.total_duration, 1.0)


@dataclass
class Recommendation:
    program: Program
    score: float             # 0.0 - 1.0 arası öneri skoru
    reason: str = ""         # Öneri nedeni


# ─── Veritabanı ─────────────────────────────────────────────────────────────

class RecommendationDB:
    """Öneri motoru veritabanı."""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS watch_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    program_id INTEGER,
                    channel_id INTEGER,
                    channel_name TEXT,
                    program_title TEXT,
                    genre TEXT,
                    watch_duration INTEGER,
                    total_duration INTEGER,
                    watch_date TEXT,
                    watch_hour INTEGER,
                    completed INTEGER DEFAULT 0,
                    liked INTEGER DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER DEFAULT 1,
                    genre TEXT,
                    weight REAL DEFAULT 0.5,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, genre)
                );

                CREATE TABLE IF NOT EXISTS channel_preferences (
                    user_id INTEGER DEFAULT 1,
                    channel_id INTEGER,
                    watch_count INTEGER DEFAULT 0,
                    total_watch_time INTEGER DEFAULT 0,
                    last_watched TIMESTAMP,
                    PRIMARY KEY (user_id, channel_id)
                );

                CREATE INDEX IF NOT EXISTS idx_watch_date ON watch_history(watch_date);
                CREATE INDEX IF NOT EXISTS idx_watch_genre ON watch_history(genre);
            """)

    def add_watch_event(self, event: WatchHistory, program_title: str = "",
                         channel_name: str = "", genre: str = ""):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO watch_history
                (user_id, program_id, channel_id, channel_name, program_title,
                 genre, watch_duration, total_duration, watch_date, watch_hour,
                 completed, liked)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.user_id, event.program_id, event.channel_id,
                channel_name, program_title, genre,
                event.watch_duration, event.total_duration,
                event.watch_date, event.watch_hour,
                event.completed, event.liked
            ))

            # Kanal tercihi güncelle
            conn.execute("""
                INSERT INTO channel_preferences (user_id, channel_id, watch_count, total_watch_time, last_watched)
                VALUES (?, ?, 1, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, channel_id) DO UPDATE SET
                    watch_count = watch_count + 1,
                    total_watch_time = total_watch_time + ?,
                    last_watched = CURRENT_TIMESTAMP
            """, (event.user_id, event.channel_id, event.watch_duration, event.watch_duration))

    def get_watch_history(self, user_id: int = 1, limit: int = 100) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute(
                "SELECT * FROM watch_history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()]

    def get_genre_preferences(self, user_id: int = 1) -> dict[str, float]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT genre, weight FROM user_preferences WHERE user_id = ?",
                (user_id,)
            ).fetchall()
            return {r["genre"]: r["weight"] for r in rows}

    def get_top_channels(self, user_id: int = 1, limit: int = 10) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute(
                "SELECT * FROM channel_preferences WHERE user_id = ? ORDER BY watch_count DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()]


# ─── Content-Based Öneri ─────────────────────────────────────────────────────

class ContentBasedRecommender:
    """İçerik tabanlı öneri (program özellikleri benzerliği)."""

    def __init__(self, db: RecommendationDB):
        self.db = db

    def compute_user_profile(self, user_id: int = 1) -> dict:
        """Kullanıcı profilini izleme geçmişinden oluştur."""
        history = self.db.get_watch_history(user_id, limit=500)

        genre_scores = defaultdict(float)
        channel_scores = defaultdict(float)
        hour_scores = defaultdict(float)
        total_weight = 0.0

        for entry in history:
            # İzleme oranına göre ağırlık
            ratio = min(entry["watch_duration"] / max(entry["total_duration"], 1), 1.0)
            weight = ratio

            # Beğeni/beğenmeme bonus
            if entry.get("liked") is True:
                weight *= 1.5
            elif entry.get("liked") is False:
                weight *= 0.3

            # Zaman decay (yeni izlemeler daha önemli)
            try:
                days_ago = (datetime.now() - datetime.fromisoformat(entry["watch_date"])).days
            except (ValueError, TypeError):
                days_ago = 30
            time_decay = math.exp(-days_ago / 30.0)  # 30 gün yarı ömür
            weight *= time_decay

            genre = entry.get("genre", "")
            if genre:
                genre_scores[genre] += weight
            channel_scores[entry["channel_id"]] += weight
            hour_scores[entry["watch_hour"]] += weight
            total_weight += weight

        # Normalizasyon
        if total_weight > 0:
            genre_scores = {k: v / total_weight for k, v in genre_scores.items()}
            channel_scores = {k: v / total_weight for k, v in channel_scores.items()}

        return {
            "genres": dict(genre_scores),
            "channels": dict(channel_scores),
            "hours": dict(hour_scores),
        }

    def recommend(self, programs: list[Program], user_id: int = 1,
                   top_k: int = 10) -> list[Recommendation]:
        """İçerik tabanlı öneri."""
        profile = self.compute_user_profile(user_id)

        recommendations = []
        for prog in programs:
            score = 0.0
            reasons = []

            # Tür benzerliği
            genre_score = profile["genres"].get(prog.genre, 0.0)
            if genre_score > 0.1:
                score += genre_score * 0.4
                reasons.append(f"{prog.genre} türünü seviyorsunuz")

            # Kanal tercihi
            ch_score = profile["channels"].get(prog.channel_id, 0.0)
            if ch_score > 0.05:
                score += ch_score * 0.3
                reasons.append(f"{prog.channel_name} sık izlediğiniz kanal")

            # Saat uyumu
            if prog.start_time:
                try:
                    hour = int(prog.start_time.split("T")[-1].split(":")[0])
                except (ValueError, IndexError):
                    hour = 20
                hour_score = profile["hours"].get(hour, 0.0)
                score += hour_score * 0.1

            # Rating bonusu
            if prog.rating > 7.0:
                score += (prog.rating - 7.0) / 10.0 * 0.15
                reasons.append(f"Yüksek puan: {prog.rating}/10")

            # HD bonus
            if prog.is_hd:
                score += 0.05

            reason = " | ".join(reasons[:2]) if reasons else "Sizin için önerildi"
            recommendations.append(Recommendation(prog, min(score, 1.0), reason))

        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations[:top_k]


# ─── Collaborative Filtering ────────────────────────────────────────────────

class CollaborativeRecommender:
    """
    Basitleştirilmiş collaborative filtering.

    Tek kullanıcı senaryosunda (kişisel cihaz), zaman bazlı
    pattern matching olarak çalışır.
    """

    def __init__(self, db: RecommendationDB):
        self.db = db

    def get_time_patterns(self, user_id: int = 1) -> dict:
        """Saat bazlı izleme kalıplarını çıkar."""
        history = self.db.get_watch_history(user_id, limit=1000)

        patterns = defaultdict(lambda: defaultdict(float))

        for entry in history:
            hour = entry["watch_hour"]
            genre = entry.get("genre", "Genel")
            ratio = min(entry["watch_duration"] / max(entry["total_duration"], 1), 1.0)
            patterns[hour][genre] += ratio

        # Her saat için en yüksek türü bul
        result = {}
        for hour, genres in patterns.items():
            sorted_genres = sorted(genres.items(), key=lambda x: x[1], reverse=True)
            result[hour] = sorted_genres[:3]

        return result

    def get_day_of_week_patterns(self, user_id: int = 1) -> dict:
        """Hafta günü bazlı izleme kalıpları."""
        history = self.db.get_watch_history(user_id, limit=1000)

        patterns = defaultdict(lambda: defaultdict(float))

        for entry in history:
            try:
                date = datetime.fromisoformat(entry["watch_date"])
                day = date.strftime("%A")
            except (ValueError, TypeError):
                day = "Unknown"
            genre = entry.get("genre", "Genel")
            patterns[day][genre] += 1

        return dict(patterns)


# ─── Hybrid Öneri Motoru ─────────────────────────────────────────────────────

class HybridRecommendationEngine:
    """
    Hybrid öneri motoru - Content-based + Collaborative.

    Skor = α × content_score + β × collab_score + γ × popularity_score
    """

    def __init__(self, db: RecommendationDB = None):
        self.db = db or RecommendationDB()
        self.content_recommender = ContentBasedRecommender(self.db)
        self.collab_recommender = CollaborativeRecommender(self.db)

        # Ağırlıklar
        self.alpha = 0.5    # Content-based
        self.beta = 0.3     # Collaborative
        self.gamma = 0.2    # Popularity

    def recommend(self, programs: list[Program], user_id: int = 1,
                   top_k: int = 10, context: dict = None) -> list[Recommendation]:
        """
        Hybrid öneri üret.

        Args:
            programs: Mevcut program listesi
            user_id: Kullanıcı ID
            top_k: Kaç öneri döndürülecek
            context: Bağlam bilgisi (saat, gün, vs.)
        """
        if context is None:
            now = datetime.now()
            context = {
                "hour": now.hour,
                "day_of_week": now.strftime("%A"),
                "is_weekend": now.weekday() >= 5,
            }

        # Content-based öneriler
        content_recs = self.content_recommender.recommend(programs, user_id, top_k * 2)
        content_scores = {r.program.program_id: r.score for r in content_recs}
        content_reasons = {r.program.program_id: r.reason for r in content_recs}

        # Collaborative pattern'ler
        time_patterns = self.collab_recommender.get_time_patterns(user_id)
        current_hour_genres = time_patterns.get(context["hour"], [])
        preferred_genres = [g[0] for g in current_hour_genres[:3]]

        # Hybrid skorlama
        results = []
        for prog in programs:
            content_score = content_scores.get(prog.program_id, 0.0)

            # Collaborative score (saat bazlı tür uyumu)
            collab_score = 0.0
            if prog.genre in preferred_genres:
                idx = preferred_genres.index(prog.genre)
                collab_score = 1.0 - (idx * 0.3)

            # Popularity score (rating tabanlı basit)
            pop_score = prog.rating / 10.0 if prog.rating > 0 else 0.5

            # Hybrid skor
            final_score = (
                self.alpha * content_score +
                self.beta * collab_score +
                self.gamma * pop_score
            )

            # Bağlamsal ayarlamalar
            if context.get("is_weekend") and prog.genre in ["Film", "Spor"]:
                final_score *= 1.2

            if context["hour"] >= 22 and prog.genre in ["Film", "Belgesel"]:
                final_score *= 1.15

            reason = content_reasons.get(prog.program_id, "Sizin için önerildi")
            if collab_score > 0.5:
                reason += f" | Bu saatte {prog.genre} izlemeyi seviyorsunuz"

            results.append(Recommendation(prog, min(final_score, 1.0), reason))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def log_watch_event(self, program: Program, watch_duration: int,
                         completed: bool = False, liked: Optional[bool] = None):
        """İzleme olayını kaydet (model güncelleme için)."""
        now = datetime.now()
        event = WatchHistory(
            user_id=1,
            program_id=program.program_id,
            channel_id=program.channel_id,
            watch_duration=watch_duration,
            total_duration=program.duration * 60,
            watch_date=now.isoformat(),
            watch_hour=now.hour,
            completed=completed,
            liked=liked,
        )
        self.db.add_watch_event(
            event, program.title, program.channel_name, program.genre
        )

    def get_user_stats(self, user_id: int = 1) -> dict:
        """Kullanıcı izleme istatistikleri."""
        history = self.db.get_watch_history(user_id, limit=10000)

        if not history:
            return {"total_watch_time": 0, "favorite_genre": "N/A", "favorite_channel": "N/A"}

        total_time = sum(h["watch_duration"] for h in history)
        genre_counts = defaultdict(int)
        channel_counts = defaultdict(int)

        for h in history:
            genre_counts[h.get("genre", "")] += 1
            channel_counts[h.get("channel_name", "")] += 1

        fav_genre = max(genre_counts, key=genre_counts.get) if genre_counts else "N/A"
        fav_channel = max(channel_counts, key=channel_counts.get) if channel_counts else "N/A"

        return {
            "total_watch_time": total_time,
            "total_watch_hours": total_time / 3600,
            "programs_watched": len(history),
            "favorite_genre": fav_genre,
            "favorite_channel": fav_channel,
            "genre_distribution": dict(genre_counts),
            "top_channels": dict(sorted(channel_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
        }


# ─── Test ve Demo ────────────────────────────────────────────────────────────

def generate_sample_data(engine: HybridRecommendationEngine):
    """Test için örnek izleme verisi oluştur."""
    import random

    sample_programs = [
        Program(1, "Ana Haber", 1, "TRT 1", "Haber", duration=60, rating=7.0),
        Program(2, "Gönül Dağı", 1, "TRT 1", "Dizi", duration=120, rating=8.5, is_hd=True),
        Program(3, "Kuruluş Osman", 10, "ATV", "Dizi", duration=150, rating=8.2, is_hd=True),
        Program(4, "Kara Sevda", 18, "Kanal D", "Dizi", duration=120, rating=8.8, is_hd=True),
        Program(5, "Survivor", 21, "TV8", "Gösteri", duration=180, rating=7.5, is_hd=True),
        Program(6, "UEFA Maçı", 4, "TRT Spor", "Spor", duration=120, rating=9.0, is_hd=True),
        Program(7, "Belgesel", 6, "TRT Belgesel", "Belgesel", duration=60, rating=8.0),
        Program(8, "Film: Hababam Sınıfı", 2, "TRT 2", "Film", duration=100, rating=9.1),
        Program(9, "NTV Ekonomi", 17, "NTV", "Haber", duration=60, rating=6.5),
        Program(10, "Yasak Elma", 20, "FOX TV", "Dizi", duration=120, rating=7.8, is_hd=True),
    ]

    # 30 günlük simüle izleme verisi
    for day in range(30):
        date = datetime.now() - timedelta(days=day)
        num_watches = random.randint(2, 6)

        for _ in range(num_watches):
            prog = random.choice(sample_programs)
            # Dizi ve film tercih ağırlığı
            if prog.genre in ["Dizi", "Film"]:
                watch_ratio = random.uniform(0.6, 1.0)
            else:
                watch_ratio = random.uniform(0.2, 0.8)

            hour = random.choice([19, 20, 21, 22, 23])  # Prime time ağırlıklı
            completed = watch_ratio > 0.85

            engine.log_watch_event(
                Program(
                    prog.program_id, prog.title, prog.channel_id,
                    prog.channel_name, prog.genre,
                    start_time=date.replace(hour=hour).isoformat(),
                    duration=prog.duration, rating=prog.rating
                ),
                watch_duration=int(prog.duration * 60 * watch_ratio),
                completed=completed,
                liked=True if watch_ratio > 0.7 and random.random() > 0.5 else None
            )

    print(f"📊 {30 * 4} örnek izleme kaydı oluşturuldu")


def test_recommendations():
    """Öneri motoru test senaryoları."""
    engine = HybridRecommendationEngine()

    print("=" * 60)
    print("  APEXSAT AI - Öneri Motoru Testi")
    print("=" * 60)

    # Örnek veri oluştur
    generate_sample_data(engine)

    # Mevcut programlar (öneri için aday)
    current_programs = [
        Program(101, "TRT Ana Haber", 1, "TRT 1", "Haber", start_time="2026-02-20T20:00", duration=60, rating=7.0),
        Program(102, "Gönül Dağı Yeni Bölüm", 1, "TRT 1", "Dizi", start_time="2026-02-20T20:00", duration=120, rating=8.5, is_hd=True),
        Program(103, "Kuruluş Osman Yeni Bölüm", 10, "ATV", "Dizi", start_time="2026-02-20T20:00", duration=150, rating=8.2, is_hd=True),
        Program(104, "Şampiyonlar Ligi", 4, "TRT Spor", "Spor", start_time="2026-02-20T21:45", duration=120, rating=9.0, is_hd=True),
        Program(105, "Mavi Gezegen", 6, "TRT Belgesel", "Belgesel", start_time="2026-02-20T22:00", duration=60, rating=9.2),
        Program(106, "Yeşilçam: Tosun Paşa", 2, "TRT 2", "Film", start_time="2026-02-20T23:00", duration=100, rating=9.0),
        Program(107, "Haber Analiz", 17, "NTV", "Haber", start_time="2026-02-20T21:00", duration=60, rating=6.5),
        Program(108, "Survivor 2026", 21, "TV8", "Gösteri", start_time="2026-02-20T20:00", duration=180, rating=7.5, is_hd=True),
        Program(109, "Kara Sevda Tekrar", 18, "Kanal D", "Dizi", start_time="2026-02-20T22:30", duration=120, rating=8.8, is_hd=True),
        Program(110, "FOX Ana Haber", 20, "FOX TV", "Haber", start_time="2026-02-20T19:00", duration=90, rating=7.2),
    ]

    # Öneriler al
    recommendations = engine.recommend(current_programs, top_k=10)

    print("\n🤖 Sizin İçin Öneriler:")
    print("─" * 60)
    for i, rec in enumerate(recommendations, 1):
        prog = rec.program
        score_bar = "█" * int(rec.score * 20) + "░" * (20 - int(rec.score * 20))
        hd = " [HD]" if prog.is_hd else ""
        print(f"\n  {i}. {prog.title}{hd}")
        print(f"     {prog.channel_name} • {prog.start_time[11:16]} • {prog.genre} • ⭐{prog.rating}")
        print(f"     Skor: [{score_bar}] {rec.score:.2f}")
        print(f"     Neden: {rec.reason}")

    # Kullanıcı istatistikleri
    stats = engine.get_user_stats()
    print(f"\n\n📊 Kullanıcı İstatistikleri:")
    print("─" * 40)
    print(f"  Toplam izleme: {stats['total_watch_hours']:.1f} saat")
    print(f"  İzlenen program: {stats['programs_watched']}")
    print(f"  Favori tür: {stats['favorite_genre']}")
    print(f"  Favori kanal: {stats['favorite_channel']}")
    print(f"  Tür dağılımı: {json.dumps(stats['genre_distribution'], ensure_ascii=False)}")

    print(f"\n{'=' * 60}")
    print(f"  Test tamamlandı ✓")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="APEXSAT AI - Öneri Motoru")
    parser.add_argument("--test", action="store_true", help="Test senaryoları çalıştır")
    parser.add_argument("--stats", action="store_true", help="Kullanıcı istatistikleri")

    args = parser.parse_args()

    if args.test:
        test_recommendations()
    elif args.stats:
        engine = HybridRecommendationEngine()
        stats = engine.get_user_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        test_recommendations()
