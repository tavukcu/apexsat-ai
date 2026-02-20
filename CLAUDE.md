# APEXSAT AI - Akıllı DVB-S2 Uydu Alıcısı

## Proje Bilgisi
- **Konum:** `/Users/halildincer/Desktop/apexsat-ai/`
- **Yazar:** Halil Dinçer - Dinçer Tavukçuluk / APEX Serisi
- **Hedef:** AI destekli DVB-S2/S2X uydu alıcısı (Türksat 42°E odaklı)
- **SoC:** Amlogic S905X4-J (Quad A55, Mali-G31, 1.2 TOPS NPU)

## Dizin Yapısı
- `hardware/` - EasyEDA Pro şematik, PCB, BOM, kasa tasarımı
- `firmware/` - Buildroot, kernel, device tree, U-Boot
- `software/dvb/` - Kanal tarama, EPG, tuner kontrol
- `software/media/` - GStreamer pipeline, PVR, timeshift
- `software/ai/` - Whisper, TTS, öneri motoru, AI super resolution
- `software/ui/` - Qt/QML kullanıcı arayüzü
- `software/iptv/` - IPTV/OTT entegrasyonu
- `software/iot/` - MQTT, APEX cihaz entegrasyonu
- `software/remote/` - BLE kumanda firmware
- `tools/` - Yardımcı scriptler
- `tests/` - Test kodları

## Diller
- Sistem: C/C++ | Uygulama: Python 3.11+ | UI: QML + JS | Firmware: C | Script: Bash + Python

## Kurallar
- Türkçe iletişim
- Build: aarch64-linux-gnu cross-compile
- AI modelleri INT8 quantized (NPU uyumlu)
- DVB: Linux DVB subsystem kullan
