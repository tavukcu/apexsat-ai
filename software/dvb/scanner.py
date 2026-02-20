#!/usr/bin/env python3
"""
APEXSAT AI - DVB-S2 Transponder Tarama Motoru
Türksat 42°E odaklı, tüm Ku-Band uydularla uyumlu.

Kullanım:
    python3 scanner.py --scan turksat       # Türksat hızlı tarama (bilinen transponderlar)
    python3 scanner.py --blind-scan         # Blind scan (tüm frekans aralığı)
    python3 scanner.py --nit-scan           # NIT tabanlı otomatik tarama
    python3 scanner.py --adapter 0          # DVB adaptör seçimi
    python3 scanner.py --list-channels      # Bulunan kanalları listele
    python3 scanner.py --export m3u         # M3U playlist olarak dışa aktar

Gereksinimler:
    - Linux DVB subsystem (dvb-core, dvb-frontend)
    - dvbv5-tools (dvb-fe-tool, dvbv5-scan, dvbv5-zap)
    - Python 3.11+
"""

import json
import os
import subprocess
import sys
import time
import argparse
import sqlite3
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Optional


# ─── Sabitler ────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).parent
TRANSPONDER_DB = SCRIPT_DIR / "turksat_transponders.json"
CHANNEL_DB = SCRIPT_DIR / "channels.db"
DVB_ADAPTER_PATH = "/dev/dvb"

# Ku-Band LNB parametreleri
LNB_UNIVERSAL = {
    "low_freq": 9750,     # MHz - düşük band LO
    "high_freq": 10600,   # MHz - yüksek band LO
    "switch_freq": 11700, # MHz - band geçiş frekansı
}

# Blind scan frekans aralığı (Ku-Band)
BLIND_SCAN_RANGE = {
    "start": 10700,  # MHz
    "end": 12750,    # MHz
    "step": 2,       # MHz adım
}

# Desteklenen symbol rate'ler
COMMON_SYMBOL_RATES = [2400, 3125, 5000, 6000, 13000, 22000, 27500, 30000, 45000]


# ─── Veri Yapıları ───────────────────────────────────────────────────────────

class DVBSystem(Enum):
    DVB_S = "DVB-S"
    DVB_S2 = "DVB-S2"
    DVB_S2X = "DVB-S2X"


class Polarization(Enum):
    HORIZONTAL = "H"
    VERTICAL = "V"
    CIRCULAR_LEFT = "L"
    CIRCULAR_RIGHT = "R"


class Modulation(Enum):
    QPSK = "QPSK"
    PSK_8 = "8PSK"
    APSK_16 = "16APSK"
    APSK_32 = "32APSK"


@dataclass
class Transponder:
    frequency: int          # MHz
    polarization: str       # H, V, L, R
    symbol_rate: int        # ksps
    fec: str               # 1/2, 2/3, 3/4, 5/6, 7/8
    system: str            # DVB-S, DVB-S2
    modulation: str        # QPSK, 8PSK
    note: str = ""

    @property
    def if_frequency(self) -> int:
        """LNB sonrası IF frekansını hesapla."""
        if self.frequency >= LNB_UNIVERSAL["switch_freq"]:
            return self.frequency - LNB_UNIVERSAL["high_freq"]
        return self.frequency - LNB_UNIVERSAL["low_freq"]

    @property
    def is_high_band(self) -> bool:
        return self.frequency >= LNB_UNIVERSAL["switch_freq"]

    @property
    def voltage(self) -> int:
        """LNB polarizasyon voltajı (13V=V, 18V=H)."""
        return 18 if self.polarization == "H" else 13

    @property
    def tone(self) -> bool:
        """22kHz tone (high band için aktif)."""
        return self.is_high_band

    def to_dvbv5_format(self) -> str:
        """dvbv5-scan uyumlu transponder satırı."""
        lines = [
            f"[Turksat_{self.frequency}{self.polarization}]",
            f"\tDELIVERY_SYSTEM = {self.system.replace('-', '')}",
            f"\tFREQUENCY = {self.if_frequency * 1000}",  # kHz cinsinden
            f"\tSYMBOL_RATE = {self.symbol_rate * 1000}",  # sps cinsinden
            f"\tPOLARIZATION = {'HORIZONTAL' if self.polarization == 'H' else 'VERTICAL'}",
            f"\tINNER_FEC = FEC_{self.fec.replace('/', '_')}",
            f"\tMODULATION = {self.modulation}",
        ]
        return "\n".join(lines)


@dataclass
class Channel:
    name: str
    service_id: int
    transponder_freq: int
    transponder_pol: str
    video_pid: int = 0
    audio_pid: int = 0
    pcr_pid: int = 0
    pmt_pid: int = 0
    channel_type: str = "TV"  # TV, Radio, Data
    is_free: bool = True
    is_hd: bool = False
    provider: str = ""
    category: str = ""


