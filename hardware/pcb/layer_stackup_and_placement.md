# APEXSAT AI v1.0 - PCB Katman Stackup ve Yerleşim Rehberi

## Tasarımcı: Halil Dinçer
## Tarih: 2026-02-20 | Revizyon: A

---

## 1. PCB GENEL ÖZELLİKLER

```
Boyut:          150mm x 100mm (6" x 4")
Katman sayısı:  6
Malzeme:        FR4 (Tg150+)
Bakır kalınlık: 1 oz (35µm) tüm katmanlar
Yüzey kaplama:  ENIG (Electroless Nickel Immersion Gold)
Renk:           Siyah solder mask / Beyaz silkscreen
Min trace:      3.5 mil (0.09mm) - JLCPCB 6L minimum
Min spacing:    3.5 mil (0.09mm)
Min via drill:  0.2mm (8 mil)
Min via pad:    0.4mm (16 mil)
PCB kalınlık:   1.6mm (standart)
Empedans:       Kontrollü (JLCPCB impedance service)
```

---

## 2. 6-KATMAN STACKUP

### 2.1 JLCPCB JLC06161H-1080 Stackup

```
                    Kalınlık    Malzeme        Fonksiyon
  ┌───────────────┐
  │ Solder Mask   │  ~0.02mm   Yeşil/Siyah
  ├───────────────┤
  │ L1 - TOP      │  0.035mm   Cu (1oz)       Sinyal + Bileşen
  ├───────────────┤
  │ Prepreg 1080  │  0.075mm   FR4 (εr≈4.2)
  ├───────────────┤
  │ L2 - GND      │  0.035mm   Cu (1oz)       ★ GND Düzlemi
  ├───────────────┤
  │ Core          │  0.50mm    FR4
  ├───────────────┤
  │ L3 - SIG/PWR  │  0.035mm   Cu (1oz)       Sinyal + Power
  ├───────────────┤
  │ Prepreg 1080  │  0.20mm    FR4 (εr≈4.2)
  ├───────────────┤
  │ L4 - POWER    │  0.035mm   Cu (1oz)       ★ Power Düzlemi
  ├───────────────┤
  │ Core          │  0.50mm    FR4
  ├───────────────┤
  │ L5 - SIG      │  0.035mm   Cu (1oz)       Sinyal
  ├───────────────┤
  │ Prepreg 1080  │  0.075mm   FR4 (εr≈4.2)
  ├───────────────┤
  │ L6 - BOTTOM   │  0.035mm   Cu (1oz)       Sinyal + Bypass
  ├───────────────┤
  │ Solder Mask   │  ~0.02mm
  └───────────────┘

  Toplam kalınlık: ~1.6mm
```

### 2.2 Katman Görev Dağılımı

| Katman | Ad | Fonksiyon | İçerik |
|--------|----|-----------|--------|
| L1 | TOP | Sinyal + Bileşen | DDR4 data+addr, HDMI TMDS, USB SS, RGMII, SMD bileşenler |
| L2 | GND | Ground Plane | Kesintisiz GND düzlemi (★ KRİTİK - bölme yapma!) |
| L3 | SIG/PWR | İç sinyal + Güç | BGA fanout overflow, power trace, iç routing |
| L4 | POWER | Power Plane | VCC_5V, VCC_3V3, VCC_1V8, VCC_1V1, VDDCORE bölgeleri |
| L5 | SIG | İç sinyal | BGA iç pin routing, taşma sinyaller |
| L6 | BOTTOM | Sinyal + Bypass | Bypass kapasitörler (BGA altı), THT bileşen padleri |

### 2.3 Empedans Tablosu

```
JLCPCB'ye sipariş ederken belirtilecek empedans değerleri:

L1 (Top), GND referans (L2, 0.075mm prepreg):
┌─────────────────────────────────────────────────────────────┐
│ Single-ended 40Ω:  W = 5.0 mil (DDR4)                     │
│ Single-ended 50Ω:  W = 3.8 mil (RGMII, eMMC, SDIO)       │
│ Diff 80Ω:          W = 4.5 mil, S = 5.0 mil (DDR4 CLK/DQS)│
│ Diff 90Ω:          W = 4.0 mil, S = 5.5 mil (USB)         │
│ Diff 100Ω:         W = 3.5 mil, S = 6.0 mil (HDMI, ETH)  │
└─────────────────────────────────────────────────────────────┘

L3 (Inner 1), GND referans (L2, 0.5mm core):
┌─────────────────────────────────────────────────────────────┐
│ Single-ended 50Ω:  W = 8.5 mil                            │
│ (İç katman trace'ler daha geniş - dielektrik kalın)        │
└─────────────────────────────────────────────────────────────┘

L5 (Inner 2), Power referans (L4, 0.5mm core):
┌─────────────────────────────────────────────────────────────┐
│ Single-ended 50Ω:  W = 8.5 mil                            │
│ (Power plane referans - mümkünse sinyal geçirme)           │
└─────────────────────────────────────────────────────────────┘

L6 (Bottom), GND referans (L5, 0.075mm prepreg):
  Aynı L1 ile simetrik yapı.

★ JLCPCB empedans hesaplayıcısından kesin değerleri al!
  https://jlcpcb.com/pcb-impedance-calculator
```

