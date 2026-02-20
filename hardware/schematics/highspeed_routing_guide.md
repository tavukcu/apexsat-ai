# APEXSAT AI v1.0 - High-Speed Sinyal Routing Guide

## Tasarımcı: Halil Dinçer
## Tarih: 2026-02-20 | Revizyon: A

---

## 1. HIGH-SPEED SİNYAL ÖZETİ

| Arayüz | Hız | Sinyal Tipi | Empedans | Çift Sayısı |
|--------|-----|-------------|----------|-------------|
| HDMI 2.0b | 6 Gbps/lane | Diferansiyel (TMDS) | 100Ω diff | 4 çift |
| USB 3.0 | 5 Gbps | Diferansiyel (SuperSpeed) | 90Ω diff | 1 TX + 1 RX çifti |
| USB 2.0 | 480 Mbps | Diferansiyel | 90Ω diff | 3 çift (3 port) |
| Gigabit Ethernet (RGMII) | 125 MHz (250 Mbps) | Single-ended | 50Ω SE | 12 sinyal |
| SDIO (WiFi) | 208 MHz (SDR104) | Single-ended | 50Ω SE | 6 sinyal |
| eMMC 5.1 | 200 MHz (HS400) | Single-ended | 50Ω SE | 11 sinyal |

---

## 2. HDMI 2.0b ROUTING

### 2.1 Sinyal Tanımları

```
HDMI 2.0b (Type-A, 19-pin):

  TMDS Data Kanalları (diferansiyel):
    TMDS_D0_P / TMDS_D0_N  → Video/Audio Lane 0
    TMDS_D1_P / TMDS_D1_N  → Video/Audio Lane 1
    TMDS_D2_P / TMDS_D2_N  → Video/Audio Lane 2
    TMDS_CLK_P / TMDS_CLK_N → TMDS Clock

  Düşük hızlı sinyaller:
    SCL, SDA  → DDC (I2C) - EDID okuma (100kHz)
    CEC       → Consumer Electronics Control
    HPD       → Hot Plug Detect
    5V_HDMI   → HDMI +5V güç çıkışı
    GND       → Shield + sinyal GND
```

### 2.2 Empedans ve Trace Boyutları

```
TMDS Diferansiyel Çift (100Ω ±10%):

  L1 (Top), GND referans L2:
  ┌─────────────────────────────────┐
  │  Trace genişliği (W): 4.0 mil  │
  │  Trace aralığı (S):  5.5 mil   │
  │  Dielektrik (H):     8.0 mil   │
  │  εr: 4.2 (FR4)                 │
  │  Zdiff ≈ 100Ω                  │
  └─────────────────────────────────┘

  JLCPCB impedans hesaplayıcı ile doğrula!
```

### 2.3 Length Matching

```
HDMI TMDS Length Matching:

  Intra-pair (P-N arası):
    TMDS_Dx_P - TMDS_Dx_N: ±2 mil (±0.05mm) ★ Çok kritik

  Inter-pair (lane'ler arası):
    TMDS_D0 - TMDS_D1 - TMDS_D2: ±50 mil (±1.27mm)

  Clock - Data arası:
    TMDS_CLK - TMDS_Dx: ±50 mil (±1.27mm)

  Toplam trace uzunluğu:
    Minimum: 20mm (SoC → konnektör)
    Maksimum: 150mm (HDMI spec sınırı)
    Önerilen: 30-80mm
```

### 2.4 Routing Kuralları

