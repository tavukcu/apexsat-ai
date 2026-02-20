# APEXSAT AI v1.0 - Detaylı Şematik Blok Diyagramı

## Tasarımcı: Halil Dinçer - Dinçer Tavukçuluk / APEX Serisi
## Tarih: 2026-02-20
## Revizyon: A

---

## 1. SİSTEM GENEL GÖRÜNÜM

```
                                    ┌─────────────────────┐
                                    │    12V DC INPUT      │
                                    │   (Barrel Jack)      │
                                    │   5.5x2.1mm, 3A     │
                                    └──────────┬──────────┘
                                               │
                              ┌────────────────┼────────────────┐
                              │         POWER MANAGEMENT         │
                              │                                  │
                              │  ┌──────────┐  ┌──────────┐    │
                              │  │ MP2315   │  │ LNBH26   │    │
                              │  │ 12V→5V   │  │ 12V→     │    │
                              │  │ 3A Buck  │  │ 13V/18V  │    │
                              │  └────┬─────┘  └────┬─────┘    │
                              │       │              │ (LNB)    │
                              │  ┌────┴────┐         │          │
                              │  │AP2112K  │         │          │
                              │  │5V→3.3V  │         │          │
                              │  │600mA LDO│         │          │
                              │  └────┬────┘         │          │
                              │       │              │          │
                              │  ┌────┴────┐ ┌──────┴──┐       │
                              │  │RT9193   │ │SY8088   │       │
                              │  │3.3V→    │ │5V→0.9V  │       │
                              │  │1.8V LDO │ │3A Buck  │       │
                              │  └────┬────┘ └────┬────┘       │
                              │       │           │             │
                              │       │      ┌────┴────┐       │
                              │       │      │MP8759   │       │
                              │       │      │5V→1.1V  │       │
                              │       │      │2A Buck  │       │
                              │       │      └────┬────┘       │
                              └───────┼───────────┼────────────┘
                                      │           │
            ┌─────────────────────────┼───────────┼─────────────────────────┐
            │                    POWER RAILS                                │
            │   5V ────── 3.3V ────── 1.8V ────── 1.1V ────── 0.9V        │
            └─────────────────────────┼───────────┼─────────────────────────┘
                                      │           │
```

---

## 2. ANA İŞLEMCİ BLOK (SoC Merkez)

