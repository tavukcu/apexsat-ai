#!/usr/bin/env python3
"""
APEXSAT AI - DiSEqC Motor ve Switch Kontrol Modülü

DiSEqC 1.0/1.1/1.2 ve USALS protokol desteği.
LNB voltaj (13V/18V) ve 22kHz tone kontrolü.
"""

import struct
import time
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


class DiSEqCVersion(IntEnum):
    V1_0 = 10   # 4 switch pozisyon
    V1_1 = 11   # 16 switch pozisyon
    V1_2 = 12   # Motor kontrol (pozisyoner)


class MotorDirection(IntEnum):
    EAST = 0
    WEST = 1
    STOP = 2


@dataclass
class SatellitePosition:
    name: str
    longitude: float      # Derece (Doğu pozitif, Batı negatif)
    lnb_type: str = "Universal"
    diseqc_port: int = 0  # DiSEqC switch port (0-3 veya 0-15)

    @property
    def orbital_position(self) -> str:
        direction = "E" if self.longitude >= 0 else "W"
        return f"{abs(self.longitude):.1f}°{direction}"


# Yaygın uydu pozisyonları (Türkiye'den görülebilen)
SATELLITE_POSITIONS = {
    "turksat": SatellitePosition("Türksat 4A/5A/6A", 42.0, diseqc_port=0),
    "hotbird": SatellitePosition("Eutelsat Hot Bird", 13.0, diseqc_port=1),
    "astra_19": SatellitePosition("Astra 1 (19.2°E)", 19.2, diseqc_port=2),
    "astra_28": SatellitePosition("Astra 2 (28.2°E)", 28.2, diseqc_port=3),
    "eutelsat_7": SatellitePosition("Eutelsat 7A", 7.0),
    "amos": SatellitePosition("Amos (4°W)", -4.0),
    "nilesat": SatellitePosition("Nilesat (7°W)", -7.0),
    "badr": SatellitePosition("Badr/Arabsat (26°E)", 26.0),
    "hellas": SatellitePosition("Hellas Sat (39°E)", 39.0),
    "yamal": SatellitePosition("Yamal 402 (55°E)", 55.0),
}