```
HDMI Routing DOs ve DON'Ts:

  ✅ DO:
  - Diferansiyel çiftleri yan yana tut (constant spacing)
  - GND guard trace (isteğe bağlı, 100Ω diff ile)
  - Konnektörün GND pinlerini geniş copper ile GND plane'e bağla
  - ESD koruması (IP4791CZ12) TMDS hatlarına konnektöre yakın
  - AC coupling kapasitör GEREKMEZ (TMDS DC-coupled)

  ❌ DON'T:
  - Diferansiyel çift aralığını değiştirme (S sabit tut)
  - TMDS trace'leri GND plane split/kesintisinin üzerinden geçirme
  - 90° açıyla dönme (45° veya arc kullan)
  - Via kullanma (mümkünse 0 via, max 1 via çifti)
  - Diğer high-speed sinyallerin yanından geçirme (20 mil aralık)

  ESD Koruma Yerleşimi:
  ┌──────────┐      ┌──────────┐      ┌──────┐
  │  S905X4  │─────→│IP4791CZ12│─────→│ HDMI │
  │  SoC     │      │  ESD     │      │Konnek│
  └──────────┘      └──────────┘      └──────┘
                    ↑ Konnektöre yakın
                      (< 10mm)
```

### 2.5 HDMI Konnektör Footprint

```
HDMI Type-A pinout (arka görünüm):

  Pin 1 ─── TMDS Data2+
  Pin 2 ─── TMDS Data2 Shield
  Pin 3 ─── TMDS Data2-
  Pin 4 ─── TMDS Data1+
  Pin 5 ─── TMDS Data1 Shield
  Pin 6 ─── TMDS Data1-
  Pin 7 ─── TMDS Data0+
  Pin 8 ─── TMDS Data0 Shield
  Pin 9 ─── TMDS Data0-
  Pin 10 ── TMDS Clock+
  Pin 11 ── TMDS Clock Shield
  Pin 12 ── TMDS Clock-
  Pin 13 ── CEC
  Pin 14 ── Utility/NC (HDMI 1.3a)
  Pin 15 ── SCL (DDC)
  Pin 16 ── SDA (DDC)
  Pin 17 ── DDC/CEC Ground
  Pin 18 ── +5V Power
  Pin 19 ── Hot Plug Detect (HPD)

  Shield pinleri → Konnektör GND shell'ine + PCB GND'ye
  Pull-up dirençler:
    HPD: 10kΩ → 3.3V (pull-up, active high)
    SCL/SDA: 2.2kΩ → 5V_HDMI
    CEC: 27kΩ → 3.3V
```

---

## 3. USB 3.0 ROUTING

### 3.1 Sinyal Tanımları

```
USB 3.0 (SuperSpeed + USB 2.0):

  SuperSpeed (5 Gbps, diferansiyel):
    SSTX_P / SSTX_N  → SuperSpeed TX çifti
    SSRX_P / SSRX_N  → SuperSpeed RX çifti

  USB 2.0 (480 Mbps, diferansiyel):
    D+ / D-           → Hi-Speed data çifti

  Güç:
    VBUS              → 5V (500mA, polyfuse korumalı)
    GND

  Toplam: 2 diff çift (SS) + 1 diff çift (HS) + power
```

### 3.2 Empedans

```
USB 3.0 SuperSpeed (90Ω diferansiyel):

  L1 (Top), GND referans L2:
  ┌─────────────────────────────────┐
  │  Trace genişliği (W): 4.5 mil  │
  │  Trace aralığı (S):  5.0 mil   │
  │  Dielektrik (H):     8.0 mil   │
  │  Zdiff ≈ 90Ω                   │
  └─────────────────────────────────┘

USB 2.0 (90Ω diferansiyel):
  Aynı boyutlar kullanılabilir.
```

### 3.3 Length Matching

```
USB 3.0 Length Matching:

  SS TX çifti (intra-pair):
    SSTX_P - SSTX_N: ±2 mil (±0.05mm)

  SS RX çifti (intra-pair):
    SSRX_P - SSRX_N: ±2 mil (±0.05mm)

  TX-RX arası (inter-pair):
    Eşleme gerekmez (bağımsız yönler)

  USB 2.0 (intra-pair):
    D+ - D-: ±5 mil (±0.127mm)

  Toplam trace uzunluğu:
    Maksimum: 150mm (board üzerinde)
    Önerilen: 30-80mm
```

### 3.4 Routing Kuralları