```
                          ┌─────────────────────────────────────────────────────────┐
                          │                                                         │
 ┌──────────────────┐     │            AMLOGIC S905X4-J (BGA-272)                   │
 │ DDR4 SDRAM       │     │                                                         │
 │ 4x K4A8G165WC   │     │  ┌────────────────────────────────────────────────────┐  │
 │ (4GB toplam)     │◄════╪══╡ DDR4 Interface                                    │  │
 │                  │     │  │ DQ[31:0], DQS[3:0]±, DM[3:0]                      │  │
 │ FBGA-96 x4      │     │  │ A[15:0], BA[1:0], BG[0], CS#, RAS#, CAS#, WE#    │  │
 │ VDD: 1.1V       │     │  │ CK±, CKE, ODT, RESET#                             │  │
 │ VDDQ: 1.1V      │     │  │ 32-bit bus, DDR4-2400/2666                         │  │
 │ VPP: 2.5V       │     │  └────────────────────────────────────────────────────┘  │
 └──────────────────┘     │                                                         │
                          │  ┌────────────────────────────────────────────────────┐  │
 ┌──────────────────┐     │  │ eMMC 5.1 Interface                                │  │
 │ eMMC 32GB        │◄════╪══╡ DAT[7:0], CMD, CLK, DS, RST#                     │  │
 │ KLMAG1JETD       │     │  │ 8-bit bus, HS400 200MHz                           │  │
 │ FBGA-153         │     │  └────────────────────────────────────────────────────┘  │
 │ VCC: 3.3V        │     │                                                         │
 │ VCCQ: 1.8V       │     │  ┌────────────────────────────────────────────────────┐  │
 └──────────────────┘     │  │ SD/SDIO Interface                                 │  │
                          │  │ DAT[3:0], CMD, CLK                                │  │
 ┌──────────────────┐     │  │ 4-bit bus, SDR50 100MHz                           │  │
 │ microSD Slot     │◄════╪══╡ (paylaşımlı: SD kart VEYA WiFi modül)            │  │
 │ UHS-I            │     │  └────────────────────────────────────────────────────┘  │
 │ VCC: 3.3V        │     │                                                         │
 └──────────────────┘     │  ┌────────────────────────────────────────────────────┐  │
                          │  │ SDIO Interface (WiFi)                              │  │
 ┌──────────────────┐     │  │ DAT[3:0], CMD, CLK                                │  │
 │ RTL8822CS        │◄════╪══╡ 4-bit SDIO 3.0                                   │  │
 │ WiFi/BT Module   │     │  │                                                    │  │
 │ VDD: 3.3V        │     │  │ UART (BT): TXD, RXD, CTS, RTS                    │  │
 │                  │◄════╪══╡ BT HCI UART @ 3Mbps                              │  │
 │ 2x u.FL antenna  │     │  │                                                    │  │
 └──────────────────┘     │  │ Host wake: BT_WAKE, WL_WAKE (GPIO)               │  │
                          │  └────────────────────────────────────────────────────┘  │
                          │                                                         │
                          │  ┌────────────────────────────────────────────────────┐  │
 ┌──────────────────┐     │  │ HDMI 2.0b TX                                      │  │
 │ HDMI Type-A      │◄════╪══╡ TMDS[2:0]±, TMDS_CLK±ℽ (100Ω differential)       │  │
 │ Connector        │     │  │ HPD (Hot Plug Detect)                              │  │
 │ + IP4791CZ12 ESD │     │  │ DDC: SDA, SCL (I2C)                               │  │
 │                  │     │  │ CEC (Consumer Electronics Control)                 │  │
 │                  │     │  │ 5V HDMI power (from 5V rail, via ferrite)          │  │
 │                  │     │  │ 4K@60Hz, HDR10, HLG, HDCP 2.2                     │  │
 └──────────────────┘     │  └────────────────────────────────────────────────────┘  │
                          │                                                         │
                          │  ┌────────────────────────────────────────────────────┐  │
 ┌──────────────────┐     │  │ USB 3.0 (SuperSpeed + USB 2.0)                    │  │
 │ USB 3.0 Type-A   │◄════╪══╡ SSTX±, SSRX± (90Ω diff) + D±                    │  │
 │ + ESD (IP4220)   │     │  │ VBUS: 5V via load switch                          │  │
 └──────────────────┘     │  └────────────────────────────────────────────────────┘  │
                          │                                                         │
 ┌──────────────────┐     │  ┌────────────────────────────────────────────────────┐  │
 │ USB 2.0 Type-A   │◄════╪══╡ USB 2.0 Host Port 1: D±                          │  │
 │ x2 + ESD         │     │  │ USB 2.0 Host Port 2: D±                          │  │
 └──────────────────┘     │  │ VBUS: 5V via polyfuse                             │  │
                          │  └────────────────────────────────────────────────────┘  │
 ┌──────────────────┐     │  ┌────────────────────────────────────────────────────┐  │
 │ USB-C (OTG/DBG)  │◄════╪══╡ USB 2.0 OTG: D±, ID, VBUS                       │  │
 │ + ESD            │     │  │ CC1, CC2 (USB-C config)                           │  │
 └──────────────────┘     │  └────────────────────────────────────────────────────┘  │
                          │                                                         │
                          │  ┌────────────────────────────────────────────────────┐  │
 ┌──────────────────┐     │  │ Ethernet RGMII                                    │  │
 │ RTL8211F-CG      │◄════╪══╡ TXD[3:0], TX_CLK, TX_EN (50Ω)                   │  │
 │ Gigabit PHY      │     │  │ RXD[3:0], RX_CLK, RX_DV (50Ω)                   │  │
 │ QFN-48           │     │  │ MDC, MDIO (management)                            │  │
 │ VDD: 3.3V/1.8V   │     │  │ INT#, RESET# (GPIO)                              │  │
 │         ↓        │     │  └────────────────────────────────────────────────────┘  │
 │ ┌──────────────┐ │     │                                                         │
 │ │ RJ45 Magjack │ │     │  ┌────────────────────────────────────────────────────┐  │
 │ │ HR911105A    │ │     │  │ I2C Bus 0 (Tuner/NIM kontrol)                     │  │
 │ │ LED'li       │ │     │  │ SDA0, SCL0 @ 400kHz                               │  │
 │ └──────────────┘ │     │  │ → DVB-S2 NIM (tuner + demod)                      │  │
 └──────────────────┘     │  │ → LNBH26 (LNB güç kontrolü)                      │  │
                          │  └────────────────────────────────────────────────────┘  │
                          │                                                         │
                          │  ┌────────────────────────────────────────────────────┐  │
                          │  │ I2C Bus 1 (Aksesuar)                               │  │
                          │  │ SDA1, SCL1 @ 100kHz                                │  │
                          │  │ → OLED Display SSD1306 (0x3C)                      │  │
                          │  │ → INMP441 Mikrofon x2 (I2S alt)                   │  │
                          │  └────────────────────────────────────────────────────┘  │
                          │                                                         │
                          │  ┌────────────────────────────────────────────────────┐  │
 ┌──────────────────┐     │  │ TS Parallel Input (DVB Transport Stream)           │  │
 │ DVB-S2 NIM       │════>╪══╡ TS_CLK, TS_VALID, TS_SYNC, TS_D[7:0]            │  │
 │ (BSBE2 uyumlu)   │     │  │ 8-bit parallel, max 96 MHz                        │  │
 │ veya             │     │  │                                                    │  │
 │ STV0910+RT710    │     │  │ Alternatif: TS Serial (TS_CLK, TS_DATA)           │  │
 └──────────────────┘     │  └────────────────────────────────────────────────────┘  │
                          │                                                         │
                          │  ┌────────────────────────────────────────────────────┐  │
                          │  │ I2S Audio Output                                   │  │
 ┌──────────────────┐     │  │ I2S_BCLK, I2S_LRCLK, I2S_DOUT                    │  │
 │ Audio DAC        │◄════╪══╡ → 3.5mm AV Jack (CVBS+Audio via RC filter)       │  │
 │ (SoC internal)   │     │  │                                                    │  │
 └──────────────────┘     │  │ SPDIF_OUT                                          │  │
                          │  │ → TOSLINK Optik Konnektör (PLT133)                │  │
 ┌──────────────────┐     │  └────────────────────────────────────────────────────┘  │
 │ TOSLINK TX       │◄════╪══╝                                                     │
 └──────────────────┘     │                                                         │
                          │  ┌────────────────────────────────────────────────────┐  │
                          │  │ I2S Audio Input (Mikrofon)                         │  │
 ┌──────────────────┐     │  │ I2S_DIN, I2S_BCLK_IN, I2S_LRCLK_IN              │  │
 │ 2x INMP441       │════>╪══╡ 2 kanal dijital MEMS mikrofon                    │  │
 │ MEMS Mikrofon    │     │  │ Sol: WS=LOW, Sağ: WS=HIGH                        │  │
 │ VDD: 3.3V        │     │  └────────────────────────────────────────────────────┘  │
 └──────────────────┘     │                                                         │
                          │  ┌────────────────────────────────────────────────────┐  │
                          │  │ GPIO / Kontrol                                     │  │
 ┌──────────────────┐     │  │ GPIOD_5  → IR_IN (TSOP38238, 38kHz)              │  │
 │ TSOP38238 IR     │════>╪══╡ GPIOD_6  → IR_OUT (IR LED, opsiyonel)            │  │
 │                  │     │  │ GPIOD_10 → LED_POWER (Kırmızı)                   │  │
 │ IR LED (TX)      │◄════╪══╡ GPIOD_11 → LED_STATUS (Yeşil)                    │  │
 │                  │     │  │ GPIOD_12 → LED_BT (Mavi)                          │  │
 │ 3x LED           │◄════╪══╡ GPIOH_4  → FAN_PWM (30mm fan)                    │  │
 │                  │     │  │ GPIOH_5  → ETH_RESET# (RTL8211F)                 │  │
 │ Fan (PWM)        │◄════╪══╡ GPIOH_6  → WIFI_EN (RTL8822CS enable)            │  │
 │                  │     │  │ GPIOH_7  → NIM_RESET# (DVB tuner reset)          │  │
 │ Reset SW         │════>╪══╡ GPIOH_8  → RESET_SW (tact switch, pull-up)       │  │
 │ Power SW         │════>╪══╡ GPIOH_9  → POWER_SW (power button)               │  │
 └──────────────────┘     │  └────────────────────────────────────────────────────┘  │
                          │                                                         │
                          │  ┌────────────────────────────────────────────────────┐  │
                          │  │ UART                                               │  │
 ┌──────────────────┐     │  │ UART_AO_TX, UART_AO_RX → Debug Header (115200)   │  │
 │ Debug Header     │◄════╪══╡ UART_A_TX, UART_A_RX   → BT HCI (RTL8822CS)     │  │
 │ (4-pin, 3.3V)    │     │  └────────────────────────────────────────────────────┘  │
 └──────────────────┘     │                                                         │
                          │  ┌────────────────────────────────────────────────────┐  │
                          │  │ Kristal / Clock                                    │  │
 ┌──────────────────┐     │  │ XTAL_IN, XTAL_OUT → 24MHz kristal (22pF load)    │  │
 │ 24MHz XTAL       │════>╪══╡ RTC_CLK → 32.768kHz kristal (6pF load)           │  │
 │ 32.768kHz XTAL   │════>╪══╡                                                   │  │
 └──────────────────┘     │  └────────────────────────────────────────────────────┘  │
                          │                                                         │
                          └─────────────────────────────────────────────────────────┘
```

