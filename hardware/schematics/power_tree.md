# APEXSAT AI v1.0 - Güç Dağıtım Ağacı (Power Tree)

## Tasarımcı: Halil Dinçer
## Tarih: 2026-02-20 | Revizyon: A

---

## 1. GENEL GÜÇ MİMARİSİ

```
                    ┌─────────────────────────────┐
                    │  12V DC GİRİŞ               │
                    │  Barrel Jack 5.5x2.1mm      │
                    │  Max: 3A (36W)              │
                    │                             │
                    │  Koruma:                    │
                    │  ├── D2 (SS54 Schottky)     │ ← Ters polarite koruması
                    │  ├── F1 (3A PPTC Fuse)      │ ← Aşırı akım koruması
                    │  └── TVS (SMBJ15A)          │ ← Aşırı gerilim koruması
                    └──────────────┬──────────────┘
                                   │
                                   │ 12V / 3A
                                   │
          ┌────────────────────────┼───────────────────────────────┐
          │                        │                               │
          ▼                        ▼                               ▼
    ┌───────────┐           ┌───────────┐                   ┌───────────┐
    │  U11      │           │  U15      │                   │  U4       │
    │  MP2315   │           │  SY8088   │                   │  LNBH26   │
    │  12V→5V   │           │  12V→0.9V │                   │  12V→     │
    │  BUCK     │           │  BUCK     │                   │  13V/18V  │
    │  3A       │           │  3A       │                   │  500mA    │
    └─────┬─────┘           └─────┬─────┘                   └─────┬─────┘
          │                       │                               │
          │ 5V / 3A               │ 0.9V / 3A                    │ LNB
          │ (ENABLE: always)      │ (ENABLE: 1st)                │ (I2C ctrl)
          │                       │ ↓                             │
          │                       │ S905X4 VDDCORE               ▼
          │                       │ (CPU çekirdek)           ┌─────────┐
          │                       │                          │  LNB    │
          │                       │                          │  F-Type │
          │                       │                          │  13/18V │
          │                       │                          └─────────┘
          │
     ┌────┼──────────────────┐
     │    │                  │
     ▼    ▼                  ▼
┌────────┐  ┌────────┐  ┌────────────┐
│ U14    │  │ U12a   │  │ USB VBUS   │
│ MP8759 │  │AP2112K │  │ (doğrudan) │
│ 5V→1.1V│  │5V→3.3V │  │            │
│ BUCK   │  │ LDO    │  │ J7: 500mA  │
│ 2A     │  │ 600mA  │  │ J8a: 500mA │
└───┬────┘  └───┬────┘  │ J8b: 500mA │
    │           │       └────────────┘
    │ 1.1V/2A  │ 3.3V/600mA
    │ (EN:2nd) │ (EN: always)
    │           │
    │ ├─ S905X4│ ├─── eMMC VCC (200mA)
    │ │  VDDGPU│ ├─── WiFi/BT VDD (300mA)
    │ │        │ ├─── RTL8211F AVDD33 (60mA)
    │ ├─ DDR4  │ ├─── LNBH26 VCC_IO (10mA)
    │    VDDQ  │ ├─── TSOP38238 VCC (5mA)
    │    (x4)  │ ├─── INMP441 VDD x2 (3mA)
    │          │ ├─── I2C Pull-ups (5mA)
    │          │ ├─── LED pull-ups (15mA)
    │          │ ├─── SSD1306 VCC (20mA)
    │          │ └─── GPIO pull-up/down (10mA)
    │          │
    │          │  ┌──────────┐
    │          └──┤ U12b     │
    │             │ AP2112K  │  (İkinci 3.3V LDO - sadece RF bölüm)
    │             │ 5V→3.3V  │
    │             │ 600mA    │
    │             └────┬─────┘
    │                  │
    │                  │ 3.3V_RF / 600mA
    │                  │ (RF bölge izolasyonu)
    │                  │
    │                  ├─── DVB NIM VCC (300mA)
    │                  └─── RF frontend (100mA)
    │
    │  ┌────────┐
    └──┤ U13    │
       │ RT9193 │
       │3.3V→   │
       │1.8V LDO│
       │ 300mA  │
       └───┬────┘
           │
           │ 1.8V / 300mA
           │ (EN: 3rd)
           │
           ├─── DDR4 VDD x4 (200mA)
           ├─── eMMC VCCQ (50mA)
           └─── S905X4 VDDIO_1.8V (30mA)
```