---

## 3. POWER PLANE (L4) BÖLGELERİ

```
L4 Power Plane bölge haritası:

  ┌──────────────────────────────────────────────────────┐
  │                                                      │
  │  ┌────────────┐  ┌──────────────────────────────┐   │
  │  │            │  │                              │   │
  │  │  VCC_5V    │  │       VCC_3V3               │   │
  │  │  (sol)     │  │       (merkez + sağ)        │   │
  │  │            │  │                              │   │
  │  │  USB VBUS  │  │  eMMC, WiFi, ETH, LED,     │   │
  │  │  HDMI 5V   │  │  IR, Mikrofon, OLED        │   │
  │  │            │  │                              │   │
  │  └────────────┘  └──────────────────────────────┘   │
  │                                                      │
  │  ┌──────────┐  ┌──────────┐  ┌───────────────┐     │
  │  │VDDCORE   │  │ VCC_1V1  │  │   VCC_1V8     │     │
  │  │ 0.9V     │  │          │  │               │     │
  │  │(SoC alt) │  │(GPU+DDR) │  │  (DDR4 VDD)  │     │
  │  │          │  │          │  │               │     │
  │  └──────────┘  └──────────┘  └───────────────┘     │
  │                                                      │
  │  ┌──────────────────┐                                │
  │  │  VCC_3V3_RF      │  (izole RF bölge)             │
  │  │  DVB + LNB bölge │                                │
  │  └──────────────────┘                                │
  │                                                      │
  └──────────────────────────────────────────────────────┘

Bölgeler arası gap: 20 mil (0.5mm)
Her bölge kendi regülatöründen beslenir (star topology)
```

---

## 4. BİLEŞEN YERLEŞİM PLANI

### 4.1 Fonksiyonel Bölge Haritası (Top View)

```
150mm
┌──────────────────────────────────────────────────────────┐
│ ┌──────┐   ┌─────────────────────────┐   ┌────────┐    │
│ │DC Jack│   │      GÜÇ BÖLGESI       │   │ RJ45   │    │
│ │ 12V   │   │  MP2315  MP1584  RT9193 │   │Magjack │    │
│ └──────┘   │  SY8088  MP8759  AP2112K│   └────────┘    │ 100mm
│             └─────────────────────────┘   ┌────────┐    │
│ ┌───────┐                                │ETH PHY │    │
│ │F-Type │   ┌──────────────────┐         │RTL8211F│    │
│ │LNB IN │   │    SoC S905X4    │         └────────┘    │
│ └───────┘   │    (BGA-272)     │                       │
│ ┌───────┐   │                  │   ┌─────────────────┐ │
│ │F-Type │   └──────────────────┘   │  DDR4 x4        │ │
│ │LNB OUT│                          │  U2 U3 U4 U5    │ │
│ └───────┘   ┌──────┐              └─────────────────┘ │
│             │LNBH26│   ┌──────┐                       │
│ ┌───────┐   └──────┘   │eMMC  │   ┌──────┐           │
│ │DVB NIM│               └──────┘   │WiFi  │           │
│ │Modülü │                          │8822CS│           │
│ └───────┘                          └──────┘           │
│                                                        │
│ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌────┐ │
│ │HDMI  │ │USB3.0│ │USB2.0│ │USB2.0│ │USB-C │ │3.5mm│ │
│ │Type-A│ │Type-A│ │Type-A│ │Type-A│ │Debug │ │Jack │ │
│ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └────┘ │
│  ← ─ ─ ─ ─ ─ KONNEKTÖR KENARI (alt) ─ ─ ─ ─ ─ →    │
└──────────────────────────────────────────────────────────┘
  ↑ Sol kenar: RF konnektörler    Sağ kenar: Dijital ↑
```

### 4.2 Yerleşim Kuralları

