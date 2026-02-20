# APEXSAT AI v1.0 - DDR4 Routing Guide

## Tasarımcı: Halil Dinçer
## Tarih: 2026-02-20 | Revizyon: A

---

## 1. DDR4 KONFIGÜRASYONU

```
SoC: Amlogic S905X4-J (BGA-272)
DDR4: 4x K4A8G165WC-BCWE (FBGA-96, x8 her biri)
Toplam: 4GB (4x 512MB x8), 32-bit bus
Hız: DDR4-2400 / DDR4-3200 (1200/1600 MHz clock)
Topoloji: Fly-by (T-branch YASAK)
VDD: 1.8V (RT9193)
VDDQ: 1.1V (MP8759)
Vref: VDDQ/2 = 0.55V (dahili)
```

---

## 2. DDR4 SİNYAL GRUPLARI

### 2.1 Data Bus (32-bit, 4 Byte Lane)

```
BYTE LANE 0 (U2 - DDR4 Chip 0):
  DQ[0:7]   → 8 data sinyali
  DQS0_P/N  → Diferansiyel strobe (100Ω)
  DM0/DBI0  → Data mask / bus inversion

BYTE LANE 1 (U3 - DDR4 Chip 1):
  DQ[8:15]  → 8 data sinyali
  DQS1_P/N  → Diferansiyel strobe (100Ω)
  DM1/DBI1  → Data mask / bus inversion

BYTE LANE 2 (U4 - DDR4 Chip 2):
  DQ[16:23] → 8 data sinyali
  DQS2_P/N  → Diferansiyel strobe (100Ω)
  DM2/DBI2  → Data mask / bus inversion

BYTE LANE 3 (U5 - DDR4 Chip 3):
  DQ[24:31] → 8 data sinyali
  DQS3_P/N  → Diferansiyel strobe (100Ω)
  DM3/DBI3  → Data mask / bus inversion
```

### 2.2 Address/Command Bus (Fly-by Topology)

```
Adres:    A[0:16]     → 17 sinyal (fly-by, sıralı)
Bank:     BA[0:1]     → 2 sinyal
Bank Grp: BG[0]       → 1 sinyal (x8 config)
RAS/CAS:  RAS_n, CAS_n, WE_n → 3 sinyal (veya CA bus)
Chip Sel: CS0_n ~ CS3_n → 4 sinyal (her chip'e 1)
Clock:    CK_P/CK_N   → 1 diferansiyel çift (100Ω)
CKE:      CKE[0:3]    → 4 sinyal
ODT:      ODT[0:3]    → 4 sinyal
RESET:    RESET_n      → 1 sinyal
```

### 2.3 Güç Sinyalleri

```
VDD     → 1.8V (RT9193 çıkışı, her chip'e ayrı bypass)
VDDQ    → 1.1V (MP8759 çıkışı, her byte lane'e ayrı bypass)
VREFCA  → VDD/2 = 0.9V (voltage divider)
VREFDQ  → Dahili (DDR4 internal Vref)
VSS/VSSQ → GND
```

---

## 3. EMPEDANS KONTROL

### 3.1 Hedef Empedanslar

| Sinyal Tipi | Topoloji | Hedef Empedans | Tolerans |
|-------------|----------|----------------|----------|
| DQ[0:31] | Single-ended | 40Ω | ±10% |
| DQS_P/N | Diferansiyel | 80Ω (diferansiyel) | ±10% |
| Address/Command | Single-ended | 40Ω | ±10% |
| CK_P/CK_N | Diferansiyel | 80Ω (diferansiyel) | ±10% |
| CLK (tek uçlu ref) | Single-ended | 40Ω | ±10% |

### 3.2 Trace Genişlikleri (6-Layer Stackup, FR4)