---

## 2. REGÜLATÖR DETAYLI TASARIMLARI

### 2.1 U11: MP2315 (12V → 5V, 3A Buck Converter)

```
Datasheet: MPS MP2315GJ-Z (TSOT-23-8)

                    12V
                     │
              ┌──────┤
              │      │
         C_IN1│      │C_IN2
         22µF │      │100nF
         25V  │      │25V
              │      │
              └──┬───┘
                 │
            ┌────┴────┐
     EN ──>│1 EN  VIN 8│──── 12V
            │         │
            │         │
    BST ──>│2 BST  SW 7│────┬──── L2 (4.7µH/3A) ──┬── 5V OUTPUT
            │         │    │                       │
    100nF   │         │    │                  C_OUT1│C_OUT2
    BST cap │3 GND FB 6│    D_BST              100µF│100nF
            │         │    (Schottky)           16V │
            │  COMP   │                            │
            │4    AGND5│                            GND
            └─────────┘
                 │
                 GND

Hesaplamalar:
  - Vin: 12V, Vout: 5.0V, Iout_max: 3A
  - Fsw: 500kHz (dahili)
  - L = Vout × (1 - Vout/Vin) / (ΔIL × Fsw)
    = 5 × (1 - 5/12) / (0.3×3 × 500k) = 5.14µH → 4.7µH seç
  - Cin: 22µF/25V (seramik X7R) + 100nF
  - Cout: 100µF/16V (polimer) + 100nF (seramik)
  - Ripple: ~30mV

Feedback direnci (5V çıkış):
  - R_TOP = 100kΩ (Pin 6 FB → 5V output)
  - R_BOT = 31.6kΩ (Pin 6 FB → GND)
  - Vout = 0.6V × (1 + R_TOP/R_BOT) = 0.6 × (1 + 100/31.6) = 4.9V ≈ 5.0V

Enable: Doğrudan VIN'e bağlı (always on) veya
        Soft-start için 100kΩ + 100nF RC
```

### 2.2 U15: SY8088AAC (12V → 0.9V, 3A Buck - SoC VDDCORE)

```
Datasheet: Silergy SY8088AAC (SOT-23-6)

                    12V (veya 5V - tercih)
                     │
                C_IN │
                22µF │
                16V  │
                     │
            ┌────────┴────────┐
     EN ──>│1 EN      VIN  6│──── 5V
            │                │
            │                │
            │2 GND     SW   5│────── L3 (2.2µH/3A) ──┬── 0.9V OUTPUT
            │                │                        │
            │3 FB     BST  4│                    C_OUT│
            │                │                    100µF│
            └────────┬───────┘                    10V │
                     │                                │
                     GND                              GND

NOT: SY8088 Vin max = 5.5V, bu yüzden 5V rail'den beslenir (12V'dan DEĞİL)

Feedback direnci (0.9V çıkış):
  - Vref = 0.6V
  - R_TOP = 51kΩ (FB → 0.9V output)
  - R_BOT = 100kΩ (FB → GND)
  - Vout = 0.6V × (1 + 51/100) = 0.906V ≈ 0.9V

Inductor: 2.2µH, 3A saturation, shielded
Cout: 2x 22µF + 100nF (düşük ESR)

⚡ POWER SEQUENCING: Bu regülatör İLK açılmalı (SoC core voltage)
  - EN pin: Doğrudan 5V'a bağlı (5V gelince hemen çalışır)
  - VEYA: Power-good sinyali ile sıralama
```

### 2.3 U14: MP8759GD-Z (5V → 1.1V, 2A Buck - SoC GPU/NPU + DDR4 VDDQ)

