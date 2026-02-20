#!/usr/bin/env python3
"""
APEXSAT AI - EPG (Elektronik Program Rehberi) Motoru

DVB-SI EIT tablolarından ve internet kaynaklarından (XMLTV) EPG verisi toplar.
AI ile zenginleştirilmiş meta-data desteği.
"""

import json
import sqlite3
import time
import struct
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


SCRIPT_DIR = Path(__file__).parent
EPG_DB = SCRIPT_DIR / "epg.db"


@dataclass
class EPGEvent:
    channel_id: int
    event_id: int
    start_time: datetime
    duration: int           # dakika
    title: str
    description: str = ""
    genre: str = ""
    sub_genre: str = ""
    parental_rating: int = 0
    language: str = "tur"
    is_hd: bool = False
    has_subtitle: bool = False
    has_audio_desc: bool = False
    # AI zenginleştirme alanları
    ai_category: str = ""
    ai_score: float = 0.0
    imdb_id: str = ""
    imdb_rating: float = 0.0
    poster_url: str = ""

    @property
    def end_time(self) -> datetime:
        return self.start_time + timedelta(minutes=self.duration)

    @property
    def is_current(self) -> bool:
        now = datetime.now()
        return self.start_time <= now < self.end_time

    @property
    def progress_percent(self) -> float:
        if not self.is_current:
            return 0.0 if datetime.now() < self.start_time else 100.0
        elapsed = (datetime.now() - self.start_time).total_seconds()
        total = self.duration * 60
        return min((elapsed / total) * 100, 100.0)


# DVB-SI EIT Tür tablosu (ETSI EN 300 468)
DVB_CONTENT_TYPES = {
    0x10: "Film", 0x11: "Polisiye/Gerilim", 0x12: "Macera/Western",
    0x13: "Bilim Kurgu/Fantezi", 0x14: "Komedi", 0x15: "Melodram/Romantik",
    0x16: "Romantik", 0x17: "Ciddi/Klasik", 0x18: "Yetişkin",
    0x20: "Haber", 0x21: "Haber/Hava Durumu", 0x22: "Haber Magazin",
    0x23: "Belgesel", 0x24: "Tartışma/Röportaj",
    0x30: "Gösteri/Oyun", 0x31: "Oyun Programı", 0x32: "Çeşitli",
    0x33: "Talk Show",
    0x40: "Spor", 0x41: "Özel Etkinlik", 0x42: "Spor Dergisi",
    0x43: "Futbol", 0x44: "Tenis", 0x45: "Takım Sporları",
    0x46: "Atletizm", 0x47: "Motor Sporları",
    0x50: "Çocuk", 0x51: "Çocuk (5-6)", 0x52: "Çocuk (7-8)",
    0x53: "Çocuk (10-16)", 0x54: "Bilgilendirici/Eğitici", 0x55: "Çizgi Film",
    0x60: "Müzik/Bale/Dans", 0x61: "Rock/Pop", 0x62: "Ciddi Müzik",
    0x63: "Halk/Geleneksel", 0x64: "Caz",
    0x70: "Sanat/Kültür", 0x71: "Sahne Sanatları", 0x72: "Güzel Sanatlar",
    0x73: "Din", 0x74: "Popüler Kültür",
    0x80: "Sosyal/Politik", 0x81: "Dergi/Rapor", 0x82: "Ekonomi/Sosyal",
    0x83: "Meşhur Kişiler",
    0x90: "Eğitim/Bilim", 0x91: "Doğa/Hayvan", 0x92: "Teknoloji/Bilim",
    0xA0: "Boş Zaman", 0xA1: "Seyahat/Turizm", 0xA2: "El Sanatları",
    0xA3: "Otomobil", 0xA4: "Fitness/Sağlık", 0xA5: "Yemek/Mutfak",
    0xA6: "Alışveriş", 0xA7: "Bahçe",
}