---

## 3. DVB-S2 FRONTEND DETAY

```
                                            ┌───────────────┐
                                            │  75Ω F-Type   │
                                            │  Connector    │
                      LNB Kablosu           │  (LNB IN)     │
    ◄─────────────────────────────────────  │  Center: RF   │
    LNB                                     │  Shield: GND  │
    (Çanak üzerinde)                        └───────┬───────┘
                                                    │
                                                    │ RF Signal (950-2150 MHz)
                                                    │ + DC (13V veya 18V)
                                                    │
                                            ┌───────┴───────┐
                                            │   LNBH26PQR   │
                                            │   (QFN-24)    │
                                            │               │
                                 12V ──────>│ VIN           │
                                            │               │
                          I2C_SDA ─────────>│ SDA     VOUT ─┼──> LNB besleme
                          I2C_SCL ─────────>│ SCL          │    (13V/18V + 22kHz)
                                            │               │
                              DSQIN ───────>│ DSQIN        │    DiSEqC pulse in
                              DSQOUT <──────│ DSQOUT       │    DiSEqC pulse out
                                            │               │
                                  GND ─────>│ GND     EN ──┼──< LNBH_EN (GPIO)
                                            │               │
                                            │ OCP# ────────┼──> overcurrent flag
                                            │ OTF  ────────┼──> over-temp flag
                                            └───────────────┘
                                                    │
                                                    │ (RF + DC combined)
                                                    │
                                ┌───────────────────┴──────────────────────────┐
                                │                                              │
                      Opsiyon A: NIM Modülü            Opsiyon B: Ayrık Çipler
                                │                                              │
                    ┌───────────┴───────────┐      ┌──────────────────────────┐
                    │  DVB-S2 NIM Module    │      │  Tuner: RT710 (QFN-24)  │
                    │  (BSBE2-401A uyumlu)  │      │  950-2150 MHz           │
                    │                       │      │  IF/IQ output           │
                    │  İçerik:              │      │         │               │
                    │  - CX24116 demod      │      │         ▼               │
                    │  - Tuner IC           │      │  Demod: STV0910        │
                    │  - RF frontend        │      │  (QFN-64)              │
                    │                       │      │  DVB-S/S2/S2X          │
                    │  Arayüz:             │      │  Dual tuner capable    │
                    │  - I2C (kontrol)      │      │                        │
                    │  - TS Parallel/Serial │      │  Arayüz:              │
                    │  - 5V veya 3.3V VCC   │      │  - I2C (0x68/0x6A)    │
                    │                       │      │  - TS Parallel 8-bit   │
                    └───────────┬───────────┘      └──────────┬─────────────┘
                                │                              │
                                │  Ortak Çıkış:                │
                                │                              │
                                ▼                              ▼
                    ┌──────────────────────────────────────────────────┐
                    │  Transport Stream Bus → S905X4 TS Input          │
                    │                                                  │
                    │  TS_CLK    ──────────> SoC TS_CLK               │
                    │  TS_VALID  ──────────> SoC TS_VALID             │
                    │  TS_SYNC   ──────────> SoC TS_SYNC              │
                    │  TS_D[7:0] ──────────> SoC TS_D[7:0]           │
                    │                                                  │
                    │  I2C_SDA   <─────────> SoC I2C0_SDA (4.7kΩ PU) │
                    │  I2C_SCL   <─────────> SoC I2C0_SCL (4.7kΩ PU) │
                    │  NIM_RST#  <────────── SoC GPIOH_7              │
                    └──────────────────────────────────────────────────┘
```