```
1. SoC (U1) - MERKEZ:
   - PCB'nin ortasına yakın
   - DDR4 chip'ler SoC'un DDR pin tarafına
   - eMMC SoC'a < 15mm
   - Heatsink montaj alanı üstünde (25x25mm)

2. DDR4 (U2-U5) - SoC YANINDA:
   - Fly-by sırası ile dizili
   - SoC DDR pinlerine en yakın taraf
   - Chip arası 5-8mm eşit aralık
   - Bypass kapasitörler alt yüzde (L6)

3. GÜÇ REGÜLATÖRLERİ - ÜST KENAR:
   - 12V giriş noktasına yakın
   - Her regülatör kendi inductor ve kapasitörü ile birlikte
   - Termal pad/pour ile soğutma alanı
   - Güç yolları kısa ve geniş

4. RF BÖLGE - SOL KENAR:
   - F-Type konnektörler sol kenarda
   - DVB NIM, LNBH26 bu bölgede
   - GND plane kesintisi YOK (RF bütünlüğü)
   - 3.3V_RF ayrı besleme (AP2112K)
   - Dijital sinyallerden izole (> 5mm)

5. KONNEKTÖRLER - ALT KENAR:
   - HDMI, USB, Audio alt kenarda sıralı
   - Kullanıcı erişimi için board kenarında
   - THT konnektörler mekanik olarak güçlü

6. ETHERNET - SAĞ ÜST:
   - RJ45 magjack köşede (EMI izolasyon)
   - RTL8211F PHY magjack'e yakın (< 25mm)
   - 25MHz kristal PHY'ye < 5mm

7. WiFi - SAĞ ORTA:
   - u.FL konnektörler board kenarına yakın
   - Anten trace için GND clearance
   - RF bölge notu

8. PERIPHERAL - DAĞITIK:
   - IR alıcı: Board ön tarafında (görüş açısı)
   - LED'ler: Board kenarında görünür
   - Butonlar: Erişilebilir konumda
   - Mikrofon: SoC'a yakın, gürültü kaynaklarından uzak
```

### 4.3 Bileşen Yükseklik Sınırları

```
Top side (L1):
  - SoC + heatsink: max 15mm (heatsink dahil)
  - DDR4: 1.2mm (FBGA paketi)
  - eMMC: 1.0mm
  - SMD IC'ler: < 2mm
  - THT konnektörler: < 12mm

Bottom side (L6):
  - Bypass kapasitörler: 0.5mm (0402)
  - BGA altı temiz tut (heatsink montajı)
  - Maksimum yükseklik: 2mm (standoff clearance)
```

---

## 5. COPPER POUR STRATEJİSİ

### 5.1 GND Pour

```
L1 (Top): GND copper pour (boş alanlarda)
  - Tüm sinyal routing sonrası kalan alan GND fill
  - Termal relief: 4 spoke, 10 mil genişlik
  - Pour-to-trace clearance: 8 mil
  - Via stitching: Her 5mm'de 1 GND via (pour bağlantı)

L2 (GND): Tam düz GND plane
  - KESİNTİ YOK (özellikle DDR4 ve HDMI altında)
  - Via clearance: 6 mil
  - Anti-pad: Standart

L6 (Bottom): GND copper pour (boş alanlarda)
  - L1 ile simetrik
  - BGA altı bölgede thermal via array
```

### 5.2 Power Pour

```
L4 (Power): Bölgesel power pour
  - Her voltaj bölgesi polygon pour ile tanımlanır
  - Bölgeler arası 20 mil gap
  - Pour priority: VCC_3V3 (en geniş) > VCC_5V > diğerleri

L3 (Inner): Güç trace'leri (pour değil trace)
  - Regülatör çıkışlarından IC'lere geniş trace
  - Genişlik: VCC_5V: 30 mil, VCC_3V3: 25 mil, diğer: 20 mil
```

### 5.3 Thermal Via Array

```
SoC altında termal via dizisi:

  ┌──────────────────┐
  │  · · · · · · · · │
  │  · · · · · · · · │
  │  · · SoC  · · · │  · = Thermal via (0.3mm drill)
  │  · ·(GND) · · · │      GND plane'e bağlantı
  │  · · · · · · · · │
  │  · · · · · · · · │      Grid: 1mm x 1mm
  └──────────────────┘      Minimum 25 via

Regülatör GND padlerinde:
  - Her exposed pad altına 4-9 termal via
  - Via drill: 0.3mm
  - Direct connection (no thermal relief) → düşük termal direnç
```

---

## 6. DRC KURALLARI (JLCPCB 6-Layer)