```
Datasheet: MPS MP8759GD-Z (QFN-12, 3x3mm)

                    5V
                     │
                C_IN │
                22µF │
                10V  │
                     │
            ┌────────┴──────────┐
     EN ──>│ EN         VIN    │──── 5V
            │                   │
     SS  ──│ SS         BOOT   │──── 100nF boot cap
     1µF   │                   │
            │ FB         SW    │────── L4 (1.0µH/4A) ──┬── 1.1V OUTPUT
            │                   │                       │
            │ COMP       PGND  │                   C_OUT│
            │                   │                   100µF│
            │ PGOOD      AGND  │                   6.3V │
            └────────┬──────────┘                       │
                     │                                  GND
                     GND

Feedback direnci (1.1V çıkış):
  - Vref = 0.6V (dahili referans)
  - R_TOP = 82kΩ
  - R_BOT = 100kΩ
  - Vout = 0.6 × (1 + 82/100) = 1.092V ≈ 1.1V

PGOOD: Open-drain çıkış → bir sonraki regülatörün EN'ine
  - PGOOD → RT9193 EN (1.8V regülatörü tetikler)

⚡ POWER SEQUENCING: İKİNCİ açılır (SY8088 PGOOD sonrası)
  - EN pin: SY8088'in power-good sinyaline veya RC delay'e bağlı
```

### 2.4 U12a/b: AP2112K-3.3 (5V → 3.3V, 600mA LDO x2)

```
Datasheet: Diodes Inc AP2112K-3.3TRG1 (SOT-23-5)

                    5V
                     │
                C_IN │
                1µF  │
                10V  │
                     │
            ┌────────┴──────┐
            │1 VIN    VOUT 5│──┬── 3.3V OUTPUT
            │               │  │
     EN ──>│3 EN     GND  2│  │C_OUT
            │               │  │1µF
            │         NC   4│  │10V
            └────────┬──────┘  │
                     │         GND
                     GND

U12a: Ana 3.3V (dijital)
  - Yükler: eMMC, WiFi, Ethernet, I2C, LED, IR, mikrofon, OLED
  - Max yük: ~550mA
  - Cin: 1µF seramik, Cout: 1µF seramik
  - Dropout: 250mV tipik @ 600mA

U12b: RF 3.3V (analog/RF izolasyon)
  - Yükler: DVB NIM modülü, RF frontend
  - Max yük: ~400mA
  - Ayrı GND bölgesi ile besleme
  - Ferrit bead ile ana 3.3V'dan izole

NOT: 600mA LDO yeterli olmayabilir. Yük hesabı:
  Ana 3.3V: eMMC(200) + WiFi(300) + ETH(60) + diğer(100) = 660mA → SINIRDA
  Alternatif: AP2112K yerine AP7361C-33 (1A LDO) kullan
  VEYA: 3.3V için de buck converter (MP2315 ikinci adet)
```

### 2.5 U13: RT9193-18 (3.3V → 1.8V, 300mA LDO)

```
Datasheet: Richtek RT9193-18GB (SOT-23-5)

                    3.3V
                     │
                C_IN │
                1µF  │
                     │
            ┌────────┴──────┐
            │1 VIN    VOUT 5│──┬── 1.8V OUTPUT
            │               │  │
     EN ──>│3 EN     GND  2│  │C_OUT
            │               │  │1µF
            │        BP   4│  │
            │        │      │  │
            │        10nF   │  GND
            └────────┬──────┘
                     │
                     GND

Yükler:
  - DDR4 VDD x4 chip: ~200mA (aktif), 50mA (idle)
  - eMMC VCCQ: 50mA
  - SoC 1.8V I/O: 30mA
  - Toplam: ~280mA → 300mA LDO yeterli (sınırda)

Bypass pin (BP): 10nF düşük gürültü kapasitör

⚡ POWER SEQUENCING: ÜÇÜNCÜ açılır
  - EN pin: MP8759'un PGOOD sinyaline bağlı
  - DDR4 VDD (1.8V) aktif OLMADAN DDR4 başlatılamaz
```

---

## 3. POWER SEQUENCING (GÜÇ SIRALAMASI)

