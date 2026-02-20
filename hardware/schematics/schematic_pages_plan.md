# APEXSAT AI v1.0 - EasyEDA Pro Şematik Sayfa Planı

## Tasarımcı: Halil Dinçer
## Tarih: 2026-02-20 | Revizyon: A

---

## 1. ŞEMATIK ORGANIZASYON

```
Toplam Sayfa: 12 sayfa
Çerçeve: A3 yatay (420 x 297 mm)
Title Block: Sağ alt köşe (firma adı, revizyon, tarih, sayfa no)
Grid: 50 mil (1.27mm)
Wire: 10 mil genişlik
```

---

## 2. SAYFA LİSTESİ

| Sayfa | Başlık | İçerik | Karmaşıklık |
|-------|--------|--------|-------------|
| 1 | Cover & Block Diagram | Proje bilgisi, genel blok diyagram | Düşük |
| 2 | Power Input & Protection | DC jack, sigorta, TVS, ters polarite | Düşük |
| 3 | Power Regulators | Tüm buck/LDO regülatörler, sequencing | Yüksek |
| 4 | SoC - Amlogic S905X4 | SoC sembol, tüm pin bağlantıları | Yüksek |
| 5 | DDR4 Memory (x4) | 4x DDR4 chip, bypass, ZQ, VREF | Yüksek |
| 6 | eMMC + microSD | eMMC flash, microSD slot | Orta |
| 7 | HDMI + Audio Output | HDMI konnektör, ESD, TOSLINK, 3.5mm | Orta |
| 8 | USB Ports | USB 3.0, USB 2.0 x2, USB-C, ESD | Orta |
| 9 | Ethernet | RTL8211F PHY, RJ45 magjack, kristal | Orta |
| 10 | DVB-S2 + LNB | NIM modülü, LNBH26, F-type konnektör | Orta |
| 11 | WiFi/BT + SDIO | RTL8822CS, u.FL, anten matching | Orta |
| 12 | Peripherals | IR, mikrofon, LED, buton, fan, OLED | Düşük |

---

## 3. SAYFA DETAYLARI

### Sayfa 1: Cover & Block Diagram

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│            APEXSAT AI v1.0                               │
│            Akıllı DVB-S2 Uydu Alıcısı                   │
│            Şematik Tasarım                               │
│                                                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │         Basitleştirilmiş Blok Diyagram              │ │
│  │                                                     │ │
│  │  12V → [Güç] → 5V/3.3V/1.8V/1.1V/0.9V            │ │
│  │              ↓                                      │ │
│  │  [DVB-S2] → [SoC S905X4] → [HDMI]                 │ │
│  │              ↓   ↓   ↓                              │ │
│  │          [DDR4] [eMMC] [USB/ETH/WiFi]              │ │
│  │              ↓                                      │ │
│  │          [Audio] [IR] [LED]                         │ │
│  │                                                     │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                          │
│  Revizyon tablosu:                                       │
│  Rev A | 2026-02-20 | İlk tasarım | H.Dinçer           │
│                                                          │
│  [TITLE BLOCK]                                           │
└──────────────────────────────────────────────────────────┘
```

### Sayfa 2: Power Input & Protection

```
Bileşenler:
  - J12: DC Barrel Jack 5.5x2.1mm (12V giriş)
  - D2: SS54 Schottky (ters polarite)
  - F1: 3A PPTC Fuse (aşırı akım)
  - D_TVS: SMBJ15A (aşırı gerilim)
  - C_IN: 100µF + 10µF giriş kapasitörleri
  - Test noktaları: TP_12V, TP_GND

