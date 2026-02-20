# APEXSAT AI v1.0 - Termal Analiz

## Tasarımcı: Halil Dinçer
## Tarih: 2026-02-20 | Revizyon: A

---

## 1. TERMAL KAYNAKLARI

### 1.1 Tüm Bileşenlerin Güç Dağılımı

| # | Bileşen | Paket | Tipik Güç (W) | Max Güç (W) | θJA (°C/W) | Soğutma |
|---|---------|-------|---------------|-------------|------------|---------|
| 1 | S905X4-J (SoC) | BGA-272 | 3.5 | 6.0 | 15* | Heatsink + Fan |
| 2 | DDR4 x4 | FBGA-96 | 0.8 (toplam) | 1.6 | 60 | PCB copper |
| 3 | eMMC | FBGA-153 | 0.3 | 0.5 | 50 | PCB copper |
| 4 | MP2315 (5V Buck) | TSOT-23-8 | 1.05 | 2.1 | 45 | PCB copper + thermal via |
| 5 | MP1584EN (3.3V Buck) | SOIC-8-EP | 0.35 | 0.7 | 50 | Exposed pad + via |
| 6 | SY8088 (0.9V Buck) | SOT-23-5 | 0.68 | 1.4 | 120 | ⚠️ PCB copper gerekli |
| 7 | MP8759 (1.1V Buck) | QFN-12 | 0.52 | 1.0 | 40 | Exposed pad + via |
| 8 | RT9193 (1.8V LDO) | SOT-23-5 | 0.38 | 0.45 | 220 | ⚠️ PCB copper gerekli |
| 9 | AP2112K (3.3V_RF LDO) | SOT-23-5 | 0.24 | 0.60 | 250 | PCB copper |
| 10 | RTL8211F (ETH PHY) | QFN-40 | 0.5 | 0.8 | 35 | Exposed pad |
| 11 | RTL8822CS (WiFi) | QFN-76 | 0.8 | 1.2 | 30 | Exposed pad |
| 12 | LNBH26 (LNB) | QFN-24 | 0.4 | 1.5 | 35 | Exposed pad |
| | **TOPLAM** | | **~9.5W** | **~18W** | | |

*θJA: BGA-272 with heatsink ≈ 15°C/W, without ≈ 25°C/W

---

## 2. KRİTİK TERMAL ANALİZ

### 2.1 SoC - Amlogic S905X4

```
En kritik termal kaynak: SoC

Çalışma koşulları:
  - Tipik güç: 3.5W (video oynatma + AI idle)
  - Max güç: 6.0W (4K decode + NPU + WiFi aktif)
  - Ortam sıcaklığı: Ta = 40°C (kabin içi)
  - Max junction sıcaklığı: Tj_max = 125°C

Hesaplama (heatsink İLE):
  Tj = Ta + (P × θJA_total)
  θJA_total = θJC + θCS + θSA

  θJC (junction → case): ~5°C/W (BGA-272)
  θCS (case → sink): ~3°C/W (termal pad ile)
  θSA (sink → ambient): ~7°C/W (25x25x10mm heatsink)
  θJA_total = 5 + 3 + 7 = 15°C/W

  Tipik: Tj = 40 + (3.5 × 15) = 92.5°C ✅ (< 125°C)
  Max:   Tj = 40 + (6.0 × 15) = 130°C ❌ (> 125°C!)

  ★ MAX yükte fan gerekli!

Fan ile (zorlamalı hava):
  θSA_fan ≈ 3°C/W (30mm fan)
  θJA_total_fan = 5 + 3 + 3 = 11°C/W
  Max: Tj = 40 + (6.0 × 11) = 106°C ✅

Sonuç:
  - Pasif soğutma: Tipik yükte yeterli (92.5°C)
  - Aktif soğutma: Max yükte ZORUNLU (fan ile 106°C)
  - PWM fan kontrolü: CPU temp > 70°C → fan başlat
  - Throttle: CPU temp > 100°C → frekans düşür
```

### 2.2 SY8088 (0.9V Buck) - UYARI

```
Sorunlu bileşen: SY8088AAC (SOT-23-5)

  P_dissipation = (5V × 1.5A) × (1 - η) = 7.5 × 0.1 = 0.75W
  θJA = 120°C/W (SOT-23-5, minimum copper)

  ΔT = 0.75 × 120 = 90°C
  Tj = 40 + 90 = 130°C ⚠️ (Tj_max = 150°C, yakın!)

Çözüm:
  1. Geniş PCB copper pour (GND pad altında)
     - 15x15mm bakır alan → θJA ~80°C/W
     - ΔT = 0.75 × 80 = 60°C → Tj = 100°C ✅

  2. Termal via dizisi (pad altına):
     - 4x termal via (0.3mm drill)
     - Bottom side'da da copper pour
     - θJA ~65°C/W → Tj = 88.75°C ✅

  3. Yükü azalt:
     - SoC idle modesunda CPU core voltajı düşür (DVFS)
     - 0.9V @ 1.0A tipik → P = 0.5W → Tj = 80°C ✅

★ PCB TASARIM KURALI: SY8088 pad altında minimum
  15x15mm GND copper pour + 4 termal via
```