```
T=0ms     T=2ms      T=5ms      T=10ms     T=50ms     T=100ms
  │         │          │          │          │          │
  │    ┌────┘     ┌────┘     ┌────┘          │          │
  │    │          │          │               │          │
  ▼    ▼          ▼          ▼               ▼          ▼
─────────────────────────────────────────────────────────────
  12V IN          5V (MP2315) hemen aktif
      ──────────────────────────────────────────────────────

                  ┌── 0.9V (SY8088) - SoC Core [1. AÇILAN]
                  │   EN: 5V'a doğrudan bağlı
                  │   Rise time: ~2ms
                  │
                  ├── 1.1V (MP8759) - GPU/NPU + DDR4 VDDQ [2. AÇILAN]
                  │   EN: SY8088 PGOOD'a bağlı veya RC delay
                  │   Gecikme: ~3ms
                  │
                  ├── 1.8V (RT9193) - DDR4 VDD [3. AÇILAN]
                  │   EN: MP8759 PGOOD'a bağlı
                  │   Gecikme: ~5ms
                  │
                  ├── 3.3V (AP2112K) - hemen aktif (EN=VIN)
                  │   5V ile birlikte gelir
                  │
                  └── LNB Power (LNBH26) - sadece I2C komutu ile
                      SoC boot tamamlandıktan sonra

Sıralama mantığı:
  1. 12V → 5V Buck açılır (MP2315, EN=VIN)
  2. 5V hazır → 0.9V açılır (SY8088, EN=5V)
  3. 0.9V PGOOD → 1.1V açılır (MP8759, EN=PGOOD_0.9V)
  4. 1.1V PGOOD → 1.8V açılır (RT9193, EN=PGOOD_1.1V)
  5. 3.3V: 5V ile paralel açılır (AP2112K x2, EN=5V)
  6. SoC boot → LNB power enable (I2C komutu, yazılımsal)

Kapatma sırası (ters):
  6 → 5 → 4 → 3 → 2 → 1

RC Delay alternatifi (PGOOD yoksa):
  - R=100kΩ, C=100nF → τ=10ms delay
  - Her kademe arasına RC delay devresi
```

---

## 4. GÜÇ HESAPLAMALARI

### 4.1 Toplam Güç Bütçesi

| Rail | Voltaj | Tipik Akım | Max Akım | Tipik Güç | Max Güç | Kaynak |
|------|--------|-----------|----------|-----------|---------|--------|
| 0.9V | 0.9V | 1.5A | 3.0A | 1.35W | 2.70W | SoC CPU Core |
| 1.1V | 1.1V | 1.2A | 2.0A | 1.32W | 2.20W | SoC GPU + DDR4 VDDQ |
| 1.8V | 1.8V | 0.20A | 0.30A | 0.36W | 0.54W | DDR4 VDD + eMMC VCCQ |
| 3.3V | 3.3V | 0.50A | 1.0A | 1.65W | 3.30W | Peripheral I/O |
| 3.3V_RF | 3.3V | 0.30A | 0.50A | 0.99W | 1.65W | DVB frontend |
| 5V (USB) | 5.0V | 0.50A | 1.5A | 2.50W | 7.50W | USB VBUS |
| LNB | 13/18V | 0.20A | 0.50A | 3.60W | 9.00W | LNB (çanaktan) |
| **TOPLAM** | | | | **11.77W** | **26.89W** | |

### 4.2 12V Giriş Akım Hesabı

```
Verim varsayımları:
  - Buck converter: %90
  - LDO: Vout/Vin × %100

5V Buck (MP2315):
  I_out_5V = 3.3V×1A/0.9 + 1.8V×0.3A/0.9 + 0.9V×1.5A/0.9 + 1.1V×1.2A/0.9 + 5V×0.5A/0.9
  P_5V_input = (1.65+0.54+1.35+1.32+2.50) / 0.9 = 8.18W
  I_12V_for_5V = 8.18W / 12V = 0.68A

LNB Power (LNBH26):
  I_12V_for_LNB = 18V × 0.3A / (12V × 0.85) = 0.53A (en kötü durum)

SY8088 (12V'dan değil 5V'dan besleniyor → MP2315 yüküne dahil)

Toplam 12V giriş akımı (tipik): 0.68A + 0.53A = 1.21A (14.5W)
Toplam 12V giriş akımı (max):   ~2.5A (30W)

→ 12V/3A adaptör yeterli ✓
```