```
6-Katman Stackup (JLCPCB JLC06161H-1080):
  L1: Signal (Top)       - 0.035mm Cu
  PP: Prepreg 1080       - 0.2mm
  L2: GND Plane          - 0.035mm Cu
  Core:                  - 0.5mm
  L3: Signal (Inner 1)   - 0.035mm Cu
  PP: Prepreg 1080       - 0.2mm
  L4: Power Plane        - 0.035mm Cu
  Core:                  - 0.5mm
  L5: Signal (Inner 2)   - 0.035mm Cu
  PP: Prepreg 1080       - 0.2mm
  L6: Signal (Bottom)    - 0.035mm Cu

DDR4 Single-ended (40Ω, L1 üstü, L2 GND referans):
  - Trace genişliği: 5.0 mil (0.127mm)
  - Dielektrik kalınlığı: ~8 mil (0.2mm)
  - Hesaplanan Z0 ≈ 40Ω (εr=4.2)

DDR4 Diferansiyel (80Ω, L1 üstü):
  - Trace genişliği: 4.5 mil (0.114mm)
  - Trace aralığı: 5.0 mil (0.127mm)
  - Hesaplanan Zdiff ≈ 80Ω

NOT: Kesin değerler JLCPCB impedans hesaplayıcısı ile doğrulanmalı
     https://jlcpcb.com/pcb-impedance-calculator
```

---

## 4. DDR4 FLY-BY TOPOLOJİSİ

### 4.1 Address/Command Routing Sırası

```
Fly-by topoloji: SoC → U2 → U3 → U4 → U5 (seri bağlantı)

                                 Fly-by Bus
SoC ──────┬──────────┬──────────┬──────────┐
          │          │          │          │
         U2         U3         U4         U5
       Chip 0     Chip 1     Chip 2     Chip 3
      (Byte 0)   (Byte 1)   (Byte 2)   (Byte 3)

Adres/Komut sinyalleri chip'lere SIRAYLA ulaşır.
Her chip arasındaki mesafe eşit olmalı (~5-8mm).

CK (Clock) de fly-by ile gider:
  SoC CK_P/N → U2 CK → U3 CK → U4 CK → U5 CK

Bu gecikmeyi DDR4 controller "write leveling" ile telafi eder.
```

### 4.2 Data Bus (Point-to-Point)

```
Data sinyalleri NOKTADAN NOKTAYA (P2P) bağlanır:

SoC DQ[0:7]  ←→ U2 DQ[0:7]   (sadece U2'ye)
SoC DQ[8:15] ←→ U3 DQ[0:7]   (sadece U3'e)
SoC DQ[16:23]←→ U4 DQ[0:7]   (sadece U4'e)
SoC DQ[24:31]←→ U5 DQ[0:7]   (sadece U5'e)

Her byte lane kendi chip'ine doğrudan bağlı.
T-branch veya multi-drop YASAK (data bus için).
```

---

## 5. LENGTH MATCHING KURALLARI

### 5.1 Data Grubu (Her Byte Lane İçinde)

```
┌──────────────────────────────────────────────────┐
│ BYTE LANE İÇİ EŞLEME (EN KRİTİK)               │
├──────────────────────────────────────────────────┤
│                                                  │
│ DQ[n] - DQS_P/N arası:  ±2 mil (±0.05mm)       │
│ DM - DQS_P/N arası:     ±2 mil (±0.05mm)       │
│                                                  │
│ Her DQ sinyali kendi byte lane'indeki            │
│ DQS'e göre eşlenir.                             │
│                                                  │
│ Byte lane'ler arası eşleme:                     │
│ DQS0 - DQS1 - DQS2 - DQS3: ±25 mil (±0.635mm) │
│                                                  │
└──────────────────────────────────────────────────┘

Hedef trace uzunlukları (SoC → DDR4 chip):
  - Minimum: 15mm (BGA fanout + routing)
  - Maksimum: 50mm (sinyal bütünlüğü sınırı)
  - Önerilen: 20-35mm
```

### 5.2 Address/Command Grubu (Fly-by)

