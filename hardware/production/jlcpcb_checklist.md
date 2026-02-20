# APEXSAT AI v1.0 - JLCPCB Üretim Dosya Checklist

## Tasarımcı: Halil Dinçer
## Tarih: 2026-02-20 | Revizyon: A

---

## 1. JLCPCB SİPARİŞ PARAMETRELERİ

```
PCB Sipariş Özellikleri:
  ┌────────────────────────────────────────────┐
  │ Base Material:      FR4 (Tg150+)          │
  │ Layers:             6                      │
  │ Dimensions:         150mm × 100mm          │
  │ PCB Qty:            5 (prototip)           │
  │ PCB Thickness:      1.6mm                  │
  │ Impedance Control:  Yes                    │
  │ Stackup:            JLC06161H-1080         │
  │ PCB Color:          Black                  │
  │ Silkscreen:         White                  │
  │ Surface Finish:     ENIG (1U")             │
  │ Copper Weight:      1 oz (outer+inner)     │
  │ Via Covering:       Resin fill + cap plate │
  │ Min Trace/Space:    3.5/3.5 mil            │
  │ Min Hole Size:      0.2mm                  │
  │ Board Edge:         Routing (no V-score)   │
  │ Gold Fingers:       No                     │
  │ Castellated Holes:  No                     │
  │ Panel:              No (single board)      │
  │ Confirm Production: Yes (impedance review) │
  └────────────────────────────────────────────┘
```

---

## 2. GEREKLİ DOSYALAR

### 2.1 Gerber Dosyaları

```
EasyEDA Pro → Fabrication → Generate Gerber

Dosya listesi (6-katman):
  ┌──────────────────────────────────────────────┐
  │ Dosya               │ Açıklama              │
  ├──────────────────────────────────────────────┤
  │ F_Cu.gtl            │ L1 Top Copper         │
  │ In1_Cu.g2           │ L2 GND Plane          │
  │ In2_Cu.g3           │ L3 Inner Signal/Power │
  │ In3_Cu.g4           │ L4 Power Plane        │
  │ In4_Cu.g5           │ L5 Inner Signal       │
  │ B_Cu.gbl            │ L6 Bottom Copper      │
  │ F_Mask.gts          │ Top Solder Mask       │
  │ B_Mask.gbs          │ Bottom Solder Mask    │
  │ F_SilkS.gto         │ Top Silkscreen        │
  │ B_SilkS.gbo         │ Bottom Silkscreen     │
  │ F_Paste.gtp         │ Top Solder Paste      │
  │ B_Paste.gbp         │ Bottom Solder Paste   │
  │ Edge_Cuts.gm1       │ Board Outline         │
  │ PTH.drl             │ Plated Through-Hole   │
  │ NPTH.drl            │ Non-Plated Holes      │
  └──────────────────────────────────────────────┘

  Format: RS-274X (Extended Gerber)
  Drill format: Excellon
  Birim: mm (milimetre)
  Koordinat: Decimal, 4.6 format

  Gerber'ları ZIP'e sıkıştır → JLCPCB'ye yükle
```

### 2.2 BOM Dosyası (SMT Assembly İçin)

```
EasyEDA Pro → BOM → Export CSV

JLCPCB BOM formatı (zorunlu kolonlar):
  ┌──────────────────────────────────────────────────────────┐
  │ Comment  │ Designator    │ Footprint  │ LCSC Part Number │
  ├──────────────────────────────────────────────────────────┤
  │ 100nF    │ C1,C2,C3,...  │ 0402       │ C131394          │
  │ 10kΩ     │ R1,R2,R3,...  │ 0402       │ C25744           │
  │ MP2315   │ U11           │ TSOT-23-8  │ C45889           │
  │ ...      │ ...           │ ...        │ ...              │
  └──────────────────────────────────────────────────────────┘

  - "Comment" = bileşen değeri
  - "Designator" = referans (virgülle ayrılmış, aynı parça)
  - "Footprint" = paket adı
  - "LCSC Part Number" = C+rakam formatında

  Dosya adı: BOM_APEXSAT_AI_v1.0.csv
  Encoding: UTF-8
```

### 2.3 CPL (Component Placement List) Dosyası