### 4.3 Termal Kayıp (Regülatör Bazlı)

| Regülatör | Vin | Vout | Iout(tip) | P_dissipation | Paket θJA | ΔT |
|-----------|-----|------|-----------|---------------|-----------|-----|
| MP2315 | 12V | 5V | 1.5A | 1.05W (η=90%) | 45°C/W | 47°C |
| SY8088 | 5V | 0.9V | 1.5A | 0.68W (η=90%) | 120°C/W | 82°C ⚠️ |
| MP8759 | 5V | 1.1V | 1.2A | 0.52W (η=90%) | 40°C/W | 21°C |
| RT9193 | 3.3V | 1.8V | 0.25A | 0.38W (LDO) | 220°C/W | 83°C ⚠️ |
| AP2112K(a) | 5V | 3.3V | 0.55A | 0.94W (LDO) | 250°C/W | 234°C ❌ |
| AP2112K(b) | 5V | 3.3V | 0.35A | 0.60W (LDO) | 250°C/W | 149°C ❌ |
| LNBH26 | 12V | 18V | 0.20A | 0.40W (boost) | 35°C/W | 14°C |

### ⚠️ KRİTİK TASARIM NOTU - 3.3V LDO SORUNU

**AP2112K (SOT-23-5) 3.3V LDO termal olarak yetmez!**

5V → 3.3V = 1.7V düşüm × 0.55A = 0.94W kayıp
SOT-23-5 pakette θJA = 250°C/W → Junction sıcaklığı aşırı yükselir.

**ÇÖZÜM SEÇENEKLERİ:**

1. **3.3V için de Buck Converter kullan (ÖNERİLEN)**
   - MP2315 ikinci adet (12V → 3.3V, 2A)
   - VEYA: MP1584 (5V → 3.3V, 3A, SOT-23-8)
   - Verim: %90+ → minimal ısınma

2. **Daha büyük paketli LDO**
   - AMS1117-3.3 (SOT-223): θJA = 90°C/W → ΔT = 84°C (hala sıcak)
   - AP7361C-33E (SOT-89): 1A, θJA = 120°C/W

3. **Yük dağılımı**
   - Ana 3.3V: Buck converter
   - RF 3.3V: LDO (düşük gürültü için, düşük akım)

**→ KARAR: Ana 3.3V → MP1584 Buck, RF 3.3V → AP2112K LDO kalabilir**

---

## 5. GÜNCELLENMIŞ GÜÇ AĞACI (Düzeltilmiş)

```
12V DC (3A) ─── D2 (Schottky) ─── F1 (3A PPTC)
                │
                ├──► U11: MP2315 → 5V / 3A Buck
                │    ├── USB 3.0 VBUS (500mA, polyfuse)
                │    ├── USB 2.0 x2 VBUS (500mA each, polyfuse)
                │    ├── HDMI 5V (50mA, ferrit bead)
                │    │
                │    ├──► U15: SY8088 → 0.9V / 3A Buck [EN: 5V, 1st]
                │    │    └── S905X4 VDDCORE
                │    │
                │    ├──► U14: MP8759 → 1.1V / 2A Buck [EN: PG_0.9V, 2nd]
                │    │    ├── S905X4 VDDGPU, VDDNPU
                │    │    └── DDR4 VDDQ (x4 chip)
                │    │
                │    ├──► U13: RT9193 → 1.8V / 300mA LDO [EN: PG_1.1V, 3rd]
                │    │    ├── DDR4 VDD (x4 chip)
                │    │    ├── eMMC VCCQ
                │    │    └── S905X4 VDDIO_1.8V
                │    │
                │    └──► U12b: AP2112K → 3.3V_RF / 600mA LDO
                │         ├── DVB NIM VCC (300mA)
                │         └── RF bölüm (100mA)
                │
                ├──► U16: MP1584EN → 3.3V / 3A Buck  ★ YENİ (LDO yerine)
                │    ├── eMMC VCC (200mA)
                │    ├── RTL8822CS WiFi/BT VDD (300mA)
                │    ├── RTL8211F AVDD33/DVDDIO (100mA)
                │    ├── TSOP38238 VCC (5mA)
                │    ├── INMP441 VDD x2 (3mA)
                │    ├── SSD1306 VCC (20mA)
                │    ├── I2C pull-ups, LED, GPIO (30mA)
                │    └── Toplam: ~660mA tipik
                │
                └──► U4: LNBH26 → 13V/18V / 500mA [EN: I2C, SoC boot sonrası]
                     └── LNB (F-type konnektör, 75Ω)
```