```
JLCPCB 6-Katman Minimum Kurallar:

Trace:
  - Min trace genişliği: 3.5 mil (0.09mm)
  - Min trace aralığı:  3.5 mil (0.09mm)
  - Min trace-pad:      3.5 mil

Via:
  - Min via drill:       0.2mm (8 mil)
  - Min via pad:         0.4mm (16 mil)
  - Min via-via:         0.254mm (10 mil)
  - Min via-trace:       0.127mm (5 mil)
  - Min via-pad:         0.127mm (5 mil)
  - Aspect ratio:        Max 8:1 (1.6mm/0.2mm = 8)

Pad:
  - Min pad boyutu:      Bileşen datasheet'e göre
  - SMD pad solder mask: 0.05mm expansion
  - BGA pad: NSMD (Non Solder Mask Defined) tercih

Copper:
  - Min copper-edge:     0.3mm (12 mil)
  - Min copper-hole:     0.2mm (8 mil)
  - Min annular ring:    0.1mm (4 mil)

Board:
  - Min board edge-trace: 0.3mm
  - Min board edge-via:   0.3mm
  - Fiducial: Min 3 adet (köşelerde, 1mm Cu pad + 3mm clearance)
```

---

## 7. ÖZEL BÖLGE KURALLARI

### 7.1 BGA Fanout Bölgesi

```
SoC BGA-272 altı:
  - Via-in-pad: Gerekli (0.65mm pitch)
  - Via dolgu: Resin fill + cap plating (JLCPCB destekler)
  - Fanout katmanı: L1 (dış 2 sıra), L3/L5 (iç sıralar)
  - GND via array: BGA merkez bölgesinde

DDR4 FBGA-96 altı:
  - Via-in-pad: Tercihen (0.8mm pitch daha rahat)
  - Alt yüzde bypass kapasitörler
```

### 7.2 RF Bölgesi

```
DVB-S2 + LNB alanı:
  - GND plane bölme YOK
  - Analog/dijital izolasyon (ferrit bead)
  - 3.3V_RF ayrı pour
  - 75Ω microstrip: W ≈ 7 mil (L1, GND ref L2)
  - RF trace dönüşleri: Yalnızca arc
  - Via kullanma (RF trace'lerde)
  - Guard ring: GND via stitching RF alanı etrafında (2mm aralık)
```

### 7.3 Anten Bölgesi (WiFi)

```
WiFi anten alanı:
  - u.FL konnektör board kenarında
  - 50Ω microstrip trace: W ≈ 7.5 mil (L1, 0.075mm prepreg)
  - Anten trace altında GND clearance: YAPMA (referans gerekli)
  - Chip anteni kullanılıyorsa: Anten alanında copper keep-out
  - u.FL → chip arası: Mümkün olduğunca kısa (< 20mm)
```

---

## 8. MONTAJ DELİKLERİ VE MEKANİK

```
Board outline:
  ┌──────────────────────────────────────────┐
  │ ○                                    ○   │
  │                                          │
  │              150mm x 100mm               │
  │                                          │
  │                                          │
  │ ○                                    ○   │
  └──────────────────────────────────────────┘

Montaj delikleri (4 köşe):
  - Delik çapı: 3.2mm (M3 vida için)
  - Pad çapı: 6.0mm (GND bağlantılı)
  - Köşeden mesafe: 5mm x 5mm
  - GND via ring: Delik etrafında 4x GND via

Fiducial işaretleri (SMT hizalama):
  - 3 adet (2 köşe + 1 çapraz)
  - 1mm bakır pad, 3mm solder mask açıklık
  - Board kenarından: 5mm iç

Board edge:
  - Frezleme (routed, panelize etme)
  - Köşe yarıçapı: R=1mm (minimum)
  - V-score: Opsiyonel (panel üretim için)
```

---

## 9. SİLKSCREEN KURALLARI

```
Silkscreen (beyaz, L1 + L6):

  Zorunlu bilgiler:
  - Bileşen referans designator (U1, R1, C1, ...)
  - Pin 1 işareti (tüm IC'ler)
  - Polarite işareti (diyot, LED, elektrolitik cap)
  - Konnektör etiketleri (HDMI, USB3, USB2, LNB IN, ...)
  - Test noktası etiketleri (TP_5V, TP_GND, ...)
  - Board adı: "APEXSAT AI v1.0"
  - Revizyon: "REV A"
  - Tarih: "2026-02"
  - QR code: Seri numarası alanı (opsiyonel)

  Min silkscreen genişlik: 6 mil (0.15mm)
  Min silkscreen boyut: 30 mil (0.75mm)
  Silkscreen pad üzerine GELMEMELİ
```
