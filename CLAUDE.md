# APEXSAT AI - Akıllı DVB-S2 Uydu Alıcısı

## Proje Bilgisi
- **Konum:** `/Users/halildincer/Desktop/apexsat-ai/`
- **GitHub:** tavukcu/apexsat-ai
- **Yazar:** Halil Dinçer - Dinçer Tavukçuluk / APEX Serisi
- **Hedef:** AI destekli DVB-S2/S2X uydu alıcısı (Türksat 42°E odaklı)
- **SoC:** Amlogic S905X4-J (Quad A55, Mali-G31, 1.2 TOPS NPU)
- **PCB:** 6-katman, 150x100mm, ENIG, JLCPCB üretim

## Dizin Yapısı
- `hardware/schematics/` - Blok diyagram, netlist, power tree, routing guide'lar
- `hardware/bom/` - BOM, JLCPCB komponent listesi, LCSC doğrulama
- `hardware/pcb/` - Layer stackup, yerleşim rehberi
- `hardware/production/` - Gerber, BOM, CPL, üretim checklist
- `firmware/` - Buildroot, kernel, device tree, U-Boot
- `software/dvb/` - Kanal tarama, EPG, tuner kontrol
- `software/media/` - GStreamer pipeline, PVR, timeshift
- `software/ai/` - Whisper, TTS, öneri motoru, AI super resolution
- `software/ui/` - Qt/QML kullanıcı arayüzü

## Donanım Özeti
- **SoC:** S905X4-J (BGA-272, 0.65mm pitch)
- **DDR4:** 4x K4A8G165WC-BCWE (4GB, 32-bit, fly-by)
- **eMMC:** KLMAG1JETD-B041 (32GB, HS400)
- **DVB-S2:** BSBE2-401A NIM + LNBH26PQR (LNB)
- **ETH:** RTL8211F-CG (QFN-40, RGMII) + HR911105A (RJ45)
- **WiFi/BT:** RTL8822CS-VL-CG (QFN-76, SDIO+UART)
- **HDMI:** 2.0b + IP4791CZ12 ESD
- **Güç:** MP2315(5V), MP1584EN(3.3V), SY8088(0.9V), MP8759(1.1V), RT9193(1.8V)
- **RF 3.3V:** Ferrit bead filtre (AP2112K termal analiz sonucu kaldırıldı)

## Kritik Tasarım Notları
- AP2112K LDO termal yetersiz → MP1584EN + ferrit bead ile değiştirildi
- SY8088 Vin max 5.5V → 5V rail'den beslenir (12V'dan DEĞİL)
- RTL8211F paketi QFN-40 (QFN-48 DEĞİL) → footprint doğrula
- LNBH26PQR LCSC'de yok → DigiKey'den consigned part
- INMP441 bare IC yok → MSM261S4030H0R alternatif (C2840615)
- DDR4 empedans: 40Ω SE, 80Ω diff (DQS/CK)
- HDMI empedans: 100Ω diff (TMDS)
- USB empedans: 90Ω diff (SS + HS)

## Diller
- Sistem: C/C++ | Uygulama: Python 3.11+ | UI: QML + JS | Firmware: C | Script: Bash + Python

## Kurallar
- Türkçe iletişim
- Build: aarch64-linux-gnu cross-compile
- AI modelleri INT8 quantized (NPU uyumlu)
- DVB: Linux DVB subsystem kullan
- PCB: JLCPCB 6-layer, impedans kontrollü, ENIG