---

## 4. ETHERNET DETAY

```
                    ┌─────────────┐         ┌──────────────┐        ┌──────────────┐
                    │  S905X4     │  RGMII  │  RTL8211F-CG │  MDI   │  HR911105A   │
                    │  MAC        │         │  PHY         │        │  RJ45+Mag    │
                    │             │         │  (QFN-48)    │        │              │
                    │  TXD[3:0] ─┼────────>│  TXD[3:0]   │        │              │
                    │  TX_CLK   ─┼────────>│  TX_CLK     │        │              │
                    │  TX_EN    ─┼────────>│  TX_EN      │        │              │
                    │             │         │             │        │              │
                    │  RXD[3:0] ─┼<────────│  RXD[3:0]   │  MDI±  │   1 ── TX+   │
                    │  RX_CLK   ─┼<────────│  RX_CLK     │──────>│   2 ── TX-   │
                    │  RX_DV    ─┼<────────│  RX_DV      │──────>│   3 ── RX+   │
                    │             │         │             │──────>│   6 ── RX-   │
                    │  MDC      ─┼────────>│  MDC        │──────>│   4 ── BI_D+ │
                    │  MDIO     ─┼<──────>│  MDIO       │──────>│   5 ── BI_D- │
                    │             │         │             │──────>│   7 ── BI_C+ │
                    │  ETH_RST# ─┼────────>│  PHYRST#    │──────>│   8 ── BI_C- │
                    │  ETH_INT# ─┼<────────│  INTB       │        │              │
                    │             │         │             │        │  LED_GREEN ──│── Yeşil LED
                    └─────────────┘         │  XTAL_IN ───│── 25MHz│  LED_YELLOW ─│── Sarı LED
                                            │  XTAL_OUT ──│── xtal │              │
                                            │             │        │  Shield ─────│── GND
                                            │  AVDD10:1.0V│        └──────────────┘
                                            │  AVDD33:3.3V│
                                            │  DVDD10:1.0V│ (internal reg)
                                            │  DVDDIO:3.3V│
                                            └──────────────┘
                                                    │
                                            49.9Ω seri rezistör
                                            her RGMII sinyal hattında
```