```
EasyEDA Pro → Pick and Place → Export CSV

JLCPCB CPL formatı:
  ┌───────────────────────────────────────────────────────────┐
  │ Designator │ Mid X    │ Mid Y    │ Rotation │ Layer      │
  ├───────────────────────────────────────────────────────────┤
  │ U11        │ 25.4mm   │ 12.7mm   │ 0        │ Top       │
  │ C1         │ 10.2mm   │ 5.1mm    │ 90       │ Top       │
  │ C_BGA_1    │ 50.0mm   │ 30.0mm   │ 0        │ Bottom    │
  │ ...        │ ...      │ ...      │ ...      │ ...       │
  └───────────────────────────────────────────────────────────┘

  - Koordinatlar: mm, board origin sol-alt köşe
  - Rotation: derece (0, 90, 180, 270)
  - Layer: "Top" veya "Bottom"

  Dosya adı: CPL_APEXSAT_AI_v1.0.csv
  Encoding: UTF-8
```

---

## 3. TASARIM DOĞRULAMA CHECKLIST

### 3.1 ERC (Electrical Rule Check)

```
EasyEDA Pro → Design → ERC

Kontrol edilecekler:
  □ Bağlantısız pin yok (unconnected pins)
  □ Kısa devre yok (short circuits)
  □ Birden fazla güç kaynağına bağlı net yok
  □ Güç pinler doğru net'e bağlı
  □ GND bağlantısı eksik bileşen yok
  □ Referans designator çakışması yok
  □ Tüm bileşenlerin footprint'i atanmış
  □ Net label eşleşme kontrolü (sayfalar arası)
  □ NC (Not Connected) pinler işaretli
```

### 3.2 DRC (Design Rule Check)

```
EasyEDA Pro → PCB → DRC

Kural seti (JLCPCB 6-Layer):
  ┌──────────────────────────────────────────────┐
  │ Kural                │ Değer                 │
  ├──────────────────────────────────────────────┤
  │ Min Trace Width      │ 3.5 mil (0.09mm)     │
  │ Min Trace Spacing    │ 3.5 mil (0.09mm)     │
  │ Min Trace-Pad        │ 3.5 mil              │
  │ Min Via Drill        │ 0.2mm                │
  │ Min Via Pad          │ 0.4mm                │
  │ Min Via-Via          │ 0.254mm              │
  │ Min Via-Trace        │ 0.127mm              │
  │ Min Annular Ring     │ 0.1mm                │
  │ Min Copper-Edge      │ 0.3mm                │
  │ Min Solder Mask      │ 0.05mm               │
  │ Min Silkscreen       │ 6 mil (0.15mm)       │
  │ Min Pad-Pad          │ 3.5 mil              │
  │ Min Hole-Hole        │ 0.5mm                │
  │ Min Hole-Edge        │ 0.5mm                │
  └──────────────────────────────────────────────┘

  □ 0 DRC hatası
  □ 0 DRC uyarısı (veya tümü açıklanmış)
```

### 3.3 Empedans Kontrol

```
JLCPCB'ye belirtilecek empedans gereksinimleri:

  ┌──────────────────────────────────────────────────────────────┐
  │ # │ Tip          │ Katman │ Empedans │ Trace W │ Space S   │
  ├──────────────────────────────────────────────────────────────┤
  │ 1 │ Single-ended │ L1     │ 40Ω      │ 5.0 mil │ -         │
  │ 2 │ Single-ended │ L1     │ 50Ω      │ 3.8 mil │ -         │
  │ 3 │ Differential │ L1     │ 80Ω      │ 4.5 mil │ 5.0 mil   │
  │ 4 │ Differential │ L1     │ 90Ω      │ 4.0 mil │ 5.5 mil   │
  │ 5 │ Differential │ L1     │ 100Ω     │ 3.5 mil │ 6.0 mil   │
  └──────────────────────────────────────────────────────────────┘

  JLCPCB impedans hesaplayıcı ile trace boyutlarını doğrula.
  Kesin stackup dielektrik kalınlığına göre ayarla.

  Sipariş notlarına ekle:
  "Impedance controlled. Please see impedance table in notes."
```

---

## 4. SMT ASSEMBLY CHECKLIST

### 4.1 Yerleştirme Kontrolü