class EPGDatabase:
    """EPG veritabanı yöneticisi."""

    def __init__(self, db_path: Path = EPG_DB):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS epg_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER NOT NULL,
                    event_id INTEGER,
                    start_time TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    genre TEXT DEFAULT '',
                    sub_genre TEXT DEFAULT '',
                    parental_rating INTEGER DEFAULT 0,
                    language TEXT DEFAULT 'tur',
                    is_hd INTEGER DEFAULT 0,
                    has_subtitle INTEGER DEFAULT 0,
                    has_audio_desc INTEGER DEFAULT 0,
                    ai_category TEXT DEFAULT '',
                    ai_score REAL DEFAULT 0,
                    imdb_id TEXT DEFAULT '',
                    imdb_rating REAL DEFAULT 0,
                    poster_url TEXT DEFAULT '',
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(channel_id, event_id)
                );

                CREATE TABLE IF NOT EXISTS epg_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    url TEXT DEFAULT '',
                    last_fetched TIMESTAMP,
                    event_count INTEGER DEFAULT 0
                );

                CREATE INDEX IF NOT EXISTS idx_epg_channel ON epg_events(channel_id);
                CREATE INDEX IF NOT EXISTS idx_epg_start ON epg_events(start_time);
                CREATE INDEX IF NOT EXISTS idx_epg_genre ON epg_events(genre);
            """)

    def save_event(self, event: EPGEvent):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO epg_events
                (channel_id, event_id, start_time, duration, title, description,
                 genre, sub_genre, parental_rating, language, is_hd,
                 has_subtitle, has_audio_desc, ai_category, ai_score,
                 imdb_id, imdb_rating, poster_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.channel_id, event.event_id,
                event.start_time.isoformat(), event.duration,
                event.title, event.description,
                event.genre, event.sub_genre, event.parental_rating,
                event.language, event.is_hd,
                event.has_subtitle, event.has_audio_desc,
                event.ai_category, event.ai_score,
                event.imdb_id, event.imdb_rating, event.poster_url
            ))

    def save_events(self, events: list[EPGEvent]):
        for event in events:
            self.save_event(event)

    def get_current_events(self, channel_ids: list[int] = None) -> list[dict]:
        """Şu anda yayınlanan programları getir."""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = """
                SELECT * FROM epg_events
                WHERE start_time <= ?
                AND datetime(start_time, '+' || duration || ' minutes') > ?
            """
            params = [now, now]
            if channel_ids:
                placeholders = ",".join("?" * len(channel_ids))
                query += f" AND channel_id IN ({placeholders})"
                params.extend(channel_ids)
            query += " ORDER BY channel_id"
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    def get_schedule(self, channel_id: int, date: str = None) -> list[dict]:
        """Belirli kanalın programını getir."""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM epg_events
                WHERE channel_id = ?
                AND date(start_time) = ?
                ORDER BY start_time
            """, (channel_id, date)).fetchall()
            return [dict(r) for r in rows]

    def search_programs(self, query: str, genre: str = None) -> list[dict]:
        """Program ara (başlık ve açıklama)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            sql = """
                SELECT * FROM epg_events
                WHERE (title LIKE ? OR description LIKE ?)
            """
            params = [f"%{query}%", f"%{query}%"]
            if genre:
                sql += " AND genre = ?"
                params.append(genre)
            sql += " ORDER BY start_time LIMIT 50"
            return [dict(r) for r in conn.execute(sql, params).fetchall()]

    def get_genres(self) -> list[dict]:
        """Mevcut türleri ve sayılarını getir."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute("""
                SELECT genre, COUNT(*) as count FROM epg_events
                WHERE genre != '' GROUP BY genre ORDER BY count DESC
            """).fetchall()]

    def cleanup_old_events(self, days_before: int = 7):
        """Eski EPG verilerini temizle."""
        cutoff = (datetime.now() - timedelta(days=days_before)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            deleted = conn.execute(
                "DELETE FROM epg_events WHERE start_time < ?", (cutoff,)
            ).rowcount
            print(f"🗑️  {deleted} eski EPG kaydı silindi (>{days_before} gün)")


class EITParser:
    """
    DVB-SI EIT (Event Information Table) parser.
    ETSI EN 300 468 standardına uygun.
    """

    TABLE_ID_ACTUAL_PF = 0x4E       # Şimdiki/sonraki (mevcut TS)
    TABLE_ID_OTHER_PF = 0x4F        # Şimdiki/sonraki (diğer TS)
    TABLE_ID_ACTUAL_SCHED = 0x50    # Program (mevcut TS) - 0x50-0x5F
    TABLE_ID_OTHER_SCHED = 0x60    # Program (diğer TS) - 0x60-0x6F

    def parse_eit_section(self, data: bytes) -> list[EPGEvent]:
        """EIT section'ı parse et."""
        events = []

        if len(data) < 14:
            return events

        table_id = data[0]
        section_length = ((data[1] & 0x0F) << 8) | data[2]
        service_id = (data[3] << 8) | data[4]
        transport_stream_id = (data[8] << 8) | data[9]
        original_network_id = (data[10] << 8) | data[11]

        offset = 14
        while offset < min(len(data) - 4, section_length + 3 - 4):
            if offset + 12 > len(data):
                break

            event_id = (data[offset] << 8) | data[offset + 1]

            # Başlangıç zamanı (MJD + UTC)
            start_time = self._parse_dvb_datetime(data[offset + 2:offset + 7])

            # Süre (BCD)
            duration_h = self._bcd_to_int(data[offset + 7])
            duration_m = self._bcd_to_int(data[offset + 8])
            duration = duration_h * 60 + duration_m

            # Durum ve descriptor loop uzunluğu
            status_byte = (data[offset + 10] << 8) | data[offset + 11]
            desc_loop_length = status_byte & 0x0FFF

            # Descriptor'ları parse et
            title = ""
            description = ""
            genre = ""
            parental_rating = 0

            desc_offset = offset + 12
            desc_end = desc_offset + desc_loop_length

            while desc_offset < desc_end and desc_offset < len(data) - 2:
                desc_tag = data[desc_offset]
                desc_len = data[desc_offset + 1]

                if desc_tag == 0x4D:  # Short event descriptor
                    title, description = self._parse_short_event_desc(
                        data[desc_offset + 2:desc_offset + 2 + desc_len]
                    )
                elif desc_tag == 0x54:  # Content descriptor
                    genre = self._parse_content_desc(
                        data[desc_offset + 2:desc_offset + 2 + desc_len]
                    )
                elif desc_tag == 0x55:  # Parental rating descriptor
                    parental_rating = self._parse_parental_desc(
                        data[desc_offset + 2:desc_offset + 2 + desc_len]
                    )

                desc_offset += 2 + desc_len

            if title and start_time:
                events.append(EPGEvent(
                    channel_id=service_id,
                    event_id=event_id,
                    start_time=start_time,
                    duration=max(duration, 1),
                    title=title,
                    description=description,
                    genre=genre,
                    parental_rating=parental_rating,
                ))

            offset = desc_end

        return events

    def _parse_dvb_datetime(self, data: bytes) -> Optional[datetime]:
        """DVB MJD+UTC zaman formatını parse et."""
        if len(data) < 5:
            return None

        mjd = (data[0] << 8) | data[1]
        if mjd == 0xFFFF:
            return None

        # MJD → Gregoryen tarih dönüşümü
        y_prime = int((mjd - 15078.2) / 365.25)
        m_prime = int((mjd - 14956.1 - int(y_prime * 365.25)) / 30.6001)
        day = mjd - 14956 - int(y_prime * 365.25) - int(m_prime * 30.6001)

        k = 1 if (m_prime == 14 or m_prime == 15) else 0
        year = y_prime + k + 1900
        month = m_prime - 1 - k * 12

        hour = self._bcd_to_int(data[2])
        minute = self._bcd_to_int(data[3])
        second = self._bcd_to_int(data[4])

        try:
            return datetime(year, month, day, hour, minute, second)
        except ValueError:
            return None

    def _bcd_to_int(self, bcd: int) -> int:
        """BCD byte'ı integer'a çevir."""
        return ((bcd >> 4) * 10) + (bcd & 0x0F)

    def _parse_short_event_desc(self, data: bytes) -> tuple[str, str]:
        """Short event descriptor'ı parse et."""
        if len(data) < 4:
            return "", ""

        lang = data[0:3].decode("ascii", errors="ignore")
        name_len = data[3]
        name = ""
        desc = ""

        if name_len > 0 and 4 + name_len <= len(data):
            name_data = data[4:4 + name_len]
            name = self._decode_dvb_text(name_data)

        offset = 4 + name_len
        if offset < len(data):
            desc_len = data[offset]
            if desc_len > 0 and offset + 1 + desc_len <= len(data):
                desc_data = data[offset + 1:offset + 1 + desc_len]
                desc = self._decode_dvb_text(desc_data)

        return name, desc

    def _parse_content_desc(self, data: bytes) -> str:
        """Content descriptor'ı parse et (tür bilgisi)."""
        if len(data) < 2:
            return ""
        content_type = data[0]
        return DVB_CONTENT_TYPES.get(content_type, f"Diğer (0x{content_type:02X})")

    def _parse_parental_desc(self, data: bytes) -> int:
        """Parental rating descriptor'ı parse et."""
        if len(data) < 4:
            return 0
        # country_code = data[0:3]
        rating = data[3]
        return rating + 3 if rating > 0 else 0  # DVB: 0x01 = 4+, 0x0F = 18+

    def _decode_dvb_text(self, data: bytes) -> str:
        """DVB metin kodlamasını decode et."""
        if not data:
            return ""

        # İlk byte karakter tablosunu belirtir
        if data[0] < 0x20:
            charset_byte = data[0]
            text_data = data[1:]

            charset_map = {
                0x01: "iso-8859-5",   # Kiril
                0x02: "iso-8859-6",   # Arapça
                0x03: "iso-8859-7",   # Yunanca
                0x04: "iso-8859-8",   # İbranice
                0x05: "iso-8859-9",   # Türkçe (Latin-5)
                0x09: "iso-8859-13",
                0x10: "iso-8859-1",   # Varsayılan
                0x11: "utf-16be",
                0x15: "utf-8",
            }
            encoding = charset_map.get(charset_byte, "iso-8859-9")
        else:
            text_data = data
            encoding = "iso-8859-9"  # Türksat varsayılan

        try:
            return text_data.decode(encoding, errors="replace").strip()
        except (UnicodeDecodeError, LookupError):
            return text_data.decode("utf-8", errors="replace").strip()