@dataclass
class ScanResult:
    transponders_scanned: int = 0
    transponders_locked: int = 0
    channels_found: int = 0
    tv_channels: int = 0
    radio_channels: int = 0
    data_services: int = 0
    scan_duration: float = 0.0
    channels: list = field(default_factory=list)


# ─── DVB Donanım Kontrol ────────────────────────────────────────────────────

class DVBAdapter:
    """Linux DVB adaptör yöneticisi."""

    def __init__(self, adapter_num: int = 0, frontend_num: int = 0):
        self.adapter_num = adapter_num
        self.frontend_num = frontend_num
        self.adapter_path = f"{DVB_ADAPTER_PATH}/adapter{adapter_num}"
        self.frontend_path = f"{self.adapter_path}/frontend{frontend_num}"
        self.demux_path = f"{self.adapter_path}/demux{frontend_num}"
        self.dvr_path = f"{self.adapter_path}/dvr{frontend_num}"

    def exists(self) -> bool:
        return os.path.exists(self.frontend_path)

    def get_info(self) -> dict:
        """Frontend bilgilerini al."""
        try:
            result = subprocess.run(
                ["dvb-fe-tool", "-a", str(self.adapter_num)],
                capture_output=True, text=True, timeout=5
            )
            info = {"raw": result.stdout}
            for line in result.stdout.splitlines():
                if ":" in line:
                    key, _, value = line.partition(":")
                    info[key.strip()] = value.strip()
            return info
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"error": str(e)}

    def get_signal_stats(self) -> dict:
        """Sinyal istatistiklerini al (SNR, BER, sinyal gücü)."""
        try:
            result = subprocess.run(
                ["dvb-fe-tool", "-a", str(self.adapter_num), "-m"],
                capture_output=True, text=True, timeout=5
            )
            stats = {}
            for line in result.stdout.splitlines():
                if "Signal" in line:
                    stats["signal_strength"] = line.split(":")[-1].strip()
                elif "SNR" in line or "C/N" in line:
                    stats["snr"] = line.split(":")[-1].strip()
                elif "BER" in line:
                    stats["ber"] = line.split(":")[-1].strip()
                elif "Lock" in line or "lock" in line:
                    stats["locked"] = "Yes" in line or "1" in line
            return stats
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"error": str(e)}


# ─── Kanal Veritabanı ────────────────────────────────────────────────────────