### 2.3 RT9193 (1.8V LDO) - UYARI

```
RT9193-18GB (SOT-23-5):

  P_dissipation = (3.3V - 1.8V) × 0.25A = 0.375W
  θJA = 220°C/W (SOT-23-5)

  ΔT = 0.375 × 220 = 82.5°C
  Tj = 40 + 82.5 = 122.5°C ⚠️ (Tj_max = 150°C, ama sıcak)

  NOT: 1.8V LDO'ya VCC_3V3'ten değil VCC_5V'dan besleme alternatif:
  P_new = (5.0 - 1.8) × 0.25 = 0.8W → Tj = 216°C ❌ DAHA KÖTÜ

  Mevcut: 3.3V → 1.8V doğru seçim ✅

Çözüm:
  1. Geniş PCB copper pour (10x10mm)
     - θJA ~150°C/W → Tj = 96°C ✅

  2. Yükü düşük tut
     - DDR4 idle'da VDD akımı düşer (50mA)
     - P_idle = 1.5V × 0.05A = 0.075W → Tj = 56.5°C ✅

  3. Alternatif: LDO yerine buck converter
     - Eğer 1.8V yükü artarsa (> 300mA), buck gerekir
     - SY8088 ikinci adet (5V → 1.8V)
```

### 2.4 AP2112K (RF 3.3V LDO) - GÜVENLI

```
AP2112K-3.3TRG1 (SOT-23-5) - Sadece RF 3.3V:

  P_dissipation = (5.0V - 3.3V) × 0.35A = 0.595W
  θJA = 250°C/W

  ΔT = 0.595 × 250 = 148.75°C
  Tj = 40 + 148.75 = 188.75°C ❌

  ★ HALİ HAZIRDA SINIRDA!

  Ancak tipik yük çok daha düşük:
  - DVB NIM aktif: ~300mA → P = 0.51W → Tj = 167°C ❌
  - DVB NIM idle: ~50mA → P = 0.085W → Tj = 61°C ✅

Çözüm:
  1. RF LDO'yu da MP1584EN yerine 3.3V buck'tan besle:
     - U16 MP1584EN (12V → 3.3V) → Ferrit bead → RF 3.3V
     - AP2112K KALDIRILIYOR
     - ✅ Termal sorun tamamen çözülür

  2. VEYA giriş voltajını düşür:
     - AP2112K'yi 3.3V buck çıkışından (MP1584EN) besle
     - P = (3.3V - 3.3V) × I ≈ 0W → LDO olarak çalışmaz!
     - Bu durumda ferrit bead + kapasitör filtre yeterli

★ KARAR: AP2112K yerine ferrit bead filtre kullan
  MP1584EN (3.3V) → [Ferrit Bead 600Ω] → 3.3V_RF
  Bu sayede:
  - Güç kaybı: ~0 (ferrit bead sadece HF filtre)
  - RF izolasyonu: Korunur
  - 1 IC azalır (maliyet + alan tasarrufu)
```

---

## 3. GÜNCELLENMIŞ TERMAL SONUÇLAR

| Bileşen | Güç (W) | θJA Efektif | ΔT (°C) | Tj (°C) | Durum |
|---------|---------|-------------|---------|---------|-------|
| S905X4 (heatsink) | 3.5 typ | 15 | 52.5 | 92.5 | ✅ OK |
| S905X4 (heatsink+fan) | 6.0 max | 11 | 66 | 106 | ✅ OK |
| DDR4 x4 (per chip) | 0.2 | 60 | 12 | 52 | ✅ OK |
| eMMC | 0.3 | 50 | 15 | 55 | ✅ OK |
| MP2315 (5V) | 1.05 | 45 | 47 | 87 | ✅ OK |
| MP1584EN (3.3V) | 0.35 | 50 | 17.5 | 57.5 | ✅ OK |
| SY8088 (0.9V) + copper | 0.75 | 65 | 48.75 | 88.75 | ✅ OK |
| MP8759 (1.1V) | 0.52 | 40 | 20.8 | 60.8 | ✅ OK |
| RT9193 (1.8V) + copper | 0.375 | 150 | 56.25 | 96.25 | ✅ OK |
| Ferrit Bead (RF 3.3V) | ~0 | - | ~0 | 40 | ✅ OK |
| RTL8211F | 0.5 | 35 | 17.5 | 57.5 | ✅ OK |
| RTL8822CS | 0.8 | 30 | 24 | 64 | ✅ OK |
| LNBH26 | 0.4 | 35 | 14 | 54 | ✅ OK |

**Tüm bileşenler güvenli termal aralıkta.**

---

## 4. SOĞUTMA STRATEJİSİ

### 4.1 Pasif Soğutma (Heatsink)

```
SoC Heatsink:
  - Boyut: 25x25x10mm (alüminyum fin)
  - Termal arayüz: 3M 8810 termal pad (1mm kalınlık)
  - θSA ≈ 7°C/W (doğal konveksiyon)
  - Montaj: Yapışkanlı termal pad + plastik klips

Alternatif heatsink seçenekleri:
  - 25x25x5mm: θSA ≈ 12°C/W (düşük profil kasa için)
  - 30x30x10mm: θSA ≈ 5°C/W (daha iyi ama PCB'de yer)
```