class XMLTVParser:
    """XMLTV formatında EPG veri parser."""

    def parse_file(self, filepath: Path) -> list[EPGEvent]:
        """XMLTV dosyasını parse et."""
        import xml.etree.ElementTree as ET

        events = []
        tree = ET.parse(filepath)
        root = tree.getroot()

        for programme in root.findall("programme"):
            channel = programme.get("channel", "")
            start = programme.get("start", "")
            stop = programme.get("stop", "")

            title_elem = programme.find("title")
            desc_elem = programme.find("desc")
            category_elem = programme.find("category")

            title = title_elem.text if title_elem is not None else ""
            desc = desc_elem.text if desc_elem is not None else ""
            genre = category_elem.text if category_elem is not None else ""

            start_time = self._parse_xmltv_time(start)
            end_time = self._parse_xmltv_time(stop)

            if start_time and title:
                duration = 30  # varsayılan
                if end_time:
                    duration = int((end_time - start_time).total_seconds() / 60)

                events.append(EPGEvent(
                    channel_id=hash(channel) & 0xFFFF,
                    event_id=hash(f"{channel}{start}") & 0xFFFF,
                    start_time=start_time,
                    duration=max(duration, 1),
                    title=title,
                    description=desc,
                    genre=genre,
                ))

        return events

    def _parse_xmltv_time(self, time_str: str) -> Optional[datetime]:
        """XMLTV zaman formatını parse et (20230615180000 +0300)."""
        if not time_str:
            return None
        try:
            time_str = time_str.strip().split()[0]  # Timezone kısmını at
            return datetime.strptime(time_str[:14], "%Y%m%d%H%M%S")
        except ValueError:
            return None