class ChannelDatabase:
    """SQLite tabanlı kanal veritabanı."""

    def __init__(self, db_path: Path = CHANNEL_DB):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    service_id INTEGER,
                    transponder_freq INTEGER,
                    transponder_pol TEXT,
                    video_pid INTEGER DEFAULT 0,
                    audio_pid INTEGER DEFAULT 0,
                    pcr_pid INTEGER DEFAULT 0,
                    pmt_pid INTEGER DEFAULT 0,
                    channel_type TEXT DEFAULT 'TV',
                    is_free INTEGER DEFAULT 1,
                    is_hd INTEGER DEFAULT 0,
                    provider TEXT DEFAULT '',
                    category TEXT DEFAULT '',
                    position INTEGER DEFAULT 0,
                    favorite INTEGER DEFAULT 0,
                    locked INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS transponders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    frequency INTEGER NOT NULL,
                    polarization TEXT NOT NULL,
                    symbol_rate INTEGER,
                    fec TEXT,
                    system TEXT,
                    modulation TEXT,
                    signal_quality REAL DEFAULT 0,
                    last_scanned TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(frequency, polarization)
                );

                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    list_name TEXT NOT NULL DEFAULT 'Favoriler',
                    channel_id INTEGER,
                    position INTEGER,
                    FOREIGN KEY (channel_id) REFERENCES channels(id)
                );

                CREATE INDEX IF NOT EXISTS idx_channels_name ON channels(name);
                CREATE INDEX IF NOT EXISTS idx_channels_type ON channels(channel_type);
                CREATE INDEX IF NOT EXISTS idx_channels_freq ON channels(transponder_freq);
            """)

    def save_channels(self, channels: list[Channel]):
        with sqlite3.connect(self.db_path) as conn:
            for ch in channels:
                conn.execute("""
                    INSERT OR REPLACE INTO channels
                    (name, service_id, transponder_freq, transponder_pol,
                     video_pid, audio_pid, pcr_pid, pmt_pid,
                     channel_type, is_free, is_hd, provider, category)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ch.name, ch.service_id, ch.transponder_freq, ch.transponder_pol,
                    ch.video_pid, ch.audio_pid, ch.pcr_pid, ch.pmt_pid,
                    ch.channel_type, ch.is_free, ch.is_hd, ch.provider, ch.category
                ))

    def save_transponder(self, tp: Transponder, signal_quality: float = 0):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO transponders
                (frequency, polarization, symbol_rate, fec, system, modulation, signal_quality)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tp.frequency, tp.polarization, tp.symbol_rate, tp.fec,
                  tp.system, tp.modulation, signal_quality))

    def get_all_channels(self, channel_type: Optional[str] = None) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if channel_type:
                rows = conn.execute(
                    "SELECT * FROM channels WHERE channel_type = ? ORDER BY position, name",
                    (channel_type,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM channels ORDER BY position, name"
                ).fetchall()
            return [dict(row) for row in rows]

    def search_channels(self, query: str) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM channels WHERE name LIKE ? ORDER BY name",
                (f"%{query}%",)
            ).fetchall()
            return [dict(row) for row in rows]

    def get_channel_count(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM channels").fetchone()[0]
            tv = conn.execute("SELECT COUNT(*) FROM channels WHERE channel_type='TV'").fetchone()[0]
            radio = conn.execute("SELECT COUNT(*) FROM channels WHERE channel_type='Radio'").fetchone()[0]
            hd = conn.execute("SELECT COUNT(*) FROM channels WHERE is_hd=1").fetchone()[0]
            fta = conn.execute("SELECT COUNT(*) FROM channels WHERE is_free=1").fetchone()[0]
            return {"total": total, "tv": tv, "radio": radio, "hd": hd, "fta": fta}


# ─── Tarama Motoru ───────────────────────────────────────────────────────────

class DVBScanner:
    """DVB-S/S2 transponder tarama motoru."""

    def __init__(self, adapter: DVBAdapter, db: ChannelDatabase):
        self.adapter = adapter
        self.db = db
        self.scan_result = ScanResult()

    def load_transponders(self, json_path: Path = TRANSPONDER_DB) -> list[Transponder]:
        """Transponder listesini JSON'dan yükle."""
        with open(json_path) as f:
            data = json.load(f)

        transponders = []
        for tp in data["transponders"]:
            transponders.append(Transponder(
                frequency=tp["freq"],
                polarization=tp["pol"],
                symbol_rate=tp["sr"],
                fec=tp["fec"],
                system=tp["system"],
                modulation=tp["modulation"],
                note=tp.get("note", "")
            ))
        return transponders

    def generate_dvbv5_scan_file(self, transponders: list[Transponder], output_path: Path) -> Path:
        """dvbv5-scan için tarama dosyası oluştur."""
        lines = [
            "# APEXSAT AI - Türksat 42°E Transponder Listesi",
            f"# Otomatik oluşturuldu: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"# Toplam transponder: {len(transponders)}",
            ""
        ]
        for tp in transponders:
            lines.append(tp.to_dvbv5_format())
            lines.append("")

        output_path.write_text("\n".join(lines))
        return output_path

    def scan_transponder(self, tp: Transponder, timeout: int = 10) -> list[Channel]:
        """Tek bir transponder'ı tara ve kanalları bul."""
        channels = []

        print(f"  📡 Taranıyor: {tp.frequency} MHz {tp.polarization} "
              f"SR:{tp.symbol_rate} {tp.system} {tp.modulation}")

        # dvbv5-zap ile transponder'a kilitlenme denemesi
        zap_cmd = [
            "dvbv5-zap",
            "-a", str(self.adapter.adapter_num),
            "-c", "/dev/null",
            "-S", str(timeout),
            "-r",  # record mode (lock only)
            "--lnbf=UNIVERSAL",
        ]

        # Transponder parametreleri
        tune_cmd = [
            "dvb-fe-tool",
            "-a", str(self.adapter.adapter_num),
            "--set-delsys", tp.system.replace("-", ""),
            "--freq", str(tp.if_frequency * 1000),  # kHz
            "--sr", str(tp.symbol_rate * 1000),
            "--fec", tp.fec.replace("/", ""),
            "--modulation", tp.modulation,
            "--voltage", str(tp.voltage),
        ]
        if tp.tone:
            tune_cmd.append("--tone=on")

        try:
            # Transponder'a kilitle
            result = subprocess.run(
                tune_cmd,
                capture_output=True, text=True, timeout=timeout + 5
            )

            # Sinyal kontrolü
            time.sleep(2)
            stats = self.adapter.get_signal_stats()

            if stats.get("locked"):
                self.scan_result.transponders_locked += 1
                print(f"    ✅ Kilitlendi! SNR: {stats.get('snr', 'N/A')}")

                # PAT/PMT taraması ile kanal keşfi
                found = self._parse_pat_pmt(tp)
                channels.extend(found)
                self.db.save_transponder(tp, float(stats.get("snr", "0").replace("dB", "")))
            else:
                print(f"    ❌ Kilitlenemedi")

        except subprocess.TimeoutExpired:
            print(f"    ⏰ Zaman aşımı")
        except FileNotFoundError:
            print(f"    ⚠️  dvb-fe-tool bulunamadı (simülasyon modunda)")
            # Simülasyon: gerçek donanım olmadan test için
            channels = self._simulate_channels(tp)

        self.scan_result.transponders_scanned += 1
        return channels

    def _parse_pat_pmt(self, tp: Transponder) -> list[Channel]:
        """PAT/PMT tablolarını parse ederek kanalları bul."""
        channels = []

        try:
            # dvbv5-scan ile otomatik kanal keşfi
            scan_file = SCRIPT_DIR / "temp_scan.conf"
            self.generate_dvbv5_scan_file([tp], scan_file)

            result = subprocess.run(
                [
                    "dvbv5-scan",
                    "-a", str(self.adapter.adapter_num),
                    "-o", str(SCRIPT_DIR / "temp_channels.conf"),
                    str(scan_file),
                ],
                capture_output=True, text=True, timeout=30
            )

            # Çıktıyı parse et
            for line in result.stdout.splitlines():
                if "Service" in line and ":" in line:
                    parts = line.split(":")
                    if len(parts) >= 2:
                        ch = Channel(
                            name=parts[1].strip(),
                            service_id=0,
                            transponder_freq=tp.frequency,
                            transponder_pol=tp.polarization,
                        )
                        channels.append(ch)

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return channels

    def _simulate_channels(self, tp: Transponder) -> list[Channel]:
        """Simülasyon modu - donanım olmadan test için örnek kanallar."""
        simulated = {
            10970: [
                Channel("TRT 1", 1001, tp.frequency, tp.polarization, 101, 201, 101, 1001, "TV", True, False, "TRT"),
                Channel("TRT 2", 1002, tp.frequency, tp.polarization, 102, 202, 102, 1002, "TV", True, False, "TRT"),
                Channel("TRT Haber", 1003, tp.frequency, tp.polarization, 103, 203, 103, 1003, "TV", True, False, "TRT"),
                Channel("TRT Spor", 1004, tp.frequency, tp.polarization, 104, 204, 104, 1004, "TV", True, False, "TRT"),
            ],
            11012: [
                Channel("TRT 1 HD", 2001, tp.frequency, tp.polarization, 201, 301, 201, 2001, "TV", True, True, "TRT"),
                Channel("TRT World HD", 2002, tp.frequency, tp.polarization, 202, 302, 202, 2002, "TV", True, True, "TRT"),
                Channel("TRT Belgesel HD", 2003, tp.frequency, tp.polarization, 203, 303, 203, 2003, "TV", True, True, "TRT"),
            ],
            11054: [
                Channel("TRT 4K", 3001, tp.frequency, tp.polarization, 301, 401, 301, 3001, "TV", True, True, "TRT"),
                Channel("TRT Radyo 1", 3002, tp.frequency, tp.polarization, 0, 402, 0, 3002, "Radio", True, False, "TRT"),
                Channel("TRT FM", 3003, tp.frequency, tp.polarization, 0, 403, 0, 3003, "Radio", True, False, "TRT"),
                Channel("TRT Nağme", 3004, tp.frequency, tp.polarization, 0, 404, 0, 3004, "Radio", True, False, "TRT"),
            ],
            11762: [
                Channel("ATV", 4001, tp.frequency, tp.polarization, 501, 601, 501, 4001, "TV", True, False, "Turkuvaz"),
                Channel("A Haber", 4002, tp.frequency, tp.polarization, 502, 602, 502, 4002, "TV", True, False, "Turkuvaz"),
                Channel("ATV Avrupa", 4003, tp.frequency, tp.polarization, 503, 603, 503, 4003, "TV", True, False, "Turkuvaz"),
                Channel("A Spor", 4004, tp.frequency, tp.polarization, 504, 604, 504, 4004, "TV", True, False, "Turkuvaz"),
                Channel("A Para", 4005, tp.frequency, tp.polarization, 505, 605, 505, 4005, "TV", True, False, "Turkuvaz"),
            ],
            11804: [
                Channel("Show TV", 5001, tp.frequency, tp.polarization, 601, 701, 601, 5001, "TV", True, False, "Ciner"),
                Channel("Habertürk TV", 5002, tp.frequency, tp.polarization, 602, 702, 602, 5002, "TV", True, False, "Ciner"),
                Channel("Bloomberg HT", 5003, tp.frequency, tp.polarization, 603, 703, 603, 5003, "TV", True, False, "Ciner"),
                Channel("Show Türk", 5004, tp.frequency, tp.polarization, 604, 704, 604, 5004, "TV", True, False, "Ciner"),
            ],
            11838: [
                Channel("Star TV", 6001, tp.frequency, tp.polarization, 701, 801, 701, 6001, "TV", True, False, "Star"),
                Channel("NTV", 6002, tp.frequency, tp.polarization, 702, 802, 702, 6002, "TV", True, False, "Doğuş"),
                Channel("Star TV HD", 6003, tp.frequency, tp.polarization, 703, 803, 703, 6003, "TV", True, True, "Star"),
                Channel("NTV Spor", 6004, tp.frequency, tp.polarization, 704, 804, 704, 6004, "TV", True, False, "Doğuş"),
            ],
            11880: [
                Channel("Kanal D", 7001, tp.frequency, tp.polarization, 801, 901, 801, 7001, "TV", True, False, "Demirören"),
                Channel("CNN Türk", 7002, tp.frequency, tp.polarization, 802, 902, 802, 7002, "TV", True, False, "Demirören"),
                Channel("Kanal D HD", 7003, tp.frequency, tp.polarization, 803, 903, 803, 7003, "TV", True, True, "Demirören"),
                Channel("Dream TV", 7004, tp.frequency, tp.polarization, 804, 904, 804, 7004, "TV", True, False, "Demirören"),
            ],
            11919: [
                Channel("Fox TV", 8001, tp.frequency, tp.polarization, 901, 1001, 901, 8001, "TV", True, False, "Fox"),
                Channel("TV8", 8002, tp.frequency, tp.polarization, 902, 1002, 902, 8002, "TV", True, False, "TV8"),
                Channel("Fox TV HD", 8003, tp.frequency, tp.polarization, 903, 1003, 903, 8003, "TV", True, True, "Fox"),
                Channel("TV8.5", 8004, tp.frequency, tp.polarization, 904, 1004, 904, 8004, "TV", True, False, "TV8"),
            ],
            11957: [
                Channel("Beyaz TV", 9001, tp.frequency, tp.polarization, 1101, 1201, 1101, 9001, "TV", True, False, "Beyaz"),
                Channel("TV360", 9002, tp.frequency, tp.polarization, 1102, 1202, 1102, 9002, "TV", True, False, "TV360"),
                Channel("TGRT Haber", 9003, tp.frequency, tp.polarization, 1103, 1203, 1103, 9003, "TV", True, False, "İhlas"),
                Channel("Halk TV", 9004, tp.frequency, tp.polarization, 1104, 1204, 1104, 9004, "TV", True, False, "Halk"),
                Channel("Tele1", 9005, tp.frequency, tp.polarization, 1105, 1205, 1105, 9005, "TV", True, False, "Tele1"),
            ],
        }

        return simulated.get(tp.frequency, [
            Channel(f"Servis_{tp.frequency}_{tp.polarization}_1", 9900, tp.frequency, tp.polarization),
            Channel(f"Servis_{tp.frequency}_{tp.polarization}_2", 9901, tp.frequency, tp.polarization),
        ])

    def scan_turksat(self, progress_callback=None) -> ScanResult:
        """Türksat 42°E bilinen transponder taraması."""
        print("=" * 60)
        print("  APEXSAT AI - Türksat 42°E Kanal Tarama")
        print("=" * 60)

        transponders = self.load_transponders()
        total = len(transponders)
        start_time = time.time()
        all_channels = []

        print(f"\n📋 Toplam {total} transponder taranacak\n")

        for i, tp in enumerate(transponders, 1):
            if progress_callback:
                progress_callback(i, total, tp)

            pct = (i / total) * 100
            print(f"\n[{i}/{total}] ({pct:.0f}%) ───────────────────────────")

            channels = self.scan_transponder(tp)
            all_channels.extend(channels)

            for ch in channels:
                if ch.channel_type == "TV":
                    self.scan_result.tv_channels += 1
                elif ch.channel_type == "Radio":
                    self.scan_result.radio_channels += 1
                else:
                    self.scan_result.data_services += 1

            print(f"    Bulunan: {len(channels)} kanal")

        self.scan_result.channels = all_channels
        self.scan_result.channels_found = len(all_channels)
        self.scan_result.scan_duration = time.time() - start_time

        # Veritabanına kaydet
        self.db.save_channels(all_channels)

        self._print_scan_summary()
        return self.scan_result

    def blind_scan(self, pol: str = "both") -> ScanResult:
        """Blind scan - tüm Ku-Band frekans aralığını tara."""
        print("=" * 60)
        print("  APEXSAT AI - Blind Scan (Ku-Band)")
        print("=" * 60)

        start_freq = BLIND_SCAN_RANGE["start"]
        end_freq = BLIND_SCAN_RANGE["end"]
        step = BLIND_SCAN_RANGE["step"]
        polarizations = ["H", "V"] if pol == "both" else [pol.upper()]

        start_time = time.time()
        all_channels = []
        total_steps = ((end_freq - start_freq) // step) * len(polarizations)
        current = 0

        print(f"\n🔍 Frekans aralığı: {start_freq}-{end_freq} MHz")
        print(f"📊 Adım: {step} MHz, Polarizasyon: {', '.join(polarizations)}")
        print(f"📋 Toplam adım: {total_steps}\n")

        for freq in range(start_freq, end_freq + 1, step):
            for p in polarizations:
                current += 1
                # Her symbol rate'i dene
                for sr in COMMON_SYMBOL_RATES:
                    for system in ["DVB-S", "DVB-S2"]:
                        mod = "QPSK" if system == "DVB-S" else "8PSK"
                        tp = Transponder(freq, p, sr, "AUTO", system, mod)

                        if current % 50 == 0:
                            pct = (current / total_steps) * 100
                            print(f"[{current}/{total_steps}] ({pct:.0f}%) {freq} MHz {p}")

                        channels = self.scan_transponder(tp, timeout=5)
                        if channels:
                            all_channels.extend(channels)
                            break  # Bu frekansta kanal bulundu, diğer sr'leri atla
                    if channels:
                        break

        self.scan_result.channels = all_channels
        self.scan_result.channels_found = len(all_channels)
        self.scan_result.scan_duration = time.time() - start_time

        self.db.save_channels(all_channels)
        self._print_scan_summary()
        return self.scan_result

    def nit_scan(self) -> ScanResult:
        """NIT (Network Information Table) tabanlı tarama."""
        print("=" * 60)
        print("  APEXSAT AI - NIT Tabanlı Otomatik Tarama")
        print("=" * 60)

        # İlk transponder'a kilitle ve NIT'i oku
        transponders = self.load_transponders()
        if not transponders:
            print("❌ Transponder listesi boş!")
            return self.scan_result

        home_tp = transponders[0]
        print(f"\n📡 Ana transponder: {home_tp.frequency} MHz {home_tp.polarization}")
        print("🔍 NIT tablosu okunuyor...\n")

        # dvbv5-scan NIT modunda
        try:
            scan_file = SCRIPT_DIR / "nit_scan.conf"
            self.generate_dvbv5_scan_file([home_tp], scan_file)

            result = subprocess.run(
                [
                    "dvbv5-scan",
                    "-a", str(self.adapter.adapter_num),
                    "-N",  # NIT tabanlı tarama
                    str(scan_file),
                ],
                capture_output=True, text=True, timeout=120
            )
            print(result.stdout)

        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("⚠️  NIT taraması başarısız, standart taramaya geçiliyor...")
            return self.scan_turksat()

        return self.scan_result

    def _print_scan_summary(self):
        """Tarama sonuç özetini yazdır."""
        r = self.scan_result
        print("\n" + "=" * 60)
        print("  TARAMA SONUÇLARI")
        print("=" * 60)
        print(f"  ⏱️  Süre: {r.scan_duration:.1f} saniye")
        print(f"  📡 Taranan transponder: {r.transponders_scanned}")
        print(f"  🔒 Kilitlenen: {r.transponders_locked}")
        print(f"  📺 TV kanalları: {r.tv_channels}")
        print(f"  📻 Radyo kanalları: {r.radio_channels}")
        print(f"  📊 Veri servisleri: {r.data_services}")
        print(f"  ─────────────────────────────")
        print(f"  📋 TOPLAM: {r.channels_found} kanal")
        print("=" * 60)


# ─── Dışa Aktarma ───────────────────────────────────────────────────────────

class ChannelExporter:
    """Kanal listesi dışa aktarma."""

    def __init__(self, db: ChannelDatabase):
        self.db = db

    def export_m3u(self, output_path: Path, channel_type: Optional[str] = None) -> Path:
        """M3U/M3U8 playlist formatında dışa aktar."""
        channels = self.db.get_all_channels(channel_type)

        lines = [
            "#EXTM3U",
            f"# APEXSAT AI - Türksat 42°E Kanal Listesi",
            f"# Oluşturulma: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"# Toplam: {len(channels)} kanal",
            "",
        ]

        for ch in channels:
            group = ch.get("category") or ch.get("provider") or "Genel"
            ch_type = "TV" if ch["channel_type"] == "TV" else "Radio"
            hd = " HD" if ch.get("is_hd") else ""

            lines.append(
                f'#EXTINF:-1 tvg-name="{ch["name"]}" '
                f'tvg-type="{ch_type}" '
                f'group-title="{group}",{ch["name"]}{hd}'
            )
            # DVB URL formatı
            freq = ch["transponder_freq"]
            pol = ch["transponder_pol"]
            sid = ch.get("service_id", 0)
            lines.append(f"dvb://frequency={freq}&polarization={pol}&service_id={sid}")
            lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"✅ M3U dışa aktarıldı: {output_path} ({len(channels)} kanal)")
        return output_path

    def export_enigma2(self, output_path: Path) -> Path:
        """Enigma2 (Dreambox/VU+) bouquet formatında dışa aktar."""
        channels = self.db.get_all_channels("TV")

        lines = ["#NAME APEXSAT Türksat"]
        for ch in channels:
            # Enigma2 servis referans formatı
            sid = ch.get("service_id", 0)
            lines.append(f"#SERVICE 1:0:1:{sid:X}:0:0:0:0:0:0:")
            lines.append(f"#DESCRIPTION {ch['name']}")

        output_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"✅ Enigma2 bouquet dışa aktarıldı: {output_path}")
        return output_path

    def export_csv(self, output_path: Path) -> Path:
        """CSV formatında dışa aktar."""
        channels = self.db.get_all_channels()

        lines = ["Kanal Adı,Tür,HD,FTA,Frekans,Pol,Video PID,Audio PID,Servis ID,Sağlayıcı"]
        for ch in channels:
            lines.append(
                f'"{ch["name"]}",{ch["channel_type"]},'
                f'{"Evet" if ch.get("is_hd") else "Hayır"},'
                f'{"Evet" if ch.get("is_free") else "Hayır"},'
                f'{ch["transponder_freq"]},{ch["transponder_pol"]},'
                f'{ch.get("video_pid", 0)},{ch.get("audio_pid", 0)},'
                f'{ch.get("service_id", 0)},"{ch.get("provider", "")}"'
            )

        output_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"✅ CSV dışa aktarıldı: {output_path} ({len(channels) - 1} kanal)")
        return output_path

    def export_xmltv(self, output_path: Path) -> Path:
        """XMLTV formatında kanal listesi (EPG için temel)."""
        channels = self.db.get_all_channels("TV")

        root = ET.Element("tv", {
            "source-info-name": "APEXSAT AI",
            "generator-info-name": "APEXSAT DVB Scanner"
        })

        for ch in channels:
            ch_elem = ET.SubElement(root, "channel", {"id": str(ch.get("service_id", 0))})
            name_elem = ET.SubElement(ch_elem, "display-name", {"lang": "tr"})
            name_elem.text = ch["name"]

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(output_path, encoding="unicode", xml_declaration=True)
        print(f"✅ XMLTV dışa aktarıldı: {output_path}")
        return output_path


