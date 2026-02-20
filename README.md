# APEXSAT AI v1.0

**AI Destekli DVB-S2 Uydu Alicisi - PCB Tasarim ve Firmware**

Amlogic S905X4 tabanli, yapay zeka destekli akilli uydu alicisi. Turksat 42°E odakli, sesli asistan, AI oneri motoru ve 4K HDR destegi.

## Donanim Ozellikleri

| Ozellik | Deger |
|---------|-------|
| SoC | Amlogic S905X4-J (Quad A55 2.0GHz, Mali-G31, 1.2T NPU) |
| RAM | 4GB DDR4-3200 (4x K4A8G165WC-BCWE, 32-bit) |
| Depolama | 32GB eMMC 5.1 + microSD |
| Tuner | DVB-S2/S2X NIM (CX24116) + LNBH26 LNB Power |
| Video | HDMI 2.0b 4K@60Hz HDR |
| Ag | Gigabit Ethernet (RTL8211F) + WiFi 5 ac + BT 5.0 (RTL8822CS) |
| USB | 1x USB 3.0 + 2x USB 2.0 + 1x USB-C (Debug) |
| Ses | TOSLINK SPDIF + 3.5mm AV + 2x MEMS Mikrofon (I2S) |
| Guc | 12V/3A DC, 6 regulator (MP2315, MP1584EN, SY8088, MP8759, RT9193) |
| PCB | 6 katman, 150x100mm, ENIG, empedans kontrollu |
| Uretim | JLCPCB SMT Assembly |

## Prototip Maliyeti

| Kalem | Tutar |
|-------|-------|
| BOM (72 benzersiz parca) | ~$72 |
| PCB (6L, ENIG) | ~$30 |
| SMT Assembly | ~$75 |
| Kargo | ~$20 |
| **Toplam (1 adet)** | **~$197** |
| **Birim (100 adet)** | **~$49** |

## Dizin Yapisi

```
apexsat-ai/
├── hardware/
│   ├── schematics/          # Blok diyagram, netlist, power tree, routing
│   ├── bom/                 # JLCPCB BOM, LCSC dogrulanmis komponent listesi
│   ├── pcb/                 # 6-katman stackup, yerlesim rehberi
│   └── production/          # Gerber, empedans, uretim checklist
│
├── firmware/
│   └── buildroot/           # Buildroot defconfig + build script (S905X4)
│
├── software/
│   ├── dvb/                 # Kanal tarama, EPG, DiSEqC (Turksat 42°E)
│   ├── media/               # GStreamer pipeline (live TV, PVR, timeshift)
│   ├── ai/
│   │   ├── whisper/         # Sesli asistan (Turkce STT, 30+ komut)
│   │   └── recommendation/  # AI oneri motoru (hibrit CF+CB)
│   └── ui/                  # Qt/QML 10-foot UI (13 bilesen)
│
└── tests/                   # Test kodlari
```

## Donanim Tasarim Dokumanlari

10 adimlik PCB tasarim sureci tamamlanmistir:

| # | Dokuman | Dosya |
|---|---------|-------|
| 1 | Blok Diyagram | `hardware/schematics/block_diagram.md` |
| 2 | Pin-Pin Netlist | `hardware/schematics/netlist_connections.md` |
| 3 | Guc Dagitim Agaci | `hardware/schematics/power_tree.md` |
| 4 | JLCPCB Komponent Listesi | `hardware/bom/jlcpcb_component_list.csv` |
| 5 | DDR4 Routing Guide | `hardware/schematics/ddr4_routing_guide.md` |
| 6 | High-Speed Routing Guide | `hardware/schematics/highspeed_routing_guide.md` |
| 7 | Sematik Sayfa Plani | `hardware/schematics/schematic_pages_plan.md` |
| 8 | PCB Stackup | `hardware/pcb/layer_stackup_and_placement.md` |
| 9 | Termal Analiz | `hardware/thermal_analysis.md` |
| 10 | Uretim Checklist | `hardware/production/jlcpcb_checklist.md` |

## Guc Mimarisi

```
12V DC (3A) --> D2 (Schottky) --> F1 (3A PPTC)
                |
                +---> MP2315  --> 5V / 3A Buck
                |     +---> SY8088  --> 0.9V / 1A (SoC Core) [1st]
                |     +---> MP8759  --> 1.1V / 2A (GPU+DDR4)  [2nd]
                |     +---> RT9193  --> 1.8V / 300mA (DDR4)   [3rd]
                |     +---> USB VBUS, HDMI 5V
                |
                +---> MP1584EN --> 3.3V / 3A Buck
                |     +---> Ferrit Bead --> 3.3V_RF (DVB izole)
                |
                +---> LNBH26  --> 13V/18V LNB Power
```

## Kritik Tasarim Notlari

- **AP2112K kaldirildi**: SOT-23-5 LDO termal yetersiz (234°C junction!) -> MP1584EN + ferrit bead
- **SY8088 besleme**: Vin max 5.5V, 5V rail'den beslenir (12V'dan DEGIL)
- **RTL8211F paketi**: QFN-40 (QFN-48 degil) - footprint dogrula
- **LNBH26PQR**: LCSC'de stoklanmiyor - DigiKey'den consigned part
- **DDR4 empedans**: 40 ohm SE, 80 ohm diff (fly-by topoloji)
- **HDMI empedans**: 100 ohm diff (TMDS)

## Yazilim Ozellikleri

- **Kanal Tarama**: Turksat 42°E 56 transponder, blind scan, NIT scan
- **Medya**: GStreamer pipeline, PVR kayit, timeshift, IPTV
- **Sesli Asistan**: Whisper.cpp Turkce STT + Piper TTS
- **AI Oneri**: Hibrit collaborative + content-based filtreleme
- **UI**: Qt/QML 10-foot arayuz, 13 sayfa/bilesen

## Build (Firmware)

```bash
cd firmware/buildroot
chmod +x build.sh
./build.sh
```

Buildroot 2024.02 indirir, S905X4 icin cross-compile yapar, rootfs + kernel + u-boot uretir.

## Lisans

Bu proje Halil Dincer - Dincer Tavukculuk / APEX Serisi'ne aittir.

## Iletisim

Halil Dincer - [GitHub](https://github.com/tavukcu)