```
┌──────────────────────────────────────────────────┐
│ ADRES/KOMUT FLY-BY EŞLEME                       │
├──────────────────────────────────────────────────┤
│                                                  │
│ A[0:16] kendi aralarında: ±5 mil (±0.127mm)     │
│ BA[0:1] kendi aralarında: ±5 mil                │
│ CS_n kendi aralarında:    ±5 mil                │
│                                                  │
│ CK_P/N diferansiyel:     ±1 mil (±0.025mm)     │
│ CK - CS/CKE/ODT arası:  ±10 mil (±0.254mm)    │
│                                                  │
│ Fly-by segmentler (chip-chip arası):            │
│ Her segment eşit: 5-8mm ±0.5mm                  │
│                                                  │
└──────────────────────────────────────────────────┘
```

### 5.3 Clock (CK_P/CK_N)

```
┌──────────────────────────────────────────────────┐
│ CLOCK ROUTING                                    │
├──────────────────────────────────────────────────┤
│                                                  │
│ CK_P - CK_N intra-pair:  ±1 mil (±0.025mm)     │
│ Diferansiyel empedans:    80Ω ±10%              │
│                                                  │
│ CK fly-by ile Address/Command ile aynı yoldan   │
│ gitmeli (paralel routing)                        │
│                                                  │
│ CK → Address gecikme farkı < 500ps              │
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 6. BGA FANOUT STRATEJİSİ

### 6.1 SoC S905X4 BGA-272 Fanout

```
BGA-272: ~17x16 ball matrix, 0.65mm pitch

Fanout stratejisi (dog-bone pattern):
  - Dış 2 sıra: L1 (Top) üzerinden doğrudan route
  - 3. ve 4. sıra: Via ile L3 (Inner 1) üzerinden route
  - Merkez pinler: Via ile L5/L6 üzerinden route
  - GND/Power pinler: Via ile L2/L4 düzlemlere

Via boyutları (BGA fanout):
  - Via drill: 0.2mm (8 mil) - JLCPCB minimum
  - Via pad: 0.4mm (16 mil)
  - Via-to-via mesafe: 0.65mm (pitch ile uyumlu)

  ┌─────────────────────────────┐
  │ · · · · · · · · · · · · · · │ ← Dış sıra (L1 route)
  │ · · · · · · · · · · · · · · │ ← 2. sıra (L1 route)
  │ · · ○ ○ ○ ○ ○ ○ ○ ○ · · · │ ← 3. sıra (via → L3)
  │ · · ○               ○ · · │ ← 4+ sıra (via → L5)
  │ · · ○    GND/PWR    ○ · · │ ← Merkez (via → plane)
  │ · · ○               ○ · · │
  │ · · ○ ○ ○ ○ ○ ○ ○ ○ · · · │
  │ · · · · · · · · · · · · · · │
  │ · · · · · · · · · · · · · · │
  └─────────────────────────────┘

  · = L1 routing
  ○ = Via + inner layer routing
```

### 6.2 DDR4 FBGA-96 Fanout

```
FBGA-96: 10x10 ball matrix (köşeler boş), 0.8mm pitch

DDR4 chip daha rahat fanout (0.8mm > 0.65mm):
  - Dış 2 sıra: L1/L6 doğrudan route
  - İç pinler: Via ile iç katmanlar
  - GND/VDD: Termal via ile GND/Power düzlemlere

Her DDR4 chip'in altına:
  - Minimum 4x 100nF bypass (VDD, VDDQ)
  - Via ile GND düzleme bağlantı
  - Bypass kapasitörler alt yüze (L6) yerleştir
```

---

## 7. ROUTING KURALLARI

### 7.1 Trace Aralıkları

```
DDR4 sinyaller arası minimum boşluk:

  DQ-DQ aralığı (aynı byte):    >= 4 mil (0.1mm)
  DQ-DQ aralığı (farklı byte):  >= 8 mil (0.2mm) ★
  DQS-DQ aralığı:               >= 5 mil (0.127mm)
  Addr/Cmd arası:                >= 4 mil (0.1mm)
  CK_P-CK_N aralığı:            5.0 mil (sabit, empedans için)
  DQS_P-DQS_N aralığı:          5.0 mil (sabit)

  DDR4 - diğer sinyal arası:    >= 20 mil (0.5mm) ★★
  DDR4 - güç trace arası:       >= 15 mil (0.38mm)