### 4.2 Aktif Soğutma (Fan)

```
Fan PWM Kontrolü:

  Fan: 30x30x10mm, 5V DC, PWM giriş
  Kontrol: SoC PWM çıkış → Q1 (AO3400A MOSFET) → Fan

  Sıcaklık eşikleri:
    < 60°C:  Fan KAPALI (duty = 0%)
    60-70°C: Fan DÜŞÜK (duty = 30%)
    70-80°C: Fan ORTA (duty = 60%)
    80-90°C: Fan YÜKSEK (duty = 90%)
    > 90°C:  Fan MAX (duty = 100%)
    > 100°C: CPU throttle (frekans düşür)
    > 110°C: Acil kapatma

  PWM frekansı: 25kHz (sessiz çalışma)
  Gürültü: < 25dB @ 30% duty
```

### 4.3 PCB Termal Tasarım

```
PCB üzerinden ısı dağıtımı:

1. SoC altı termal via array:
   - 5x5 = 25 via (0.3mm drill, 1mm grid)
   - L1 → L2 (GND) → L6 termal yol
   - L6'da geniş copper pour (heatsink montaj alanı)

2. Regülatör termal pad'leri:
   - MP2315: Exposed pad altında 4 via → GND plane
   - MP1584EN: Exposed pad altında 6 via → GND plane
   - MP8759: Exposed pad altında 4 via → GND plane
   - SY8088: GND pin genişletilmiş pad + 4 via
   - RT9193: GND pin genişletilmiş pad + 4 via

3. Copper pour alanları:
   - SoC çevresi: 30x30mm GND pour (L1)
   - Her regülatör: 15x15mm GND pour (L1)
   - L2 tam düz GND (kesintisiz)

4. Termal relief:
   - GND plane via'ları: Direct connect (termal relief YOK)
   - Sinyal via'ları: 4-spoke thermal relief
```

---

## 5. WORST-CASE SENARYO ANALİZİ

```
En kötü durum: 40°C ortam + tüm bileşenler max yükte

Toplam güç dağılımı: ~18W
12V giriş akımı: ~2.5A

Kasa iç sıcaklığı (kapalı kasa):
  ΔT_kasa = P_total × θ_kasa
  θ_kasa ≈ 5°C/W (tipik plastik kasa, havalandırma delikli)
  ΔT_kasa = 18 × 5 = 90°C → Kasa içi = 130°C ❌

  ★ KRİTİK: Kapalı kasada havalandırma ZORUNLU

  Fan + havalandırma delikleri ile:
  θ_kasa_fan ≈ 1.5°C/W
  ΔT = 18 × 1.5 = 27°C → Kasa içi = 67°C ✅

  Sonuç: Kasada havalandırma + fan ZORUNLU

Kasa tasarım gereksinimleri:
  - Alt ve üst yüzde havalandırma delikleri
  - Fan çıkış açıklığı (30x30mm)
  - Minimum 20% açık alan (havalandırma oranı)
```

---

## 6. TERMAL TASARIM CHECKLIST

```
□ SoC heatsink boyutu yeterli (25x25x10mm min)
□ Termal pad seçildi (3M 8810 veya eşdeğer)
□ SoC altında 25+ termal via (0.3mm drill)
□ Fan PWM devresi tasarlandı (Q1 + 10kΩ pull-down)
□ Fan sıcaklık eşikleri yazılımda tanımlandı
□ SY8088 pad altında 15x15mm copper pour
□ RT9193 pad altında 10x10mm copper pour
□ Tüm regülatör exposed pad'larda termal via
□ L2 GND plane kesintisiz (termal yol)
□ Copper pour tüm boş alanlarda (L1, L6)
□ Via stitching her 5mm'de (copper pour bağlantı)
□ Kasa havalandırma delikleri planlandı
□ AP2112K kaldırıldı → ferrit bead filtre (termal çözüm)
□ Worst-case analiz: Tüm Tj < 125°C (fan ile)
```

---

## 7. TASARIM DEĞİŞİKLİK ÖZETİ (Termal Analiz Sonucu)

```
Termal analizden kaynaklanan tasarım değişiklikleri:

1. ★ AP2112K (RF 3.3V LDO) → Ferrit Bead filtre
   - Neden: SOT-23-5 termal olarak DVB NIM yükü için yetersiz
   - Çözüm: MP1584EN (3.3V) → FB → 3.3V_RF
   - Etki: 1 IC azaldı, termal sorun çözüldü

2. SY8088 PCB copper pour gereksinimi
   - Minimum 15x15mm GND copper pour
   - 4+ termal via exposed pad altında

3. RT9193 PCB copper pour gereksinimi
   - Minimum 10x10mm GND copper pour

4. Fan ZORUNLU (max yükte)
   - PWM kontrollü, 5V DC, 30x30mm
   - 70°C threshold ile otomatik başlatma

5. Kasa havalandırma ZORUNLU
   - Alt + üst yüz delikler
   - Min %20 açık alan
```