class DiSEqCController:
    """DiSEqC switch ve motor kontrol sınıfı."""

    # DiSEqC komut framing byte'ları
    FRAMING_MASTER_NOREPLY = 0xE0    # Master, yanıt bekleme
    FRAMING_MASTER_REPLY = 0xE1      # Master, yanıt bekle
    FRAMING_REPEAT_NOREPLY = 0xE3    # Tekrar, yanıt bekleme

    # Adres byte'ları
    ADDR_ANY = 0x00                   # Herhangi bir cihaz
    ADDR_POLAR_POSITIONER = 0x10      # Polarizasyon / pozisyoner
    ADDR_POSITIONER = 0x31            # Pozisyoner (motor)
    ADDR_SWITCH = 0x10                # LNB switch

    # Komut byte'ları
    CMD_RESET = 0x00
    CMD_CLR_RESET = 0x01
    CMD_WRITE_N0 = 0x38              # DiSEqC 1.0 switch komutu
    CMD_WRITE_N1 = 0x39              # DiSEqC 1.1 switch komutu
    CMD_GOTO_POSITION = 0x6B         # Motor: pozisyona git
    CMD_STORE_POSITION = 0x6A        # Motor: pozisyon kaydet
    CMD_GOTO_ANGULAR = 0x6E          # Motor: açısal pozisyona git
    CMD_DRIVE_EAST = 0x68            # Motor: doğuya dön
    CMD_DRIVE_WEST = 0x69            # Motor: batıya dön
    CMD_STOP = 0x60                  # Motor: dur
    CMD_LIMITS_OFF = 0x63            # Motor: limit kaldır
    CMD_SET_EAST_LIMIT = 0x66        # Motor: doğu limiti ayarla
    CMD_SET_WEST_LIMIT = 0x67        # Motor: batı limiti ayarla
    CMD_GOTO_REF = 0x6B              # Motor: referans pozisyona git (0)

    def __init__(self, adapter_num: int = 0, frontend_num: int = 0):
        self.adapter_num = adapter_num
        self.frontend_num = frontend_num
        self.frontend_fd = None
        self._current_voltage = 0
        self._current_tone = False

    def _build_diseqc_cmd(self, framing: int, addr: int, cmd: int,
                           data: bytes = b"") -> bytes:
        """DiSEqC komut paketi oluştur."""
        msg = bytes([framing, addr, cmd]) + data
        return msg

    def _send_diseqc_cmd(self, msg: bytes):
        """DiSEqC komutu gönder (ioctl üzerinden)."""
        # Not: Gerçek implementasyonda Linux DVB ioctl kullanılır
        # FE_DISEQC_SEND_MASTER_CMD
        hex_str = " ".join(f"0x{b:02X}" for b in msg)
        print(f"  DiSEqC TX: [{hex_str}]")

        # Gerçek gönderim (Linux ortamında):
        # import fcntl
        # FE_DISEQC_SEND_MASTER_CMD = 0x40086f63
        # struct diseqc_master_cmd { uint8_t msg[6]; uint8_t msg_len; }
        # cmd_struct = struct.pack("6sB", msg.ljust(6, b'\x00'), len(msg))
        # fcntl.ioctl(self.frontend_fd, FE_DISEQC_SEND_MASTER_CMD, cmd_struct)

        time.sleep(0.05)  # 50ms bekleme (DiSEqC protokol gerekliliği)

    def set_voltage(self, voltage: int):
        """LNB voltajını ayarla (13V=Vertical, 18V=Horizontal)."""
        self._current_voltage = voltage
        print(f"  LNB Voltaj: {voltage}V ({'Horizontal' if voltage == 18 else 'Vertical'})")
        # Gerçek: ioctl(fd, FE_SET_VOLTAGE, SEC_VOLTAGE_13/18)

    def set_tone(self, on: bool):
        """22kHz tone ayarla (band seçimi)."""
        self._current_tone = on
        print(f"  22kHz Tone: {'ON (Yüksek band)' if on else 'OFF (Düşük band)'}")
        # Gerçek: ioctl(fd, FE_SET_TONE, SEC_TONE_ON/OFF)

    def send_tone_burst(self, sat_a: bool = True):
        """Tone burst gönder (mini-DiSEqC)."""
        burst = "SAT-A" if sat_a else "SAT-B"
        print(f"  Tone Burst: {burst}")
        # Gerçek: ioctl(fd, FE_DISEQC_SEND_BURST, SEC_MINI_A/B)

    # ─── DiSEqC 1.0 Switch ──────────────────────────────────────────────

    def switch_port_1_0(self, port: int, polarization: str, high_band: bool):
        """
        DiSEqC 1.0 switch port seçimi (4 pozisyon).

        Args:
            port: Switch port numarası (0-3)
            polarization: "H" veya "V"
            high_band: True = yüksek band (22kHz ON)
        """
        if port < 0 or port > 3:
            raise ValueError(f"DiSEqC 1.0: Port 0-3 arası olmalı, verilen: {port}")

        # Data byte hesaplama
        # Bit 0: Low/High band
        # Bit 1: V/H polarization
        # Bit 2-3: Port (0-3)
        # Bit 4: Position option
        # Bit 5-7: Sabit (1, 1, 0)

        data = 0xF0  # Üst 4 bit sabit
        data |= (port & 0x03) << 2
        data |= (1 if polarization == "H" else 0) << 1
        data |= (1 if high_band else 0)

        print(f"\n📡 DiSEqC 1.0 - Port {port + 1} seçiliyor...")

        # Voltaj ve tone ayarla
        self.set_voltage(18 if polarization == "H" else 13)
        time.sleep(0.015)
        self.set_tone(False)
        time.sleep(0.015)

        # DiSEqC komutu gönder
        msg = self._build_diseqc_cmd(
            self.FRAMING_MASTER_NOREPLY,
            self.ADDR_SWITCH,
            self.CMD_WRITE_N0,
            bytes([data])
        )
        self._send_diseqc_cmd(msg)
        time.sleep(0.015)

        # Tone burst
        self.send_tone_burst(port < 2)
        time.sleep(0.015)

        # 22kHz tone ayarla
        self.set_tone(high_band)

        print(f"  ✅ Port {port + 1} aktif\n")

    # ─── DiSEqC 1.1 Switch ──────────────────────────────────────────────

    def switch_port_1_1(self, port: int, polarization: str, high_band: bool):
        """
        DiSEqC 1.1 switch port seçimi (16 pozisyon).

        Args:
            port: Switch port numarası (0-15)
        """
        if port < 0 or port > 15:
            raise ValueError(f"DiSEqC 1.1: Port 0-15 arası olmalı, verilen: {port}")

        # Uncommitted switch (1.1) data byte
        data = 0xF0 | (port & 0x0F)

        print(f"\n📡 DiSEqC 1.1 - Port {port + 1} seçiliyor...")

        self.set_voltage(18 if polarization == "H" else 13)
        time.sleep(0.015)
        self.set_tone(False)
        time.sleep(0.015)

        # Önce 1.1 uncommitted komutu
        msg_11 = self._build_diseqc_cmd(
            self.FRAMING_MASTER_NOREPLY,
            self.ADDR_SWITCH,
            self.CMD_WRITE_N1,
            bytes([data])
        )
        self._send_diseqc_cmd(msg_11)
        time.sleep(0.025)

        # Sonra 1.0 committed komutu (ilk 4 port için)
        committed_port = port % 4
        data_10 = 0xF0
        data_10 |= (committed_port & 0x03) << 2
        data_10 |= (1 if polarization == "H" else 0) << 1
        data_10 |= (1 if high_band else 0)

        msg_10 = self._build_diseqc_cmd(
            self.FRAMING_MASTER_NOREPLY,
            self.ADDR_SWITCH,
            self.CMD_WRITE_N0,
            bytes([data_10])
        )
        self._send_diseqc_cmd(msg_10)
        time.sleep(0.015)

        self.set_tone(high_band)
        print(f"  ✅ Port {port + 1} aktif\n")

    # ─── DiSEqC 1.2 Motor (Pozisyoner) ──────────────────────────────────

    def motor_goto_position(self, position: int):
        """
        Motor: Kayıtlı pozisyona git.

        Args:
            position: Pozisyon numarası (1-255, 0=referans)
        """
        print(f"\n🔄 Motor: Pozisyon {position}'e gidiliyor...")
        msg = self._build_diseqc_cmd(
            self.FRAMING_MASTER_NOREPLY,
            self.ADDR_POSITIONER,
            self.CMD_GOTO_POSITION,
            bytes([position])
        )
        self._send_diseqc_cmd(msg)
        time.sleep(0.1)

    def motor_store_position(self, position: int):
        """Motor: Mevcut konumu kaydet."""
        print(f"💾 Motor: Pozisyon {position} kaydediliyor...")
        msg = self._build_diseqc_cmd(
            self.FRAMING_MASTER_NOREPLY,
            self.ADDR_POSITIONER,
            self.CMD_STORE_POSITION,
            bytes([position])
        )
        self._send_diseqc_cmd(msg)

    def motor_drive(self, direction: MotorDirection, steps: int = 0):
        """
        Motor: Yön ve hız kontrolü.

        Args:
            direction: EAST, WEST veya STOP
            steps: 0=sürekli, 1-127=adım sayısı
        """
        if direction == MotorDirection.STOP:
            print("⏹️  Motor: Durduruluyor...")
            msg = self._build_diseqc_cmd(
                self.FRAMING_MASTER_NOREPLY,
                self.ADDR_POSITIONER,
                self.CMD_STOP,
            )
        else:
            dir_name = "Doğu" if direction == MotorDirection.EAST else "Batı"
            cmd = self.CMD_DRIVE_EAST if direction == MotorDirection.EAST else self.CMD_DRIVE_WEST

            # steps: 0x00=sürekli, 0x01-0x7F=adım (timeout=yavaş...hızlı)
            step_byte = min(steps, 0x7F) if steps > 0 else 0x00
            mode = f"{steps} adım" if steps > 0 else "sürekli"
            print(f"🔄 Motor: {dir_name}'ya dönüyor ({mode})...")

            msg = self._build_diseqc_cmd(
                self.FRAMING_MASTER_NOREPLY,
                self.ADDR_POSITIONER,
                cmd,
                bytes([step_byte])
            )

        self._send_diseqc_cmd(msg)

    def motor_set_limit(self, direction: MotorDirection):
        """Motor: Dönüş limiti ayarla."""
        if direction == MotorDirection.EAST:
            print("📍 Motor: Doğu limiti ayarlandı")
            cmd = self.CMD_SET_EAST_LIMIT
        else:
            print("📍 Motor: Batı limiti ayarlandı")
            cmd = self.CMD_SET_WEST_LIMIT

        msg = self._build_diseqc_cmd(
            self.FRAMING_MASTER_NOREPLY,
            self.ADDR_POSITIONER,
            cmd,
        )
        self._send_diseqc_cmd(msg)

    def motor_limits_off(self):
        """Motor: Limitleri kaldır."""
        print("🔓 Motor: Limitler kaldırıldı")
        msg = self._build_diseqc_cmd(
            self.FRAMING_MASTER_NOREPLY,
            self.ADDR_POSITIONER,
            self.CMD_LIMITS_OFF,
        )
        self._send_diseqc_cmd(msg)

    # ─── USALS (DiSEqC 1.3) ─────────────────────────────────────────────

    def usals_goto_angle(self, satellite_longitude: float,
                          site_latitude: float, site_longitude: float):
        """
        USALS: Uydu açısına göre motor pozisyonlama.

        GotoX protokolü ile motor açısını hesaplar ve gönderir.

        Args:
            satellite_longitude: Uydu boylamı (Doğu pozitif)
            site_latitude: Alıcı enlem (Kuzey pozitif)
            site_longitude: Alıcı boylam (Doğu pozitif)
        """
        import math

        # Motor açısı hesaplama (GotoX formülü)
        sat_lon_rad = math.radians(satellite_longitude)
        site_lat_rad = math.radians(site_latitude)
        site_lon_rad = math.radians(site_longitude)

        delta_lon = sat_lon_rad - site_lon_rad

        # Azimut hesaplama
        azimuth = math.atan2(
            math.tan(delta_lon),
            math.sin(site_lat_rad)
        )

        # Elevasyon hesaplama
        r_eq = 42164.0    # Geostasyon yörünge yarıçapı (km)
        r_earth = 6378.14  # Dünya yarıçapı (km)

        cos_gamma = math.cos(site_lat_rad) * math.cos(delta_lon)
        elevation = math.atan2(
            cos_gamma - r_earth / r_eq,
            math.sqrt(1 - cos_gamma ** 2)
        )

        # Motor açısı
        motor_angle = math.degrees(azimuth)

        print(f"\n🛰️  USALS Hesaplama:")
        print(f"  Uydu: {satellite_longitude:.1f}°{'E' if satellite_longitude >= 0 else 'W'}")
        print(f"  Konum: {site_latitude:.2f}°N, {site_longitude:.2f}°E")
        print(f"  Motor açısı: {motor_angle:.2f}°")
        print(f"  Elevasyon: {math.degrees(elevation):.2f}°")

        # GotoX DiSEqC komutu (açıyı 16-bit formatına çevir)
        # Byte 1: D[7:4] = derece onlar, D[3:0] = derece birler
        # Byte 2: D[7:4] = ondalık 1. basamak, D[3:0] = ondalık 2. basamak

        angle_abs = abs(motor_angle)
        direction = 0xE0 if motor_angle >= 0 else 0xD0  # Doğu/Batı

        degrees_int = int(angle_abs)
        fraction = angle_abs - degrees_int

        byte1 = direction | (degrees_int >> 4)
        byte2 = ((degrees_int & 0x0F) << 4) | int(fraction * 16)

        msg = self._build_diseqc_cmd(
            self.FRAMING_MASTER_NOREPLY,
            self.ADDR_POSITIONER,
            self.CMD_GOTO_ANGULAR,
            bytes([byte1, byte2])
        )
        self._send_diseqc_cmd(msg)

        dir_name = "Doğu" if motor_angle >= 0 else "Batı"
        print(f"  🔄 Motor {abs(motor_angle):.2f}° {dir_name}'ya gönderildi\n")

    def goto_satellite(self, sat_name: str,
                        site_lat: float = 38.42, site_lon: float = 27.14):
        """
        Bilinen uyduya yönlen (USALS ile).

        Args:
            sat_name: Uydu kısa adı (turksat, hotbird, astra_19, vs.)
            site_lat: Alıcı enlemi (varsayılan: İzmir/Manisa civarı)
            site_lon: Alıcı boylamı
        """
        sat = SATELLITE_POSITIONS.get(sat_name.lower())
        if not sat:
            available = ", ".join(SATELLITE_POSITIONS.keys())
            print(f"❌ Bilinmeyen uydu: {sat_name}")
            print(f"   Mevcut: {available}")
            return

        print(f"🛰️  {sat.name} ({sat.orbital_position})'e yönleniyor...")
        self.usals_goto_angle(sat.longitude, site_lat, site_lon)


# ─── Kullanım Örneği ────────────────────────────────────────────────────────

if __name__ == "__main__":
    diseqc = DiSEqCController(adapter_num=0)

    print("=" * 50)
    print("  APEXSAT AI - DiSEqC Kontrol Testi")
    print("=" * 50)

    # DiSEqC 1.0 switch testi
    print("\n--- DiSEqC 1.0 Switch Testi ---")
    diseqc.switch_port_1_0(port=0, polarization="V", high_band=False)

    # USALS motor testi - Türksat'a yönlen
    # Konum: Manisa/Ahmetli civarı (yaklaşık)
    print("\n--- USALS Motor Testi ---")
    diseqc.goto_satellite("turksat", site_lat=38.52, site_lon=27.94)

    # Diğer uydu testleri
    diseqc.goto_satellite("hotbird", site_lat=38.52, site_lon=27.94)

    print("\n✅ DiSEqC test tamamlandı")