```

### 7.2 Via Kullanım Kuralları

```
DDR4 sinyallerinde via kullanımı:
  - Data bus (DQ): Maksimum 1 via per sinyal (tercihen 0)
  - DQS: Maksimum 1 via
  - Address/Command: Maksimum 2 via per sinyal
  - Clock (CK): 0 via (mümkünse), en fazla 1 via

Via kapasitansı tahmini: ~0.5pF per via
  - 3200MHz'de bu tolere edilebilir ama minimize et

Via stub (kullanılmayan via kısmı):
  - Back-drill gerekli DEĞİL (DDR4-3200 için)
  - Ancak L3'e route ediyorsan, L6'ya stub kalır (~0.7mm)
  - DDR4-3200'de kabul edilebilir, DDR4-4800+ için back-drill gerekir
```

### 7.3 Layer Tercihleri

```
DDR4 sinyalleri için katman tercihi:

  1. Tercih (en iyi):
     - L1 (Top): Data + Address (GND referans L2 ile)

  2. Alternatif:
     - L3 (Inner 1): Taşan data sinyalleri (GND ref: L2)

  3. Alt yüz:
     - L6 (Bottom): Bypass kapasitörler, kısa bağlantılar

  ASLA:
     - L4 (Power plane) üzerinden DDR4 sinyali geçirme
     - L2 (GND plane) kesme/split yapma (DDR4 altında)

  GND Plane bütünlüğü:
     - DDR4 bölgesinde L2 GND düzlemi KESİLMEMELİ
     - GND via'ları ile dönüş yolu sağla
     - Her 5 sinyal via'sına 1 GND via ekle
```

---

## 8. TERMINASYON

### 8.1 On-Die Termination (ODT)

```
DDR4 dahili ODT kullanır (harici terminasyon direnci GEREKMEZ):

  Data (DQ) ODT:
    - Write: RTT_NOM = 120Ω (veya 240Ω)
    - Read: RTT_WR = RZQ/1 = 240Ω
    - DDR4 controller MRS register ile ayarlanır

  Address/Command:
    - Harici terminasyon gerekli DEĞİL (fly-by)
    - Son chip (U5) sonunda ~39Ω pull-up to VDD/2 (opsiyonel)

  Clock (CK):
    - Son chip'te dahili ODT yeterli
```

### 8.2 Seri Terminasyon (Opsiyonel)

```
SoC çıkışında seri terminasyon (source termination):
  - Genellikle DDR4 için GEREKMEZ (on-die driver impedance match)
  - Amlogic S905X4 DDR4 I/O: Kalibre edilebilir çıkış empedansı
  - MRS komutu ile ZQ kalibrasyon otomatik yapılır

Eğer kullanılacaksa:
  - Rs = Z0 - Rout = 40 - 34 = 6Ω → 0Ω (kullanma)
```

---

## 9. BYPASS KAPASİTÖR YERLEŞİMİ

```
Her DDR4 chip için minimum bypass:

  ┌──────────────────────────────┐
  │         DDR4 Chip            │
  │         (TOP side)           │
  │                              │
  │   VDD ●──── VDDQ ●         │
  └──────────┬───────────────────┘
             │ (via to bottom)
  ┌──────────┴───────────────────┐
  │    (BOTTOM side - bypass)    │
  │                              │
  │  [100nF] [100nF] [100nF]    │ ← VDD bypass (3x 100nF)
  │  [100nF] [100nF]            │ ← VDDQ bypass (2x 100nF)
  │  [10µF]                     │ ← Bulk kapasitör (1x 10µF)
  │                              │
  └──────────────────────────────┘

Toplam bypass per chip: 5x 100nF + 1x 10µF
4 chip için: 20x 100nF + 4x 10µF = 24 kapasitör

