# APEXSAT AI v1.0 - JLCPCB Komponent Doğrulama Notları

## Tarih: 2026-02-20 | Revizyon: A

---

## 1. LCSC DOĞRULANMIŞ PARÇALAR (Stokta)

### Güç Regülatörleri
| Parça | LCSC # | Durum | Not |
|-------|--------|-------|-----|
| MP2315GJ-Z | C45889 | ✅ Doğrulandı | TSOT-23-8, Extended, ~$0.49 |
| MP1584EN-LF-Z | C15051 | ✅ Doğrulandı | SOIC-8-EP, Extended, ~$0.55 |
| SY8088AAC | C79313 | ✅ Doğrulandı | SOT-23-5, Extended, ~$0.049 |
| RT9193-18GB | C27416 | ✅ Doğrulandı | SOT-23-5, Extended, ~$0.054 |
| AP2112K-3.3TRG1 | C51118 | ✅ Doğrulandı | SOT-23-5, Extended, ~$0.078 |
| MP8759GD-Z | C3187827 | ⚠️ Sınırlı stok | TSOT-23-8, Extended, ~$0.80 |

### Pasif Komponentler
| Parça | LCSC # | Durum | Not |
|-------|--------|-------|-----|
| 100nF 0402 | C307331 | ✅ Basic | Samsung, çok yaygın |
| 1µF 0402 | C52923 | ✅ Basic | Samsung |
| 10µF 0402 | C15525 | ✅ Basic | Samsung |
| 22µF 0805 | C45783 | ✅ Basic | Samsung |
| 10kΩ 0402 | C25744 | ✅ Basic | UniOhm, çok yaygın |
| 4.7kΩ 0402 | C25900 | ✅ Basic | UniOhm |

### IC'ler
| Parça | LCSC # | Durum | Not |
|-------|--------|-------|-----|
| RTL8211F-CG | C187932 | ✅ Extended | ⚠️ QFN-40 (QFN-48 değil!), ~$0.85 - footprint doğrula |
| RTL8822CS-VL-CG | C2761413 | ✅ Extended | QFN-76, ~$7.51 (bare IC, modül değil) |
| LNBH26PQR | -- | ❌ LCSC'de YOK | DigiKey/Mouser'dan temin (~$3.50), consigned part |
| IP4791CZ12 | C551518 | ⚠️ Stok belirsiz | WLCSP-12, datasheet var ama stok doğrula |
| IP4220CZ6 | C111944 | ✅ Extended | SOT-457, USB ESD |
| INMP441 | -- | ❌ Bare IC yok | Alt: MSM261S4030H0R (C2840615) ~$1.71, I2S uyumlu |
| AO3400A | C20917 | ✅ Basic | SOT-23, MOSFET |

---

## 2. JLCPCB'DE BULUNMAYAN PARÇALAR (Ayrı Temin)

| Parça | Neden | Temin Kaynağı | Not |
|-------|-------|---------------|-----|
| S905X4-J | Amlogic distribütör | Shenzhen / AliExpress | BGA, NDA gerekir |
| K4A8G165WC-BCWE | Samsung DDR4, özel | Mouser / DigiKey / Taobao | FBGA-96, 4 adet |
| KLMAG1JETD-B041 | Samsung eMMC, özel | Mouser / DigiKey | FBGA-153 |
| LNBH26PQR | LCSC'de stoklanmıyor | DigiKey / Mouser / Arrow | ~$3.50, consigned part olarak JLCPCB'ye gönder |
| BSBE2-401A | DVB-S2 NIM modülü | AliExpress / uydu mağaza | THT, CX24116 tabanlı |
| Heatsink | Mekanik parça | AliExpress / yerel | 25x25x10mm |
| 3010 Fan | Mekanik parça | AliExpress / yerel | 5V PWM |
| WiFi Antenna | Harici aksesuar | AliExpress | Dual-band, IPEX |

### ⚠️ Web Araştırması Sonucu Kritik Bulgular:

1. **RTL8211F-CG paketi QFN-40**, QFN-48 değil! Footprint'i EasyEDA'da doğrula.
   - QFN-48 istiyorsan: RTL8211FSI-CG (C2904132, ~$4.02)

2. **RTL8822CS** LCSC'de bare IC olarak bulundu (C2761413, ~$7.51, QFN-76)
   - Modül değil, bare chip - kendi anten devresini tasarla

3. **INMP441** LCSC'de bare IC olarak yok (sadece $32+ eval board)
   - **Alternatif: MSM261S4030H0R** (C2840615, ~$1.71) - I2S dijital MEMS mic

4. **LNBH26PQR** LCSC'de stoklanmıyor
   - DigiKey'den temin et (~$3.50) ve JLCPCB'ye "consigned part" olarak gönder

5. **IP4791CZ12** C551518 olarak kayıtlı ama stok belirsiz
   - Alternatif: PRTR5V0U2X (C12333) - daha basit ESD koruma