class EPGManager:
    """EPG yönetim ana sınıfı."""

    def __init__(self, db: EPGDatabase = None):
        self.db = db or EPGDatabase()
        self.eit_parser = EITParser()
        self.xmltv_parser = XMLTVParser()

    def fetch_dvb_epg(self, adapter_num: int = 0, timeout: int = 30):
        """DVB-SI EIT tablolarından EPG topla."""
        print("📺 DVB-SI EPG verisi toplanıyor...")

        # dvbv5-tools ile EIT dump
        import subprocess
        try:
            result = subprocess.run(
                ["dvbv5-scan", "-a", str(adapter_num), "--input-format=CHANNEL",
                 "--output-format=VDR"],
                capture_output=True, timeout=timeout
            )
            # Parse edilecek veri...
            print(f"  ✅ DVB EPG verisi alındı ({len(result.stdout)} bytes)")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("  ⚠️  DVB EPG alınamadı (simülasyon verisi kullanılacak)")
            self._load_simulation_epg()

    def fetch_xmltv_epg(self, url: str):
        """XMLTV formatında internet EPG'si indir."""
        print(f"🌐 XMLTV EPG indiriliyor...")
        try:
            temp_path = SCRIPT_DIR / "temp_epg.xml"
            urllib.request.urlretrieve(url, temp_path)
            events = self.xmltv_parser.parse_file(temp_path)
            self.db.save_events(events)
            print(f"  ✅ {len(events)} program yüklendi")
        except Exception as e:
            print(f"  ❌ XMLTV indirme hatası: {e}")

    def get_now_next(self, channel_id: int) -> dict:
        """Kanalın şimdiki ve sonraki programını getir."""
        events = self.db.get_schedule(channel_id)
        now = datetime.now()

        current = None
        next_prog = None

        for event in events:
            start = datetime.fromisoformat(event["start_time"])
            end = start + timedelta(minutes=event["duration"])
            if start <= now < end:
                current = event
            elif start > now and next_prog is None:
                next_prog = event
                break

        return {"current": current, "next": next_prog}

    def _load_simulation_epg(self):
        """Simülasyon EPG verisi (test için)."""
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        sim_events = [
            # TRT 1
            EPGEvent(1001, 1, now - timedelta(hours=1), 120, "Ana Haber Bülteni", "Günün önemli haberleri", "Haber"),
            EPGEvent(1001, 2, now + timedelta(hours=1), 90, "Gönül Dağı", "Türk dizisi", "Film"),
            EPGEvent(1001, 3, now + timedelta(hours=2, minutes=30), 60, "Spor Bülteni", "Günün spor haberleri", "Spor"),
            # Kanal D
            EPGEvent(7001, 10, now - timedelta(minutes=30), 120, "Kara Sevda", "Türk dizisi", "Film"),
            EPGEvent(7001, 11, now + timedelta(hours=1, minutes=30), 90, "Ana Haber", "Gündem", "Haber"),
            # ATV
            EPGEvent(4001, 20, now, 120, "Kuruluş Osman", "Tarihî dizi", "Film"),
            EPGEvent(4001, 21, now + timedelta(hours=2), 60, "ATV Ana Haber", "Haberler", "Haber"),
        ]
        self.db.save_events(sim_events)
        print(f"  📋 {len(sim_events)} simülasyon EPG kaydı yüklendi")


if __name__ == "__main__":
    print("=" * 50)
    print("  APEXSAT AI - EPG Motoru Testi")
    print("=" * 50)

    manager = EPGManager()
    manager.fetch_dvb_epg()

    # Şimdiki programlar
    print("\n📺 Şimdiki Programlar:")
    for event in manager.db.get_current_events():
        print(f"  CH{event['channel_id']}: {event['title']} ({event['genre']}) "
              f"- {event['start_time'][:16]}")

    # TRT 1 program akışı
    print("\n📋 TRT 1 Program Akışı:")
    for event in manager.db.get_schedule(1001):
        print(f"  {event['start_time'][11:16]} - {event['title']} ({event['duration']}dk)")

    print("\n✅ EPG test tamamlandı")