```
SMT Assembly siparişinden ÖNCE:

  □ JLCPCB Part Library'de tüm LCSC parçalar mevcut
  □ Stok kontrolü: Her parça sipariş adedi kadar stokta
  □ Extended parça sayısı not edildi (~15 benzersiz × $3 = ~$45)
  □ Footprint uyumu: LCSC parça footprint'i PCB ile eşleşiyor
  □ Rotation kontrolü: CPL'deki açılar doğru (pin 1 uyumu)
  □ BOM'daki designator'lar CPL'deki ile birebir eşleşiyor
  □ Top + Bottom assembly seçimi yapıldı
  □ DNP (Do Not Place) bileşenler BOM'dan çıkarıldı
```

### 4.2 Consigned Parts (Harici Temin)

```
JLCPCB'ye gönderilecek consigned parçalar:

  1. LNBH26PQR (QFN-24) - DigiKey'den temin
     - Adet: 5 + 2 yedek = 7
     - Paketleme: Tape & reel veya tray

  Consigned part prosedürü:
  1. JLCPCB sipariş sırasında "Consigned Parts" seç
  2. Parçayı kargo ile JLCPCB'ye gönder
  3. JLCPCB depoda teslim alınca assembly başlar
  4. Teslimat süresi: +5-7 gün ek
```

### 4.3 Manuel Lehim Parçaları

```
JLCPCB SMT sonrası, manuel lehim gereken parçalar:

BGA Reflow (profesyonel reflow station gerekli):
  □ U1: S905X4-J (BGA-272, 0.65mm pitch) ★ En kritik
  □ U2-U5: DDR4 x4 (FBGA-96, 0.8mm pitch)
  □ U6: eMMC (FBGA-153, 0.5mm pitch)

Through-Hole (el lehimi):
  □ J2, J3: F-Type konnektör x2
  □ J5: RJ45 Magjack
  □ J7: USB 3.0 Type-A
  □ J8a, J8b: USB 2.0 Type-A x2
  □ J10: 3.5mm Audio Jack
  □ J11: TOSLINK konnektör
  □ J12: DC Barrel Jack
  □ U18: TSOP38238 IR alıcı
  □ D1: IR LED
  □ M1: DVB NIM modülü

Sıralama:
  1. JLCPCB SMT assembly → tüm SMD parçalar
  2. BGA reflow → SoC, DDR4, eMMC (reflow oven ile)
  3. THT lehim → konnektörler (el ile)
  4. NIM modülü → soket/lehim
  5. Heatsink montaj → termal pad + yapıştır
```

---

## 5. KALİTE KONTROL

### 5.1 PCB Teslim Sonrası Kontrol

```
PCB geldiğinde (SMT assembly öncesi veya sonrası):

Görsel kontrol:
  □ Board boyutu doğru (150x100mm ±0.2mm)
  □ Katman sayısı doğru (6 katman, kenardan kontrol)
  □ Solder mask rengi doğru (siyah)
  □ Silkscreen okunabilir
  □ ENIG yüzey parlak ve düzgün
  □ Montaj delikleri doğru pozisyonda
  □ Board kenarları pürüzsüz
  □ Via dolgusu düzgün (resin fill + cap)

Elektriksel kontrol:
  □ GND - VCC arası kısa devre YOK (multimetre)
  □ Güç rail'leri arası kısa devre YOK
  □ Montaj delikleri GND'ye bağlı (kontrol)

Empedans kontrolü (opsiyonel, JLCPCB coupon ile):
  □ Empedans test kuponu kart üzerinde varsa ölç
  □ 50Ω ±10%, 90Ω ±10%, 100Ω ±10%
```

### 5.2 İlk Güç Verme Prosedürü

```
⚡ İLK GÜÇ VERME (Smoke Test):

UYARI: BGA bileşenler lehimlenmeden güç testi yapılabilir
(sadece regülatör çıkış voltajlarını kontrol etmek için)

Adım 1: Görsel kontrol (lehim köprüsü, eksik bileşen)
Adım 2: Multimetre ile kısa devre testi
  - VIN_12V ↔ GND: > 10Ω olmalı
  - VCC_5V ↔ GND: > 5Ω olmalı
  - VCC_3V3 ↔ GND: > 5Ω olmalı

Adım 3: Akım sınırlı güç kaynağı ile:
  - 12V, akım limiti: 0.5A (başlangıç)
  - Beklenen boş kart akımı: < 100mA (SoC yok)

Adım 4: Voltaj ölçümleri:
  □ TP_5V:  5.0V ±0.1V
  □ TP_3V3: 3.3V ±0.1V
  □ TP_1V8: 1.8V ±0.05V
  □ TP_1V1: 1.1V ±0.05V
  □ TP_0V9: 0.9V ±0.05V

Adım 5: Power sequencing doğrula (osiloskop):
  □ 0.9V → 1.1V → 1.8V sırası doğru
  □ Rise time < 10ms (her kademe)

Adım 6: Ripple ölçümü (osiloskop, AC coupling):
  □ 5V ripple: < 50mV
  □ 3.3V ripple: < 30mV
  □ 1.8V ripple: < 20mV
  □ 0.9V ripple: < 20mV
```