Yerleşim kuralı:
  - Bypass kapasitör: Chip'e MAX 2mm mesafe
  - GND via: Her bypass'ın yanında (< 0.5mm)
  - Bulk (10µF): Chip'e MAX 5mm mesafe
```

---

## 10. DDR4 ROUTING CHECKLIST

```
□ Tüm DQ sinyalleri kendi byte lane'indeki DQS'e ±2 mil eşlendi
□ DM sinyali kendi DQS'ine ±2 mil eşlendi
□ Byte lane'ler arası DQS eşleme ±25 mil
□ CK_P/CK_N intra-pair ±1 mil
□ Address/Command kendi aralarında ±5 mil
□ Fly-by segmentleri eşit (±0.5mm)
□ Single-ended empedans 40Ω ±10%
□ Diferansiyel empedans 80Ω ±10%
□ DDR4 bölgesinde GND plane bütünlüğü korundu
□ DQ trace'ler arası minimum 4 mil aralık
□ DDR4 - diğer sinyal arası minimum 20 mil
□ Her DDR4 chip'e 5x 100nF + 1x 10µF bypass yerleştirildi
□ Via sayısı minimize edildi (DQ: max 1, Addr: max 2)
□ BGA fanout dog-bone pattern uygulandı
□ Power plane (L4) üzerinden DDR4 sinyal geçmiyor
□ VREFCA voltage divider (2x 10kΩ) VDD'ye yakın
□ ZQ kalibrasyon direnci (240Ω ±1%) ZQ pinine yakın
□ DDR4 alanı diğer high-speed sinyallerden izole
```

---

## 11. ZQ KALİBRASYON

```
Her DDR4 chip'in ZQ pinine:
  - 240Ω ±1% direnç → GND
  - Trace uzunluğu < 5mm
  - GND via en yakın yere

  ZQ ─── [240Ω ±1%] ─── GND

Bu direnç DDR4 output driver impedance kalibrasyonu için kritik.
%1 tolerans zorunlu (±5% impedans hatasına neden olur).
```

---

## 12. AMLOGIC S905X4 DDR4 PIN ATAMASI

```
NOT: Amlogic BGA pinout NDA altında olabilir.
     OEM SDK/reference design'dan doğrula.

Genel S905X4 DDR4 pin bölgeleri (BGA-272):
  - DDR4 Data: BGA'nın batı tarafı (sol kenar)
  - DDR4 Addr/Cmd: BGA'nın güneybatı tarafı
  - DDR4 Clock: Addr/Cmd grubuna yakın
  - DDR4 Power: Dağıtık + merkez GND

Chip yerleşim önerisi:
                      ┌─────────┐
     U2 (Byte 0) ←── │         │
     U3 (Byte 1) ←── │  S905X4 │
     U4 (Byte 2) ←── │  BGA    │
     U5 (Byte 3) ←── │         │
                      └─────────┘

     DDR4 chip'ler SoC'un DDR pinlerinin olduğu
     tarafa dizilir, fly-by sırasında.

     Chip arası mesafe: 5-8mm (eşit aralıklı)
     SoC → U2 mesafe: 8-12mm
```

---

## 13. YAYGIN HATALAR VE ÇÖZÜMLER

| Hata | Sonuç | Çözüm |
|------|-------|-------|
| T-branch data routing | Sinyal yansıması, hata | P2P routing kullan |
| GND plane kesintisi DDR altında | Return path kaybı, EMI | GND plane bütün tut |
| DQ-DQS eşleme > 5 mil | Timing window ihlali | Meander ile eşle |
| Farklı byte DQ'lar yakın | Crosstalk | 8 mil aralık |
| Via stub > 1mm | Sinyal rezonansı | Back-drill veya inner route |
| Bypass kapasitör uzak | Power integrity bozulması | < 2mm mesafe |
| 240Ω ZQ direnci %5 | Driver cal. hatası | %1 tolerans kullan |
| DDR4 trace power plane üstünde | Referans düzlem kaybı | GND ref. katman kullan |