### Alternatif SoC Seçenekleri (LCSC'de bulunabilecek):
- **Allwinner H616** (C-) - Daha kolay temin, benzer özellikler
- **Rockchip RK3566** (C-) - Mali-G52, daha güçlü GPU
- Not: S905X4 spesifik olarak seçildi (HW video codec + NPU)

---

## 3. SMT TİPİ ANALİZİ

### JLCPCB SMT ile Yerleştirilebilecek (~150 parça):
- **Basic parçalar** (ek ücret yok): ~120 yerleştirme
  - Tüm 0402 kapasitörler (50+14+10+4+8+2+4+3 = ~95)
  - Tüm 0402 dirençler (~57)
  - LED'ler (4), Kristaller (2), Fuse (4), Diode (2)
  - RT9193, AP2112K, MP1584EN, AO3400A

- **Extended parçalar** ($3/benzersiz): ~30 yerleştirme, ~15 benzersiz
  - MP2315, SY8088, MP8759 (güç IC'leri)
  - RTL8211F (Ethernet PHY)
  - LNBH26PQR (LNB power)
  - IP4791CZ12, IP4220CZ6 (ESD)
  - INMP441 x2 (mikrofon)
  - İndüktörler (5 benzersiz)
  - Polimer kapasitörler (1 benzersiz, 4 adet)
  - u.FL konnektörler (2)
  - microSD yuvası, HDMI konnektör, USB-C
  - Butonlar (2)

### Manuel Lehim Gerektiren (~20 parça):
- **BGA (Reflow oven gerekli)**: SoC, DDR4 x4, eMMC, WiFi = 7 parça
- **Through-Hole (El lehimi)**: F-Type x2, RJ45, USB-A x3, DC Jack, Audio, TOSLINK, IR alıcı, IR LED, NIM = 12 parça

---

## 4. MALİYET KARŞILAŞTIRMASI

### Prototip (1 adet)
| Kalem | Maliyet |
|-------|---------|
| JLCPCB SMT BOM | ~$45 |
| Manuel BOM (SoC, DDR4, eMMC, WiFi, NIM) | ~$27 |
| PCB (6L, 150x100mm, ENIG) | ~$30 |
| SMT Montaj | ~$35 |
| Extended Ek Ücret (~15 × $3) | ~$45 |
| Kargo (DHL Express) | ~$20 |
| **TOPLAM** | **~$202** |

### 10 Adet Üretim
| Kalem | Birim Maliyet |
|-------|---------------|
| BOM (toplu fiyat) | ~$55 |
| PCB | ~$5 |
| SMT | ~$8 |
| Extended Ek Ücret | ~$5 |
| Kargo (birim) | ~$3 |
| **BİRİM TOPLAM** | **~$76** |

### 100 Adet Üretim
| Kalem | Birim Maliyet |
|-------|---------------|
| BOM (toplu fiyat) | ~$42 |
| PCB | ~$2 |
| SMT | ~$3 |
| Extended Ek Ücret | ~$1 |
| Kargo (birim) | ~$1 |
| **BİRİM TOPLAM** | **~$49** |

---

## 5. SİPARİŞ ÖNCESİ KONTROL LİSTESİ

- [ ] LCSC stok kontrolü (her parça için minimum sipariş adedi)
- [ ] MP8759GD-Z (C3187827) stok doğrulama
- [ ] S905X4-J temin kaynağı belirleme (Shenzhen agent)
- [ ] DDR4 / eMMC temin ve uyumluluk testi
- [ ] RTL8822CS FCC/CE belge kontrolü
- [ ] DVB NIM modülü uyumluluk testi (CX24116 driver)
- [ ] EasyEDA Pro'da footprint doğrulama (tüm LCSC parçalar)
- [ ] DRC (Design Rule Check) sonrası BOM güncelleme
- [ ] Gerber + BOM + CPL dosyası JLCPCB format kontrolü

---

## 6. ÖNEMLİ UYARILAR

1. **MP8759GD-Z** yeni bir parça, LCSC'de stok dalgalanması olabilir
   - Alternatif: TPS62130 (TI), RT6150A (Richtek)

2. **AP2112K** sadece RF 3.3V için kullanılıyor (ana 3.3V → MP1584EN)
   - power_tree.md'deki termal analiz sonucu

3. **Polimer kapasitörler** (100µF) Extended kategori
   - Alternatif: 2x 47µF MLCC 1206 (Basic olabilir)

4. **INMP441** stok sıkıntısı yaşanabilir
   - Alternatif: SPH0645LM4H (Knowles), ICS-43434 (TDK)

5. **25MHz kristal** ETH PHY için - yanlış yük kapasitansı performansı bozar
   - Datasheet'ten CL değerini doğrula, uygun C_LOAD seç