```
USB 3.0 Routing:

  ✅ DO:
  - SS TX/RX çiftlerini birbirinden > 15 mil ayır
  - AC coupling kapasitörleri konnektöre yakın yerleştir
  - ESD koruması (IP4220CZ6) konnektöre < 5mm
  - VBUS'a polyfuse (500mA PTC) konnektöre yakın
  - Shield GND'yi PCB GND'ye birden fazla via ile bağla

  ❌ DON'T:
  - SS ve USB 2.0 çiftlerini paralel koşturma (> 20 mil)
  - Via stub bırakma (SS 5 Gbps hassas)
  - Power trace'leri sinyal çiftlerinin arasından geçirme

  AC Coupling Kapasitörleri (SS TX/RX):
  ┌──────────┐            ┌────┐    ┌──────┐
  │  S905X4  │──TX──[100nF]────│ESD │───│USB-A │
  │  USB3    │──RX──[100nF]────│    │───│ 3.0  │
  └──────────┘            └────┘    └──────┘

  100nF veya 200nF, 0402, konnektöre yakın
```

---

## 4. USB 2.0 ROUTING (3 Port)

### 4.1 Portlar

```
Port 1: USB 2.0 Type-A (J8a) - medya cihazları
Port 2: USB 2.0 Type-A (J8b) - çevre birimler
Port 3: USB Type-C (J9)      - debug/OTG

Her port için:
  D+ / D-: 90Ω diferansiyel
  VBUS: 5V, 500mA (polyfuse)
  ESD: IP4220CZ6 per port
```

### 4.2 Routing

```
USB 2.0 Routing:

  Empedans: 90Ω diferansiyel
  Trace: W=4.5 mil, S=5.0 mil
  Intra-pair: ±5 mil
  Max uzunluk: 200mm
  Via: Max 2 per sinyal (tercihen 0)

  Seri terminasyon gerekli DEĞİL
  (USB 2.0 PHY dahili terminasyon kullanır)
```

---

## 5. GIGABIT ETHERNET (RGMII) ROUTING

### 5.1 RTL8211F-CG Arayüz Sinyalleri

```
RGMII (Reduced Gigabit MII) - SoC ↔ RTL8211F:

  TX (SoC → PHY):
    TXD[0:3]    → 4 data (125MHz DDR = 250Mbps)
    TX_CLK      → TX clock (125MHz, SoC sürüyor)
    TX_EN       → TX enable

  RX (PHY → SoC):
    RXD[0:3]    → 4 data (125MHz DDR)
    RX_CLK      → RX clock (125MHz, PHY sürüyor)
    RX_DV       → RX data valid (+ RX_ERR in-band)

  Yönetim:
    MDC         → Management clock (2.5MHz)
    MDIO        → Management data (bidirectional)

  PHY → RJ45 (MDI):
    TRD0_P/N    → Pair A (diferansiyel, trafo ile)
    TRD1_P/N    → Pair B
    TRD2_P/N    → Pair C
    TRD3_P/N    → Pair D

  Toplam RGMII sinyal: 12 (tek yönlü) + 2 (MDIO)
```

### 5.2 RGMII Empedans ve Trace

```
RGMII sinyalleri (50Ω single-ended):

  L1 (Top), GND referans L2:
  ┌─────────────────────────────────┐
  │  Trace genişliği (W): 5.8 mil  │
  │  Dielektrik (H):     8.0 mil   │
  │  Z0 ≈ 50Ω                      │
  └─────────────────────────────────┘

MDI Diferansiyel Çiftler (100Ω, PHY → Magjack):
  ┌─────────────────────────────────┐
  │  Trace genişliği (W): 4.0 mil  │
  │  Trace aralığı (S):  5.5 mil   │
  │  Zdiff ≈ 100Ω                  │
  └─────────────────────────────────┘
```

### 5.3 RGMII Length Matching