---

## 6. BYPASS KAPASİTÖR DETAY HARİTASI

### Her regülatör için giriş/çıkış kapasitör seçimi:

| Regülatör | Cin | Cout | Bootstrap | Notlar |
|-----------|-----|------|-----------|--------|
| MP2315 (12V→5V) | 22µF/25V X7R + 100nF | 100µF/10V Polimer + 22µF/10V X7R + 100nF | 100nF BST cap | Cin ve Cout IC'ye en yakın |
| SY8088 (5V→0.9V) | 22µF/10V X7R + 100nF | 2x 22µF/6.3V X7R + 100nF | - | Via ile GND'ye |
| MP8759 (5V→1.1V) | 22µF/10V X7R + 100nF | 100µF/6.3V Polimer + 22µF/6.3V X7R | 100nF BOOT cap | PGND ayrı trace |
| MP1584 (12V→3.3V) | 22µF/25V X7R + 100nF | 100µF/10V Polimer + 22µF/10V X7R | 100nF BST cap | ★ Yeni eklenen |
| RT9193 (3.3V→1.8V) | 1µF/10V X7R | 1µF/10V X7R | 10nF BP cap | Düşük gürültü |
| AP2112K (5V→3.3V_RF) | 1µF/10V X7R | 1µF/10V X7R | - | RF bölüm, ayrı GND |

### SoC Bypass Kapasitör Yerleşim Kuralı:

```
SoC üst yüz (Top side):
  - SoC'un her kenarında minimum 2x 100nF 0402
  - Her güç pini grubuna 1x 100nF mümkün olan en yakın mesafede
  - Bulk kapasitörler (10µF 0805) SoC'dan max 5mm mesafede

SoC alt yüz (Bottom side, BGA altı):
  - Termal via dizisi (en az 16 via, 0.3mm drill)
  - Via-in-pad tasarım ile bypass kapasitörler alt yüzde
  - Her güç via grubuna 100nF 0402 alt yüzde yerleştir
```

---

## 7. GÜÇ NET LİSTESİ (Özet)

| Net Adı | Voltaj | Kaynak | Tüketiciler | Max Akım | Koruma |
|---------|--------|--------|-------------|----------|--------|
| VIN_12V | 12V | DC Jack | MP2315, MP1584, LNBH26 | 3A | PPTC + TVS + Schottky |
| VCC_5V | 5V | MP2315 | SY8088, MP8759, USB VBUS, HDMI, AP2112K | 3A | - |
| VCC_3V3 | 3.3V | MP1584 | eMMC, WiFi, ETH, IR, MIC, LED | 3A | - |
| VCC_3V3_RF | 3.3V | AP2112K | DVB NIM, RF frontend | 600mA | Ferrit bead izolasyon |
| VCC_1V8 | 1.8V | RT9193 | DDR4 VDD, eMMC VCCQ, SoC IO | 300mA | - |
| VCC_1V1 | 1.1V | MP8759 | SoC GPU/NPU, DDR4 VDDQ | 2A | - |
| VDDCORE_0V9 | 0.9V | SY8088 | SoC CPU Core | 3A | - |
| LNB_PWR | 13/18V | LNBH26 | LNB (F-connector) | 500mA | OCP (IC dahili) |
| USB3_VBUS | 5V | VCC_5V | USB 3.0 port | 500mA | 500mA polyfuse |
| USB2A_VBUS | 5V | VCC_5V | USB 2.0 port A | 500mA | 500mA polyfuse |
| USB2B_VBUS | 5V | VCC_5V | USB 2.0 port B | 500mA | 500mA polyfuse |
| HDMI_5V | 5V | VCC_5V | HDMI connector | 50mA | Ferrit bead |