Net Labels:
  - VIN_12V (çıkış → Sayfa 3'e)
  - GND

Notlar:
  - Giriş koruma sırası: F1 → D_TVS → D2 → C_IN
  - LED (D3 kırmızı) ile güç göstergesi
```

### Sayfa 3: Power Regulators

```
Bileşenler:
  - U11: MP2315 (12V → 5V Buck)
  - U16: MP1584EN (12V → 3.3V Buck) ★
  - U15: SY8088 (5V → 0.9V Buck)
  - U14: MP8759 (5V → 1.1V Buck)
  - U13: RT9193 (3.3V → 1.8V LDO)
  - FB1: Ferrit Bead (3.3V → 3.3V_RF izolasyon) ★ AP2112K kaldırıldı
  - İlgili tüm inductor, kapasitör, feedback dirençler
  - PGOOD bağlantıları (sequencing zinciri)

Net Labels (Çıkış):
  - VCC_5V        → USB VBUS, SY8088, MP8759, HDMI
  - VCC_3V3       → Sayfa 6,7,8,9,11,12
  - VCC_3V3_RF    → Sayfa 10 (DVB)
  - VCC_1V8       → Sayfa 5 (DDR4), Sayfa 6 (eMMC)
  - VCC_1V1       → Sayfa 4 (SoC), Sayfa 5 (DDR4)
  - VDDCORE_0V9   → Sayfa 4 (SoC)
  - PG_0V9, PG_1V1 → Power sequencing sinyalleri

Layout:
  ┌──────────────────────────────────────────────┐
  │ VIN_12V ──┬──→ [MP2315] → VCC_5V            │
  │           │         ├──→ [SY8088] → 0.9V     │
  │           │         ├──→ [MP8759] → 1.1V     │
  │           │         ├──→ [FB]→ 3.3V_RF ★      │
  │           │         └──→ [RT9193] → 1.8V     │
  │           │                                   │
  │           └──→ [MP1584EN] → VCC_3V3 ★        │
  │                                               │
  │ PGOOD zinciri: 0.9V → 1.1V → 1.8V           │
  └──────────────────────────────────────────────┘

Test noktaları: TP_5V, TP_3V3, TP_1V8, TP_1V1, TP_0V9
```

### Sayfa 4: SoC - Amlogic S905X4

```
Bileşenler:
  - U1: S905X4-J (BGA-272 sembolü)
  - Bypass kapasitörleri (SoC çevresinde)

Sembol bölümleri (multi-part symbol):
  Part A: DDR4 Interface (DQ, DQS, Addr, Cmd, CK)
  Part B: HDMI + Display (TMDS, I2S)
  Part C: USB + Ethernet (USB3, USB2, RGMII)
  Part D: Storage (eMMC, SDIO)
  Part E: Peripheral (GPIO, I2C, SPI, UART, IR, PWM)
  Part F: Power (VDD, VDDQ, VDDCORE, VDDIO, GND)

Net Labels (SoC çıkışları):
  DDR4_*      → Sayfa 5
  HDMI_*      → Sayfa 7
  USB3_*, USB2_* → Sayfa 8
  RGMII_*     → Sayfa 9
  EMMC_*      → Sayfa 6
  SDIO_*      → Sayfa 11
  I2C_*, SPI_* → Sayfa 10, 12
  IR_IN       → Sayfa 12
  GPIO_*      → Sayfa 12

NOT: S905X4 sembolü çok büyük, multi-part olarak böl.
     EasyEDA Pro'da "Multi-Part Symbol" kullan.
```

### Sayfa 5: DDR4 Memory

```
Bileşenler:
  - U2: K4A8G165WC-BCWE (DDR4 Chip 0, Byte Lane 0)
  - U3: K4A8G165WC-BCWE (DDR4 Chip 1, Byte Lane 1)
  - U4: K4A8G165WC-BCWE (DDR4 Chip 2, Byte Lane 2)
  - U5: K4A8G165WC-BCWE (DDR4 Chip 3, Byte Lane 3)
  - R_ZQ x4: 240Ω ±1% (ZQ kalibrasyon)
  - R_VREF: 2x 10kΩ (VREFCA divider)
  - Bypass: 20x 100nF + 4x 10µF

Layout:
  ┌─────────────────────────────────────────────┐
  │  Fly-by bus (Addr/Cmd/CK)                   │
  │  ═══════════╦══════╦══════╦══════╗          │
  │             ║      ║      ║      ║          │
  │           ┌─╨─┐  ┌─╨─┐  ┌─╨─┐  ┌─╨─┐      │
  │  DQ[0:7]─│ U2 │  │ U3 │  │ U4 │  │ U5 │    │
  │  DQ[8:15]│    │  │    │  │    │  │    │    │
  │           └───┘  └───┘  └───┘  └───┘      │
  │  Byte 0   Byte 1  Byte 2  Byte 3          │
  │                                             │
  │  [Bypass caps alt kısımda detaylı]          │
  │  [ZQ dirençleri her chip'in yanında]        │
  │  [VREFCA divider sol üstte]                │
  └─────────────────────────────────────────────┘

Net Labels:
  DDR4_DQ[0:31]     ← Sayfa 4'ten
  DDR4_DQS[0:3]_P/N ← Sayfa 4'ten
  DDR4_A[0:16]      ← Sayfa 4'ten
  DDR4_CK_P/N       ← Sayfa 4'ten
  VCC_1V8 (VDD)     ← Sayfa 3'ten
  VCC_1V1 (VDDQ)    ← Sayfa 3'ten
```

### Sayfa 6: eMMC + microSD

```
Bileşenler:
  - U6_EMMC: KLMAG1JETD-B041 (eMMC 32GB)
  - J1: XKTF-003 (microSD slot)
  - Bypass kapasitörler
  - ESD koruması (opsiyonel)

Net Labels:
  EMMC_CLK, EMMC_CMD, EMMC_DAT[0:7], EMMC_DS, EMMC_RST
  SD_CLK, SD_CMD, SD_DAT[0:3], SD_CD
  VCC_3V3, VCC_1V8 (eMMC VCCQ)
```

### Sayfa 7: HDMI + Audio Output

```
Bileşenler:
  - J6: HDMI Type-A konnektör
  - U9: IP4791CZ12 (HDMI ESD)
  - R_HDMI: 2.2kΩ x4 (pull-up)
  - J10: 3.5mm TRRS Audio Jack
  - J11: TOSLINK optik konnektör
  - Ses çıkış filtre devreleri

Layout:
  Sol taraf: SoC HDMI sinyalleri girişi
  Orta: ESD koruma IC
  Sağ taraf: HDMI konnektör

  Alt kısım: Audio çıkışları (analog + dijital)
```

### Sayfa 8: USB Ports

```
Bileşenler:
  - J7: USB 3.0 Type-A
  - J8a, J8b: USB 2.0 Type-A x2
  - J9: USB Type-C (OTG/Debug)
  - U10a,b,c: IP4220CZ6 x3 (ESD)
  - F_USB1,2a,2b: 500mA polyfuse x3
  - AC coupling kapasitörler (USB 3.0)

Layout:
  Üst: USB 3.0 (SS + HS)
  Orta: USB 2.0 x2
  Alt: USB-C (CC dirençleri, OTG ID)
```

### Sayfa 9: Ethernet

```
Bileşenler:
  - U7: RTL8211F-CG (PHY)
  - J5: HR911105A (RJ45 Magjack)
  - Y1: 25MHz kristal + yük kapasitörleri
  - R_TERM: 33Ω x6 (RGMII terminasyon)
  - R_STRAP: Strap dirençleri (PHYAD, mode)
  - Bypass kapasitörler

Layout:
  Sol: SoC RGMII sinyalleri → Terminasyon dirençleri
  Orta: RTL8211F + kristal + bypass
  Sağ: MDI çiftleri → RJ45 Magjack

  Alt: Strap pin konfigürasyonu detayı
```

### Sayfa 10: DVB-S2 + LNB

```
Bileşenler:
  - M1: DVB-S2 NIM modülü (BSBE2-401A)
  - U4: LNBH26PQR (LNB power supply)
  - J2: F-Type LNB IN
  - J3: F-Type LNB OUT (loop)
  - L1: 4.7µH RF choke
  - FB1: Ferrit bead (RF izolasyon)
  - Bypass kapasitörler (RF grade)

Layout:
  Sol: SoC I2C/TS sinyalleri
  Orta: NIM modülü + LNBH26
  Sağ: F-Type konnektörler

  RF bölge sınırı çizgisi ile göster
```

### Sayfa 11: WiFi/BT + SDIO

```
Bileşenler:
  - U8: RTL8822CS (WiFi/BT IC)
  - J4a, J4b: u.FL anten konnektörleri
  - Kristal osilatör (WiFi)
  - RF matching network (opsiyonel)
  - Bypass kapasitörler

Layout:
  Sol: SoC SDIO + UART sinyalleri
  Orta: RTL8822CS + bypass
  Sağ: u.FL konnektörler

  RF bölge notu: "Bu bölge RF - GND plane bütünlüğü koru"
```

### Sayfa 12: Peripherals

```
Bileşenler:
  - U18: TSOP38238 (IR alıcı)
  - D1: IR LED + Q2 (IR blaster)
  - U17a, U17b: MSM261S4030H0R (MEMS mikrofon x2)
  - D3-D6: LED'ler + R_LED (akım sınırlama)
  - SW1: Reset butonu + debounce RC
  - SW2: Power butonu + debounce RC
  - Q1: AO3400A (fan MOSFET) + fan header
  - DISP1_HDR: 4-pin I2C header (OLED)
  - UART debug header (4-pin)
  - JTAG/SWD debug header (opsiyonel)

Layout:
  Sol üst: IR alıcı + blaster
  Sağ üst: Mikrofon devresi
  Sol alt: LED'ler + butonlar
  Sağ alt: Fan kontrolü + debug headerlar
```

---

## 4. NET LABEL KURALLARI

### 4.1 İsimlendirme Konvansiyonu

```
Güç netleri (kalın, kırmızı):
  VIN_12V       → 12V giriş
  VCC_5V        → 5V ana rail
  VCC_3V3       → 3.3V dijital
  VCC_3V3_RF    → 3.3V RF izole
  VCC_1V8       → 1.8V DDR VDD
  VCC_1V1       → 1.1V GPU/VDDQ
  VDDCORE_0V9   → 0.9V CPU core
  GND           → Ana toprak
  AGND          → Analog toprak (RF bölge)

Sinyal netleri (siyah, normal):
  Prefix_Sinyal şeklinde:
  DDR4_DQ0, DDR4_DQ1, ..., DDR4_DQ31
  DDR4_DQS0_P, DDR4_DQS0_N
  DDR4_A0, DDR4_A1, ..., DDR4_A16
  DDR4_CK_P, DDR4_CK_N
  HDMI_TMDS_D0_P, HDMI_TMDS_D0_N
  USB3_SSTX_P, USB3_SSTX_N
  USB3_SSRX_P, USB3_SSRX_N
  USB2A_DP, USB2A_DN
  RGMII_TXD0, ..., RGMII_TXD3
  RGMII_TX_CLK, RGMII_TX_EN
  RGMII_RXD0, ..., RGMII_RXD3
  EMMC_CLK, EMMC_CMD, EMMC_DAT0, ...
  SDIO_CLK, SDIO_CMD, SDIO_DAT0, ...
  I2C0_SCL, I2C0_SDA
  SPI0_CLK, SPI0_MOSI, SPI0_MISO, SPI0_CS
  UART0_TX, UART0_RX
  IR_IN
  MIC_I2S_SCK, MIC_I2S_WS, MIC_I2S_SD
```

### 4.2 Bus Notation

```
EasyEDA Pro'da bus gösterimi:

  DDR4_DQ[0:31]    → 32-bit data bus
  DDR4_A[0:16]     → 17-bit address bus
  EMMC_DAT[0:7]    → 8-bit eMMC data
  RGMII_TXD[0:3]   → 4-bit TX data

  Bus wire: Kalın mavi çizgi
  Bus entry: 45° açıyla ayrılma
```

### 4.3 Sayfalar Arası Bağlantı

```
EasyEDA Pro "Off-Sheet Connector" kullanımı:

  Sayfa 3 → Sayfa 4 (güç):
    ▶ VCC_5V
    ▶ VCC_3V3
    ▶ VCC_1V8
    ▶ VCC_1V1
    ▶ VDDCORE_0V9
    ▶ GND

  Sayfa 4 → Sayfa 5 (DDR4):
    ▶ DDR4_DQ[0:31]
    ▶ DDR4_DQS[0:3]_P/N
    ▶ DDR4_A[0:16]
    ▶ DDR4_CK_P/N
    ▶ DDR4_CS[0:3]_N
    ...

Her sayfanın sol kenarında: Gelen sinyaller (off-sheet input)
Her sayfanın sağ kenarında: Giden sinyaller (off-sheet output)
```

---

## 5. EasyEDA Pro SEMBOL LİSTESİ

### 5.1 Mevcut LCSC Semboller (Otomatik)

```
LCSC parça numarası ile EasyEDA Pro otomatik sembol yükler:

  C45889  → MP2315GJ-Z sembol + footprint
  C15051  → MP1584EN-LF-Z sembol + footprint
  C79313  → SY8088AAC sembol + footprint
  C27416  → RT9193-18GB sembol + footprint
  C1015   → GZ2012D601TF ferrit bead (RF 3.3V izolasyon)
  # AP2112K kaldırıldı (termal analiz sonucu)
  C187932 → RTL8211F-CG sembol + footprint
  C111944 → IP4220CZ6 sembol + footprint
  C131394 → 100nF 0402 sembol + footprint
  ... (tüm LCSC parçalar)
```

### 5.2 Manuel Oluşturulacak Semboller

```
LCSC'de olmayan parçalar için manuel sembol gerekli:

  1. S905X4-J (BGA-272)
     - Multi-part sembol (6 bölüm)
     - Pin sayısı: ~272
     - Referans: Amlogic OEM datasheet
     - Footprint: BGA-272, 0.65mm pitch

  2. K4A8G165WC-BCWE (DDR4 FBGA-96)
     - Standart DDR4 x8 sembol
     - Footprint: FBGA-96, 0.8mm pitch

  3. KLMAG1JETD-B041 (eMMC FBGA-153)
     - Standart eMMC sembol
     - Footprint: FBGA-153, 0.5mm pitch

  4. BSBE2-401A (DVB NIM)
     - Konnektör/modül sembolü
     - Pin header footprint (NIM socket)

  5. LNBH26PQR (QFN-24)
     - ST datasheet'ten pin map
     - Footprint: QFN-24, 4x4mm

  6. MSM261S4030H0R (MEMS Mic)
     - LGA sembol
     - Footprint: 3.35x2.5mm LGA
```

---

## 6. TASARIM KURALLARI

### 6.1 Şematik Stilleri

```
Wire renkleri:
  - Güç (VCC): Kırmızı, kalın (20 mil)
  - GND: Siyah, kalın (20 mil)
  - Sinyal: Yeşil, normal (10 mil)
  - Bus: Mavi, kalın (15 mil)
  - Not-connected: Gri, X işareti

Bileşen yönelimi:
  - IC'ler: Giriş sol, çıkış sağ
  - Pasifler: Yatay (mümkünse)
  - Konnektörler: Sayfa kenarına yakın

Referans designator:
  U  = IC (entegre devre)
  R  = Direnç
  C  = Kapasitör
  L  = İndüktör
  D  = Diyot / LED
  Q  = Transistör / MOSFET
  J  = Konnektör
  SW = Switch / Buton
  F  = Sigorta
  Y  = Kristal
  M  = Modül
  FB = Ferrit bead
  TP = Test noktası
  HS = Heatsink
```

### 6.2 Not Kutuları

```
Her sayfada bulunması gereken notlar:

  1. Sayfa başlığı ve açıklama
  2. Kritik bileşen değerleri (tolerans, voltaj rating)
  3. Assembly varyantları (DNP notları)
  4. Referans doküman (ilgili routing guide sayfası)
  5. Revizyon notu

Örnek not kutusu:
  ┌──────────────────────────────────┐
  │ NOT:                             │
  │ 1. Tüm kapasitörler X7R, 0402   │
  │ 2. R_FB değerleri power_tree.md  │
  │    hesaplamalarına göre          │
  │ 3. PGOOD zinciri: U15→U14→U13   │
  │ 4. DNP: D1 (IR LED, opsiyonel)  │
  └──────────────────────────────────┘
```

---

## 7. EASYEDA PRO İŞ AKIŞI

```
Adım 1: Proje oluştur
  - EasyEDA Pro → New Project → "APEXSAT_AI_v1.0"
  - 12 şematik sayfası ekle

Adım 2: LCSC parçalarını içe aktar
  - Her LCSC parça numarasını ara ve yerleştir
  - Sembol + footprint otomatik yüklenir

Adım 3: Manuel semboller oluştur
  - S905X4, DDR4, eMMC, NIM, LNBH26 için
  - Multi-part symbol (SoC için)

Adım 4: Şematik çizimi (sayfa sırasıyla)
  - Sayfa 2 → 3 → 4 → 5 → ... → 12
  - Her sayfa sonrası ERC (Electrical Rule Check)

Adım 5: Net label doğrulama
  - Sayfalar arası net label eşleşme kontrolü
  - Bağlantısız pin kontrolü

Adım 6: BOM oluştur
  - EasyEDA Pro → BOM → Export CSV
  - jlcpcb_component_list.csv ile karşılaştır

Adım 7: Netlist export
  - EasyEDA Pro → Netlist → Export
  - PCB layout'a geçiş için

Adım 8: PCB'ye geçiş
  - Şematik → "Convert to PCB"
  - Board outline: 150x100mm
  - Layer stackup: 6-layer ayarla
```