```
RGMII TX grubu (SoC → PHY):
  TXD[0:3] + TX_EN kendi aralarında: ±50 mil (±1.27mm)
  TX_CLK → TXD[x] arası: ±100 mil (±2.54mm)
  (RGMII 2.0 internal delay kullanıyorsa daha rahat)

RGMII RX grubu (PHY → SoC):
  RXD[0:3] + RX_DV kendi aralarında: ±50 mil
  RX_CLK → RXD[x] arası: ±100 mil

MDI Çiftler (PHY → Magjack):
  Intra-pair: ±5 mil (±0.127mm)
  Inter-pair: ±100 mil (eşleme rahat)

Toplam RGMII trace uzunluğu:
  SoC → PHY: 15-40mm (kısa tut)
  PHY → RJ45: 15-30mm
```

### 5.4 RGMII Timing ve Delay

```
RGMII Timing sorunu ve çözümü:

  RGMII'de CLK ve DATA arasında 2ns setup/hold gerekir.
  Board trace gecikmesi bunu karşılamayabilir.

  Çözüm: RTL8211F dahili TX/RX delay kullan
  - TXDLY strap pin: HIGH → 2ns TX delay aktif
  - RXDLY strap pin: HIGH → 2ns RX delay aktif
  (netlist_connections.md'de strap pin konfigürasyonu mevcut)

  Bu sayede board üzerinde ekstra gecikme eklemeye GEREK YOK.
  Trace uzunluklarını eşlemek yeterli.
```

### 5.5 Seri Terminasyon Dirençleri

```
RGMII seri terminasyon:

  SoC TX çıkışlarında seri terminasyon:
    TXD[0:3] → 33Ω seri → PHY
    TX_CLK   → 33Ω seri → PHY
    TX_EN    → 33Ω seri → PHY

  PHY RX çıkışlarında:
    RXD[0:3] → 33Ω seri → SoC (PHY'de dahili olabilir)
    RX_CLK   → 33Ω seri → SoC

  Direnç yerleşimi: Kaynak IC'ye yakın (< 5mm)
  Paket: 0402, 33Ω ±5%

  NOT: Bazı tasarımlarda 49.9Ω kullanılır.
  RTL8211F datasheet'ini kontrol et.
```

### 5.6 25MHz Kristal

```
RTL8211F Kristal Osilatör (25MHz):

  Y1 (3225 paket) → PHY XI/XO pinleri

  ┌────────┐
  │ XI  XO │
  └─┬────┬─┘
    │    │
   [CL1] [CL2]   ← Yük kapasitörleri
    │    │
    GND  GND

  CL hesaplama:
    CL = 2 × (CLoad - Cstray)
    CLoad = 18pF (kristal datasheet)
    Cstray ≈ 3pF (PCB + IC pin)
    CL = 2 × (18 - 3) = 30pF → 2x 15pF seç

  Routing:
    - Kristal PHY'ye en yakın yere (< 5mm)
    - Trace'leri kısa tut (< 10mm)
    - GND guard trace ile çevrele
    - Diğer high-speed sinyallerden uzak tut
```

### 5.7 RJ45 Magjack Bağlantısı

```
RTL8211F → HR911105A (Magjack, entegre manyetik):

  PHY MDI Çıkışları → Magjack Trafo Girişleri:
    TRD0_P/N → Pin 1/2 (yeşil çift)
    TRD1_P/N → Pin 3/6 (turuncu çift)
    TRD2_P/N → Pin 4/5 (mavi çift)
    TRD3_P/N → Pin 7/8 (kahverengi çift)

  75Ω terminasyon: Magjack dahili
  Bob Smith terminasyon: Magjack dahili
  LED bağlantısı: Magjack LED pinleri → PHY LED çıkışları

  Routing:
    - Diferansiyel 100Ω, ±5 mil intra-pair
    - PHY → Magjack mesafe: < 30mm
    - 4 çifti birbirinden > 10 mil ayır
    - GND split YAPMA (EMI sorun)
```

---

## 6. SDIO (WiFi - RTL8822CS)

### 6.1 Sinyaller

```
SDIO 3.0 (SoC ↔ RTL8822CS):

  CLK     → SDIO Clock (208MHz max, SDR104)
  CMD     → Command/Response
  DAT[0:3]→ 4-bit Data
  (CD/WP yok - WiFi modülde gerekli değil)

  Empedans: 50Ω single-ended
  Trace: W=5.8 mil (aynı RGMII)
```

