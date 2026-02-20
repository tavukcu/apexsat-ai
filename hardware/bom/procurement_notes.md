# APEXSAT AI v1.0 - Parça Temin Notları

## Kritik Bileşenler (Özel Temin Gerekli)

### 1. Amlogic S905X4-J (SoC)
- **LCSC/JLCPCB'de YOK** - Amlogic OEM kanal gerektirir
- **Alternatif temin:**
  - AliExpress'ten X96 Max Plus TV Box alıp SoC'u rework etme
  - Taobao üzerinden bare chip sipariş (minimum adet sınırı olabilir)
  - Shenzhen broker/distribütör ile iletişim
- **Referans kart alternatifi:** Khadas VIM4 veya X96 Max Plus geliştirme amaçlı kullanılabilir

### 2. DVB-S2 NIM Modülü
- **LCSC/JLCPCB'de YOK**
- **Temin kaynakları:**
  - eBay: "DVB-S2 NIM module" / "BSBE2-401A" araması
  - AliExpress: "satellite tuner module" araması
  - TBS TV tuner kartlarından söküm
- **Ayrık alternatif:** STV0910 + RT710 (stokta bulunursa)

### 3. RTL8822CS WiFi/BT Modülü
- **LCSC'de arama:** "RTL8822CS" veya "AP6256" ile kontrol
- AliExpress'ten modül olarak temin edilebilir

### 4. DDR4 RAM (K4A8G165WC)
- LCSC'de Samsung DDR4 sınırlı stok olabilir
- **Alternatifler:** Micron MT40A512M16, SK Hynix H5AN8G6NDJR

## LCSC/JLCPCB'den Temin Edilebilir Bileşenler

Aşağıdaki bileşenler LCSC kataloğunda mevcut ve JLCPCB SMT montaj ile yerleştirilebilir:

| Kategori | Parça Sayısı | Durum |
|----------|-------------|-------|
| Pasif (R, C, L) | ~150 | ✅ Tümü LCSC Basic |
| LDO/DC-DC | 5 | ✅ LCSC Extended |
| ESD Koruma | 4 | ✅ LCSC Extended |
| Konnektörler | 12 | ✅ LCSC Extended |
| LED'ler | 3 | ✅ LCSC Basic |
| Kristaller | 3 | ✅ LCSC Extended |
| IR Alıcı | 1 | ✅ LCSC Extended |
| MEMS Mikrofon | 2 | ⚠️ Kontrol gerekli |
| Ethernet PHY | 1 | ✅ LCSC Extended |
| LNBH26 | 1 | ✅ LCSC Extended |

## Maliyet Optimizasyonu İpuçları

1. **JLCPCB Basic Parts** kullanımını maksimize et (montaj ücreti düşük)
2. **Extended Parts** için minimum sipariş adedi kontrol et
3. **Pasif bileşenler:** 0402 paket tercih et (PCB alanı tasarrufu)
4. **PCB:** 6 katman yerine 4 katmanla başla (maliyet %40 düşer), DDR4 routing zorlaşır ama PoC için yeterli
5. **İlk prototip:** SoC yerine geliştirme kartı kullan, sadece peripheral PCB tasarla

## Sipariş Planı

### Aşama 1: Geliştirme Kartı ile PoC ($50-80)
- Khadas VIM4 veya X96 Max Plus TV Box: ~$40-60
- USB DVB-S2 tuner (TBS 5580): ~$25-35

### Aşama 2: Prototip PCB ($150-200)
- JLCPCB PCB + SMT: ~$55
- Özel temin bileşenler: ~$35
- LCSC bileşenler: ~$30
- Kasa/soğutucu: ~$15
- Kargo/gümrük: ~$20-30

### Aşama 3: Tam Prototip ($200-250)
- Aşama 2 + BLE kumanda + anten + aksesuarlar