---

## 6. ÜRETİM TAKVİMİ

```
Prototip üretim takvimi (tahmini):

  Gün 0:   Şematik tamamlama
  Gün 3:   PCB layout tamamlama
  Gün 4:   DRC + ERC pass, Gerber export
  Gün 5:   JLCPCB sipariş (PCB + SMT assembly)
  Gün 7:   Consigned parçalar kargoya (LNBH26)
  Gün 12:  JLCPCB PCB üretim tamamlanır
  Gün 15:  SMT assembly tamamlanır
  Gün 17:  Kargo çıkışı (DHL Express)
  Gün 20:  Board teslim alınır
  Gün 21:  BGA reflow (SoC, DDR4, eMMC)
  Gün 22:  THT lehim (konnektörler)
  Gün 23:  İlk güç testi
  Gün 24:  Firmware yükleme + boot testi
  Gün 25:  Fonksiyon testleri başlar
  ─────────────────────────────────────
  Toplam:  ~25 iş günü (5 hafta)
```

---

## 7. DOSYA YAPISI ÖZETİ

```
hardware/production/
├── gerber/
│   ├── APEXSAT_AI_v1.0_Gerber.zip    ← JLCPCB'ye yükle
│   ├── F_Cu.gtl
│   ├── In1_Cu.g2
│   ├── In2_Cu.g3
│   ├── In3_Cu.g4
│   ├── In4_Cu.g5
│   ├── B_Cu.gbl
│   ├── F_Mask.gts
│   ├── B_Mask.gbs
│   ├── F_SilkS.gto
│   ├── B_SilkS.gbo
│   ├── F_Paste.gtp
│   ├── B_Paste.gbp
│   ├── Edge_Cuts.gm1
│   ├── PTH.drl
│   └── NPTH.drl
├── BOM_APEXSAT_AI_v1.0.csv           ← JLCPCB BOM format
├── CPL_APEXSAT_AI_v1.0.csv           ← JLCPCB CPL format
├── impedance_requirements.txt         ← Empedans tablosu
└── jlcpcb_checklist.md               ← Bu dosya

hardware/schematics/
├── block_diagram.md                   ← ADIM 1
├── netlist_connections.md             ← ADIM 2
├── power_tree.md                      ← ADIM 3
├── ddr4_routing_guide.md              ← ADIM 5
├── highspeed_routing_guide.md         ← ADIM 6
└── schematic_pages_plan.md            ← ADIM 7

hardware/bom/
├── jlcpcb_component_list.csv          ← ADIM 4
├── jlcpcb_verification_notes.md       ← ADIM 4 ek
├── bom_apexsat_v1.csv                 ← Orijinal BOM
└── procurement_notes.md               ← Temin notları

hardware/pcb/
└── layer_stackup_and_placement.md     ← ADIM 8

hardware/
└── thermal_analysis.md                ← ADIM 9
```

---

## 8. JLCPCB SİPARİŞ NOTU ŞABLONU

```
Sipariş sırasında "Remark" alanına yazılacak:

─────────────────────────────────────────────
APEXSAT AI v1.0 - 6-Layer Impedance Controlled PCB

Impedance Requirements:
1. Single-ended 40Ω (DDR4) - L1, ref GND L2
2. Single-ended 50Ω (RGMII/eMMC) - L1, ref GND L2
3. Differential 80Ω (DDR4 CLK/DQS) - L1
4. Differential 90Ω (USB) - L1
5. Differential 100Ω (HDMI/ETH MDI) - L1

Stackup: JLC06161H-1080 (or equivalent 6-layer)
Via fill: Resin fill + cap plating required
BGA via-in-pad: Yes (U1 area, 0.65mm pitch)

Please confirm impedance trace widths before production.
─────────────────────────────────────────────
```