### 6.2 Routing

```
SDIO Routing Kuralları:

  CLK - DAT/CMD arası: ±100 mil (rahat)
  DAT[0:3] kendi aralarında: ±50 mil
  Max trace uzunluğu: 50mm
  Via: Max 1 per sinyal

  Seri terminasyon: 22Ω seri CLK hattında
    (ringing azaltmak için, opsiyonel)

  ┌──────────┐    22Ω    ┌──────────┐
  │  S905X4  │──CLK──[R]──│RTL8822CS │
  │  SDIO    │──CMD──────│  WiFi    │
  │          │──DAT0~3───│          │
  └──────────┘           └──────────┘
```

---

## 7. eMMC 5.1 (HS400)

### 7.1 Sinyaller

```
eMMC 5.1 HS400 (SoC ↔ KLMAG1JETD):

  CLK       → eMMC Clock (200MHz DDR = HS400)
  CMD       → Command/Response
  DAT[0:7]  → 8-bit Data
  DS        → Data Strobe (HS400 mode)
  RST_n     → Hardware Reset

  Empedans: 50Ω single-ended
```

### 7.2 Routing

```
eMMC HS400 Routing:

  DAT[0:7] kendi aralarında: ±50 mil
  CLK - DAT arası: ±100 mil
  DS - DAT arası: ±50 mil (HS400'de DS referans)
  Max trace uzunluğu: 30mm (kısa tut - 200MHz DDR)

  Seri terminasyon: 33Ω seri CLK hattında

  eMMC IC'yi SoC'a mümkün olduğunca YAKIN yerleştir (< 15mm)

  ┌──────────┐    33Ω    ┌──────────┐
  │  S905X4  │──CLK──[R]──│KLMAG1JET│
  │  eMMC IF │──CMD──────│  eMMC   │
  │          │──DAT0~7───│  32GB   │
  │          │──DS───────│         │
  └──────────┘           └──────────┘
```

---

## 8. GENEL HIGH-SPEED ROUTING KURALLARI

### 8.1 Dönüş Açıları

```
High-speed trace dönüşleri:

  ❌ 90° açı (köşe) → Empedans süreksizliği, yansıma
  ✅ 45° açı (chamfer) → Kabul edilebilir
  ✅ Arc (yay) dönüş → En iyi (HDMI, USB 3.0 için önerilir)

  DDR4:   45° yeterli
  HDMI:   Arc tercih, 45° kabul
  USB 3.0: Arc tercih, 45° kabul
  RGMII:  45° yeterli
```

### 8.2 Referans Düzlem Değişimi

```
Sinyal katman değiştirdiğinde (via ile):

  L1 → L3 geçişinde GND referans düzlemi değişir:
    L1: GND ref = L2
    L3: GND ref = L2 (aynı) ✅ → Sorun yok

  L1 → L5 geçişinde:
    L1: GND ref = L2
    L5: GND ref = L4 (Power) ❌ → Return path kopukluk

  Çözüm: Via geçişi yakınına GND via koy (return via)
    Mesafe: Return GND via < 0.5mm sinyal via'sından
```

### 8.3 Crosstalk Azaltma

```
Sinyal sınıfları arası minimum boşluk:

  DDR4 ↔ HDMI:      ≥ 40 mil (1mm)
  DDR4 ↔ USB 3.0:   ≥ 30 mil
  HDMI ↔ USB 3.0:   ≥ 30 mil
  USB 3.0 ↔ USB 2.0: ≥ 20 mil
  RGMII ↔ herhangi:  ≥ 20 mil
  Analog ↔ dijital:  ≥ 40 mil

  3W kuralı: Trace merkez-merkez mesafe ≥ 3 × trace genişliği
  5W kuralı (kritik): ≥ 5 × trace genişliği (DDR4, HDMI için)
```

### 8.4 Power Plane Geçişi