# ─── Ana Program ─────────────────────────────────────────────────────────────

def check_dvb_tools():
    """DVB araçlarının yüklü olup olmadığını kontrol et."""
    tools = ["dvb-fe-tool", "dvbv5-scan", "dvbv5-zap"]
    missing = []
    for tool in tools:
        try:
            subprocess.run([tool, "--version"], capture_output=True, timeout=3)
        except FileNotFoundError:
            missing.append(tool)
        except subprocess.TimeoutExpired:
            pass  # Çalışıyor ama yanıt vermedi - sorun yok

    if missing:
        print("⚠️  Eksik DVB araçları:", ", ".join(missing))
        print("   Yüklemek için: sudo apt install dvb-tools dvbv5-tools")
        print("   Simülasyon modunda devam ediliyor...\n")
        return False
    return True


def check_dvb_adapter(adapter_num: int = 0) -> bool:
    """DVB adaptörünün bağlı olup olmadığını kontrol et."""
    adapter = DVBAdapter(adapter_num)
    if not adapter.exists():
        print(f"⚠️  DVB adaptör bulunamadı: {adapter.frontend_path}")
        print("   USB DVB-S2 tuner bağlayın veya simülasyon modunda devam edin.\n")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description="APEXSAT AI - DVB-S2 Transponder Tarama Motoru",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  %(prog)s --scan turksat              Türksat 42°E hızlı tarama
  %(prog)s --blind-scan                Blind scan (tüm Ku-Band)
  %(prog)s --blind-scan --pol H        Sadece Horizontal blind scan
  %(prog)s --nit-scan                  NIT tabanlı otomatik tarama
  %(prog)s --list-channels             Bulunan kanalları listele
  %(prog)s --list-channels --type TV   Sadece TV kanalları
  %(prog)s --search "TRT"              Kanal ara
  %(prog)s --export m3u                M3U playlist dışa aktar
  %(prog)s --export csv                CSV olarak dışa aktar
  %(prog)s --export enigma2            Enigma2 bouquet dışa aktar
  %(prog)s --stats                     Kanal istatistikleri
        """
    )

    parser.add_argument("--scan", choices=["turksat", "all"], help="Tarama modu")
    parser.add_argument("--blind-scan", action="store_true", help="Blind scan başlat")
    parser.add_argument("--nit-scan", action="store_true", help="NIT tabanlı tarama")
    parser.add_argument("--adapter", type=int, default=0, help="DVB adaptör numarası")
    parser.add_argument("--pol", choices=["H", "V", "both"], default="both", help="Polarizasyon filtresi")
    parser.add_argument("--list-channels", action="store_true", help="Kanal listesini göster")
    parser.add_argument("--type", choices=["TV", "Radio", "Data"], help="Kanal türü filtresi")
    parser.add_argument("--search", type=str, help="Kanal adı ara")
    parser.add_argument("--export", choices=["m3u", "csv", "enigma2", "xmltv"], help="Dışa aktarma formatı")
    parser.add_argument("--output", type=str, help="Dışa aktarma dosya yolu")
    parser.add_argument("--stats", action="store_true", help="Kanal istatistikleri")
    parser.add_argument("--simulate", action="store_true", help="Simülasyon modu (donanım olmadan test)")

    args = parser.parse_args()

    # Varsayılan: --scan turksat
    if not any([args.scan, args.blind_scan, args.nit_scan,
                args.list_channels, args.search, args.export, args.stats]):
        args.scan = "turksat"

    db = ChannelDatabase()

    # Tarama komutları
    if args.scan or args.blind_scan or args.nit_scan:
        has_tools = check_dvb_tools()
        has_adapter = check_dvb_adapter(args.adapter)

        adapter = DVBAdapter(args.adapter)
        scanner = DVBScanner(adapter, db)

        if not has_tools or not has_adapter:
            print("🔄 Simülasyon modunda çalışıyor...\n")

        if args.scan == "turksat" or args.scan == "all":
            result = scanner.scan_turksat()
        elif args.blind_scan:
            result = scanner.blind_scan(args.pol)
        elif args.nit_scan:
            result = scanner.nit_scan()

    # Listeleme
    elif args.list_channels:
        channels = db.get_all_channels(args.type)
        if not channels:
            print("📋 Kayıtlı kanal bulunamadı. Önce tarama yapın: --scan turksat")
            return

        print(f"\n{'Kanal Adı':<30} {'Tür':<8} {'HD':<5} {'Frekans':<10} {'Pol':<5} {'Sağlayıcı':<15}")
        print("─" * 80)
        for ch in channels:
            hd = "HD" if ch.get("is_hd") else ""
            print(f"{ch['name']:<30} {ch['channel_type']:<8} {hd:<5} "
                  f"{ch['transponder_freq']:<10} {ch['transponder_pol']:<5} "
                  f"{ch.get('provider', ''):<15}")
        print(f"\nToplam: {len(channels)} kanal")

    # Arama
    elif args.search:
        channels = db.search_channels(args.search)
        if not channels:
            print(f"🔍 '{args.search}' için sonuç bulunamadı.")
            return

        print(f"\n🔍 '{args.search}' araması: {len(channels)} sonuç\n")
        for ch in channels:
            hd = " [HD]" if ch.get("is_hd") else ""
            print(f"  📺 {ch['name']}{hd} - {ch['transponder_freq']} MHz {ch['transponder_pol']}")

    # Dışa aktarma
    elif args.export:
        exporter = ChannelExporter(db)
        output_dir = SCRIPT_DIR / "exports"
        output_dir.mkdir(exist_ok=True)

        ext_map = {"m3u": ".m3u8", "csv": ".csv", "enigma2": ".tv", "xmltv": ".xml"}
        output_path = Path(args.output) if args.output else output_dir / f"apexsat_channels{ext_map[args.export]}"

        if args.export == "m3u":
            exporter.export_m3u(output_path, args.type)
        elif args.export == "csv":
            exporter.export_csv(output_path)
        elif args.export == "enigma2":
            exporter.export_enigma2(output_path)
        elif args.export == "xmltv":
            exporter.export_xmltv(output_path)

    # İstatistikler
    elif args.stats:
        stats = db.get_channel_count()
        if stats["total"] == 0:
            print("📊 Kayıtlı kanal yok. Önce tarama yapın.")
            return

        print("\n📊 APEXSAT AI - Kanal İstatistikleri")
        print("─" * 40)
        print(f"  📋 Toplam kanal: {stats['total']}")
        print(f"  📺 TV kanalları: {stats['tv']}")
        print(f"  📻 Radyo kanalları: {stats['radio']}")
        print(f"  🔷 HD kanallar: {stats['hd']}")
        print(f"  🔓 FTA (ücretsiz): {stats['fta']}")
        print("─" * 40)


if __name__ == "__main__":
    main()