---

## 5. USB PORTLARI DETAY

```
                    ┌─────────────┐
                    │  S905X4     │
                    │             │
                    │  USB3_DP   ─┼──┐  90Ω diff pair
                    │  USB3_DM   ─┼──┤  (SuperSpeed)
                    │  USB2_DP   ─┼──┤  90Ω diff pair
                    │  USB2_DM   ─┼──┤  (High Speed)
                    │             │  │
                    │  USB_H1_DP ─┼──┤──── USB 2.0 Host 1
                    │  USB_H1_DM ─┼──┤
                    │             │  │
                    │  USB_H2_DP ─┼──┤──── USB 2.0 Host 2
                    │  USB_H2_DM ─┼──┤
                    │             │  │
                    │  USB_OTG_DP┼──┤──── USB OTG (USB-C)
                    │  USB_OTG_DM┼──┤
                    │  USB_OTG_ID┼──┘
                    └─────────────┘
                         │  │  │  │
                         ▼  ▼  ▼  ▼
            ┌────────────────────────────────────────────┐
            │              ESD Koruması                   │
            │         IP4220CZ6 (her port için)           │
            └────────────┬───────┬───────┬───────┬──────┘
                         │       │       │       │
                    ┌────┴──┐ ┌─┴────┐ ┌┴────┐ ┌┴──────┐
                    │USB 3.0│ │USB2.0│ │USB2.0│ │USB-C  │
                    │Type-A │ │Type-A│ │Type-A│ │(OTG)  │
                    │       │ │  #1  │ │  #2  │ │       │
                    │VBUS:5V│ │VBUS  │ │VBUS  │ │VBUS:5V│
                    │via SW │ │PTC   │ │PTC   │ │via CC │
                    └───────┘ └──────┘ └──────┘ └───────┘
                        │         │        │         │
                      500mA     500mA    500mA    1.5A max
```