```
High-speed sinyaller ASLA power plane split üzerinden geçmemeli.

  Sorunlu durum:
  ─────────[5V]───┃───[3.3V]─────── L4 Power Plane
                   ┃ ← Split burada
  ═══════════════════════════════════ L3 Sinyal trace
  ↑ Bu sinyal split üzerinden geçer → return path kopukluk

  Çözüm:
  1. Power plane split'lerini sinyal routing alanlarından uzak tut
  2. GND plane (L2) bölme YAPMA (tam düz GND)
  3. Sinyalleri L1 veya L3'te route et (L2 GND referans)
```

---

## 9. HIGH-SPEED ROUTING CHECKLIST

```
HDMI 2.0b:
  □ TMDS 4 çift 100Ω diferansiyel ±10%
  □ Intra-pair eşleme ±2 mil
  □ Inter-pair eşleme ±50 mil
  □ ESD (IP4791CZ12) konnektöre < 10mm
  □ HPD, SCL/SDA pull-up dirençleri yerleştirildi
  □ Shield pinler GND'ye multiple via ile bağlı
  □ 0 via (tercihen) veya max 1 via çifti

USB 3.0:
  □ SS TX/RX çiftleri 90Ω diferansiyel ±10%
  □ Intra-pair eşleme ±2 mil
  □ AC coupling kapasitörleri (100nF) konnektöre yakın
  □ ESD (IP4220CZ6) konnektöre < 5mm
  □ VBUS polyfuse (500mA) yerleştirildi
  □ SS ve USB 2.0 çiftleri > 20 mil ayrık

USB 2.0:
  □ D+/D- çiftleri 90Ω diferansiyel
  □ Intra-pair eşleme ±5 mil
  □ Her port için ESD koruma
  □ Her port için VBUS polyfuse

Gigabit Ethernet:
  □ RGMII sinyalleri 50Ω single-ended
  □ TX grubu kendi arası ±50 mil, CLK ±100 mil
  □ RX grubu kendi arası ±50 mil, CLK ±100 mil
  □ Seri terminasyon dirençleri (33Ω) kaynak IC yakınında
  □ MDI çiftleri 100Ω diferansiyel, intra-pair ±5 mil
  □ 25MHz kristal PHY'ye < 5mm, yük kapasitörleri (15pF)
  □ RTL8211F strap pinleri doğru konfigüre (RGMII + delay)

WiFi SDIO:
  □ 50Ω single-ended trace
  □ CLK-DAT eşleme ±100 mil
  □ Anten trace: 50Ω microstrip veya u.FL konnektör

eMMC:
  □ 50Ω single-ended trace
  □ DAT0~7 eşleme ±50 mil
  □ eMMC chip SoC'a < 15mm
  □ CLK hattında 33Ω seri terminasyon

Genel:
  □ Tüm dönüşler 45° veya arc
  □ GND plane (L2) DDR4+HDMI+USB alanında kesintisiz
  □ Farklı sinyal sınıfları arası minimum boşluk sağlandı
  □ Via geçişlerinde return GND via eklendi
  □ Power plane split üzerinden sinyal geçmiyor
```

---

## 10. SİNYAL BÜTÜNLÜğÜ SİMÜLASYON ÖNERİLERİ

```
Simülasyon araçları:
  - KiCad + IBIS modeller (ücretsiz)
  - HyperLynx (profesyonel)
  - Saturn PCB Toolkit (empedans hesaplama, ücretsiz)
  - JLCPCB Impedance Calculator (web bazlı)

Öncelikli simülasyon sinyalleri:
  1. DDR4 DQ/DQS (3200 MT/s) → Eye diagram
  2. HDMI TMDS (6 Gbps) → S-parameter, IL < 4dB
  3. USB 3.0 SS (5 Gbps) → Eye mask compliance

IBIS model kaynakları:
  - Amlogic: OEM SDK ile (NDA)
  - Realtek RTL8211F: Realtek website
  - Samsung DDR4: Samsung IBIS portal
  - Nexperia IP4791CZ12: Nexperia.com
```