---

## 6. AUDIO SUBSYSTEM DETAY

```
                    ┌─────────────┐
                    │  S905X4     │
                    │             │
                    │  I2S_BCLK ──┼──────┐
                    │  I2S_LRCLK ─┼──────┤  I2S Output
                    │  I2S_DOUT ──┼──────┤  (Audio DAC)
                    │             │      │
                    │  I2S_DIN  ──┼──┐   │
                    │  I2S_BCLK_I─┼──┤   │  I2S Input (Mikrofon)
                    │  I2S_LRCLK_I┼──┤   │
                    │             │  │   │
                    │  SPDIF_OUT ─┼──┼───┼───────────────────────┐
                    │             │  │   │                       │
                    └─────────────┘  │   │                       │
                                     │   │                       │
                              ┌──────┘   │                       │
                              │          │                       │
                    ┌─────────┴────┐     │              ┌────────┴──────┐
                    │  INMP441 x2  │     │              │  TOSLINK TX   │
                    │  MEMS Mic    │     │              │  PLT133/T10W  │
                    │              │     │              │               │
                    │  L: WS=GND  │     │              │  SPDIF ──> Optik │
                    │  R: WS=VDD  │     │              │               │
                    │              │     │              └───────────────┘
                    │  VDD: 3.3V  │     │
                    │  SCK: I2S_BCLK    │
                    │  SD: I2S_DIN │     │
                    │  WS: I2S_LRCLK    │
                    └──────────────┘     │
                                         │
                              ┌──────────┴──────────┐
                              │  Analog Audio Out    │
                              │                      │
                              │  I2S → DAC (internal)│
                              │  → RC Low-Pass Filter│
                              │  → 3.5mm TRRS Jack   │
                              │                      │
                              │  Tip:  CVBS Video    │
                              │  Ring1: Audio L      │
                              │  Ring2: Audio R      │
                              │  Sleeve: GND         │
                              └─────────────────────┘
```

---

## 7. SINYAL İMPEDANS ÖZETİ

| Sinyal | Tip | İmpedans | Max Uzunluk | Eşleşme Toleransı |
|--------|-----|----------|-------------|-------------------|
| DDR4 DQ/DQS | Differential | 80Ω diff / 40Ω SE | 50mm | ±2mm grupiçi |
| DDR4 Addr/Cmd | Single-ended | 40Ω | 80mm | ±5mm |
| DDR4 CK | Differential | 80Ω diff | 50mm | ±1mm |
| HDMI TMDS | Differential | 100Ω ±10% | 100mm | ±0.5mm pair |
| USB 3.0 SS | Differential | 90Ω ±10% | 80mm | ±0.5mm pair |
| USB 2.0 | Differential | 90Ω ±10% | 150mm | ±2mm pair |
| RGMII | Single-ended | 50Ω ±10% | 50mm | ±5mm grupiçi |
| TS Parallel | Single-ended | 50Ω | 80mm | ±10mm |
| I2C | Single-ended | N/A | 200mm | N/A |
| SPDIF | Single-ended | 75Ω | 100mm | N/A |

---

## 8. GÜÇ RAİL ÖZETİ

| Rail | Voltaj | Max Akım | Regülatör | Kullananlar |
|------|--------|----------|-----------|-------------|
| VIN | 12V | 3A | - | Giriş |
| 5V | 5.0V | 3A | MP2315 | USB VBUS, HDMI, LDO giriş |
| 3.3V | 3.3V | 2A | AP2112K x2 | eMMC, SD, WiFi, ETH, IR, MIC, LNBH |
| 1.8V | 1.8V | 1A | RT9193 | DDR4 VDD, eMMC VCCQ |
| 1.1V | 1.1V | 2A | MP8759 | SoC GPU/NPU, DDR4 VDDQ |
| VDDCORE | 0.9V | 3A | SY8088 | SoC CPU Core |
| LNB_PWR | 13/18V | 500mA | LNBH26 | LNB (F-connector) |
