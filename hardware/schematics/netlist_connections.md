# APEXSAT AI v1.0 - Pin-Pin Bağlantı Tablosu (Netlist)

## Tasarımcı: Halil Dinçer
## Tarih: 2026-02-20 | Revizyon: A

> **Not:** Amlogic S905X4 pin numaraları, Amlogic referans tasarımı ve
> CoreELEC/LibreELEC topluluk dokümanlarına dayanmaktadır.
> BGA ball map'i OEM SDK ile doğrulanmalıdır.
> Amlogic BGA-272 (15x15mm, 0.65mm pitch) kullanır.

---

## 1. DDR4 BELLEK BAĞLANTILARI

### S905X4 → DDR4 (K4A8G165WC-BCWE x4 = 4GB, 32-bit bus)

#### Byte Lane 0 (Chip U2-A, DQ[7:0])

| Kaynak IC | Kaynak Pin | Sinyal Adı | Hedef IC | Hedef Pin | İmpedans | Not |
|-----------|-----------|------------|----------|----------|----------|-----|
| S905X4 | AE3 | DDR4_DQ0 | U2-A | A3 (DQ0) | 40Ω SE | Length match ±2mm |
| S905X4 | AF3 | DDR4_DQ1 | U2-A | B8 (DQ1) | 40Ω SE | Length match ±2mm |
| S905X4 | AE4 | DDR4_DQ2 | U2-A | C3 (DQ2) | 40Ω SE | Length match ±2mm |
| S905X4 | AF4 | DDR4_DQ3 | U2-A | C7 (DQ3) | 40Ω SE | Length match ±2mm |
| S905X4 | AD3 | DDR4_DQ4 | U2-A | C2 (DQ4) | 40Ω SE | Length match ±2mm |
| S905X4 | AD4 | DDR4_DQ5 | U2-A | C8 (DQ5) | 40Ω SE | Length match ±2mm |
| S905X4 | AC3 | DDR4_DQ6 | U2-A | D3 (DQ6) | 40Ω SE | Length match ±2mm |
| S905X4 | AC4 | DDR4_DQ7 | U2-A | D7 (DQ7) | 40Ω SE | Length match ±2mm |
| S905X4 | AE5 | DDR4_DQS0_P | U2-A | A7 (DQS_t) | 80Ω diff | Differential pair |
| S905X4 | AF5 | DDR4_DQS0_N | U2-A | B7 (DQS_c) | 80Ω diff | Differential pair |
| S905X4 | AD5 | DDR4_DM0 | U2-A | B3 (DM/DBI) | 40Ω SE | Data mask |

#### Byte Lane 1 (Chip U2-B, DQ[15:8])

| Kaynak IC | Kaynak Pin | Sinyal Adı | Hedef IC | Hedef Pin | İmpedans | Not |
|-----------|-----------|------------|----------|----------|----------|-----|
| S905X4 | AB3 | DDR4_DQ8 | U2-B | A3 (DQ0) | 40Ω SE | Length match ±2mm |
| S905X4 | AB4 | DDR4_DQ9 | U2-B | B8 (DQ1) | 40Ω SE | Length match ±2mm |
| S905X4 | AA3 | DDR4_DQ10 | U2-B | C3 (DQ2) | 40Ω SE | Length match ±2mm |
| S905X4 | AA4 | DDR4_DQ11 | U2-B | C7 (DQ3) | 40Ω SE | Length match ±2mm |
| S905X4 | Y3 | DDR4_DQ12 | U2-B | C2 (DQ4) | 40Ω SE | Length match ±2mm |
| S905X4 | Y4 | DDR4_DQ13 | U2-B | C8 (DQ5) | 40Ω SE | Length match ±2mm |
| S905X4 | W3 | DDR4_DQ14 | U2-B | D3 (DQ6) | 40Ω SE | Length match ±2mm |
| S905X4 | W4 | DDR4_DQ15 | U2-B | D7 (DQ7) | 40Ω SE | Length match ±2mm |
| S905X4 | AB5 | DDR4_DQS1_P | U2-B | A7 (DQS_t) | 80Ω diff | |
| S905X4 | AA5 | DDR4_DQS1_N | U2-B | B7 (DQS_c) | 80Ω diff | |
| S905X4 | Y5 | DDR4_DM1 | U2-B | B3 (DM/DBI) | 40Ω SE | |

#### Byte Lane 2 (Chip U2-C, DQ[23:16])

| Kaynak IC | Kaynak Pin | Sinyal Adı | Hedef IC | Hedef Pin | İmpedans | Not |
|-----------|-----------|------------|----------|----------|----------|-----|
| S905X4 | V3-V4, U3-U4, T3-T4, R3-R4 | DDR4_DQ[23:16] | U2-C | DQ[7:0] | 40Ω SE | Byte Lane 0/1 ile aynı yapı |
| S905X4 | V5 | DDR4_DQS2_P | U2-C | DQS_t | 80Ω diff | |
| S905X4 | U5 | DDR4_DQS2_N | U2-C | DQS_c | 80Ω diff | |
| S905X4 | T5 | DDR4_DM2 | U2-C | DM/DBI | 40Ω SE | |

#### Byte Lane 3 (Chip U2-D, DQ[31:24])

| Kaynak IC | Kaynak Pin | Sinyal Adı | Hedef IC | Hedef Pin | İmpedans | Not |
|-----------|-----------|------------|----------|----------|----------|-----|
| S905X4 | P3-P4, N3-N4, M3-M4, L3-L4 | DDR4_DQ[31:24] | U2-D | DQ[7:0] | 40Ω SE | |
| S905X4 | P5 | DDR4_DQS3_P | U2-D | DQS_t | 80Ω diff | |
| S905X4 | N5 | DDR4_DQS3_N | U2-D | DQS_c | 80Ω diff | |
| S905X4 | M5 | DDR4_DM3 | U2-D | DM/DBI | 40Ω SE | |

#### Address / Command (Ortak - tüm DDR4 chip'lere fly-by)

| Kaynak IC | Kaynak Pin | Sinyal Adı | Hedef | İmpedans | Not |
|-----------|-----------|------------|-------|----------|-----|
| S905X4 | K7 | DDR4_A0 | U2-A/B/C/D (R2) | 40Ω SE | Fly-by topology |
| S905X4 | K8 | DDR4_A1 | U2-A/B/C/D (T8) | 40Ω SE | |
| S905X4 | L7 | DDR4_A2 | U2-A/B/C/D (R7) | 40Ω SE | |
| S905X4 | L8 | DDR4_A3 | U2-A/B/C/D (P8) | 40Ω SE | |
| S905X4 | M7 | DDR4_A4 | U2-A/B/C/D (N2) | 40Ω SE | |
| S905X4 | M8 | DDR4_A5 | U2-A/B/C/D (N8) | 40Ω SE | |
| S905X4 | N7 | DDR4_A6 | U2-A/B/C/D (M2) | 40Ω SE | |
| S905X4 | N8 | DDR4_A7 | U2-A/B/C/D (L2) | 40Ω SE | |
| S905X4 | P7 | DDR4_A8 | U2-A/B/C/D (K2) | 40Ω SE | |
| S905X4 | P8 | DDR4_A9 | U2-A/B/C/D (L8) | 40Ω SE | |
| S905X4 | R7 | DDR4_A10 | U2-A/B/C/D (K8) | 40Ω SE | AP (auto precharge) |
| S905X4 | R8 | DDR4_A11 | U2-A/B/C/D (J2) | 40Ω SE | |
| S905X4 | T7 | DDR4_A12 | U2-A/B/C/D (J8) | 40Ω SE | BC# |
| S905X4 | T8 | DDR4_A13 | U2-A/B/C/D (H7) | 40Ω SE | |
| S905X4 | K9 | DDR4_BA0 | U2-A/B/C/D (M7) | 40Ω SE | Bank Address |
| S905X4 | L9 | DDR4_BA1 | U2-A/B/C/D (R8) | 40Ω SE | |
| S905X4 | M9 | DDR4_BG0 | U2-A/B/C/D (P7) | 40Ω SE | Bank Group |
| S905X4 | K10 | DDR4_RAS# | U2-A/B/C/D (P3) | 40Ω SE | (A16) |
| S905X4 | L10 | DDR4_CAS# | U2-A/B/C/D (P2) | 40Ω SE | (A15) |
| S905X4 | M10 | DDR4_WE# | U2-A/B/C/D (N3) | 40Ω SE | (A14) |
| S905X4 | N10 | DDR4_CS0# | U2-A/B/C/D (G9) | 40Ω SE | Chip Select |
| S905X4 | P10 | DDR4_CKE0 | U2-A/B/C/D (H2) | 40Ω SE | Clock Enable |
| S905X4 | R10 | DDR4_ODT0 | U2-A/B/C/D (G7) | 40Ω SE | On-Die Term |
| S905X4 | K11 | DDR4_CK_P | U2-A/B/C/D (G2) | 80Ω diff | ±1mm match |
| S905X4 | L11 | DDR4_CK_N | U2-A/B/C/D (F2) | 80Ω diff | |
| S905X4 | T10 | DDR4_RESET# | U2-A/B/C/D (N7) | 40Ω SE | |

#### DDR4 Güç Bağlantıları (her chip için)

| Pin | Sinyal | Bağlantı | Not |
|-----|--------|----------|-----|
| VDD (x birden fazla) | DDR4_VDD | 1.1V rail | 100nF + 10µF bypass |
| VDDQ (x birden fazla) | DDR4_VDDQ | 1.1V rail | 100nF bypass, her pin yanında |
| VPP | DDR4_VPP | 2.5V (1.1V üzerinden LDO veya SoC internal) | Row activate power |
| VREF_DQ | DDR4_VREF | 0.55V (VDD/2 divider) | 100nF cap to GND |
| VSS | GND | GND plane | Düzlem bağlantısı |

---

## 2. eMMC BAĞLANTILARI

### S905X4 → eMMC (KLMAG1JETD-B041, FBGA-153)

| Kaynak IC | Kaynak Pin | Sinyal Adı | Hedef IC | Hedef Pin | Not |
|-----------|-----------|------------|----------|----------|-----|
| S905X4 | C12 | EMMC_CLK | U3 (eMMC) | H2 (CLK) | 50Ω, max 200MHz |
| S905X4 | D12 | EMMC_CMD | U3 (eMMC) | J1 (CMD) | 10kΩ pull-up to 1.8V |
| S905X4 | E12 | EMMC_D0 | U3 (eMMC) | H3 (DAT0) | |
| S905X4 | F12 | EMMC_D1 | U3 (eMMC) | H4 (DAT1) | |
| S905X4 | G12 | EMMC_D2 | U3 (eMMC) | J2 (DAT2) | |
| S905X4 | H12 | EMMC_D3 | U3 (eMMC) | J3 (DAT3) | |
| S905X4 | C13 | EMMC_D4 | U3 (eMMC) | G2 (DAT4) | |
| S905X4 | D13 | EMMC_D5 | U3 (eMMC) | G3 (DAT5) | |
| S905X4 | E13 | EMMC_D6 | U3 (eMMC) | G4 (DAT6) | |
| S905X4 | F13 | EMMC_D7 | U3 (eMMC) | F2 (DAT7) | |
| S905X4 | G13 | EMMC_DS | U3 (eMMC) | F3 (DS) | Data Strobe (HS400) |
| S905X4 | H13 | EMMC_RST# | U3 (eMMC) | K1 (RST#) | 10kΩ pull-up |
| - | - | VCC | U3 (eMMC) | VCC pins | 3.3V |
| - | - | VCCQ | U3 (eMMC) | VCCQ pins | 1.8V |

---

## 3. HDMI BAĞLANTILARI

### S905X4 → HDMI Connector (J6) + ESD (U7 IP4791CZ12)

| Kaynak IC | Kaynak Pin | Sinyal Adı | Hedef IC/Konnektör | Hedef Pin | İmpedans | Not |
|-----------|-----------|------------|-------------------|----------|----------|-----|
| S905X4 | A1 | HDMI_TX2_P | J6 (HDMI) | 1 (TMDS D2+) | 100Ω diff | AC coupled 100nF |
| S905X4 | A2 | HDMI_TX2_N | J6 (HDMI) | 3 (TMDS D2-) | 100Ω diff | |
| S905X4 | B1 | HDMI_TX1_P | J6 (HDMI) | 4 (TMDS D1+) | 100Ω diff | AC coupled 100nF |
| S905X4 | B2 | HDMI_TX1_N | J6 (HDMI) | 6 (TMDS D1-) | 100Ω diff | |
| S905X4 | C1 | HDMI_TX0_P | J6 (HDMI) | 7 (TMDS D0+) | 100Ω diff | AC coupled 100nF |
| S905X4 | C2 | HDMI_TX0_N | J6 (HDMI) | 9 (TMDS D0-) | 100Ω diff | |
| S905X4 | D1 | HDMI_TXCLK_P | J6 (HDMI) | 10 (TMDS CLK+) | 100Ω diff | AC coupled 100nF |
| S905X4 | D2 | HDMI_TXCLK_N | J6 (HDMI) | 12 (TMDS CLK-) | 100Ω diff | |
| S905X4 | E1 | HDMI_HPD | J6 (HDMI) | 19 (HPD) | - | 100kΩ pull-down |
| S905X4 | E2 | HDMI_CEC | J6 (HDMI) | 13 (CEC) | - | 27kΩ pull-up to 3.3V |
| S905X4 | F1 | HDMI_SDA | J6 (HDMI) | 16 (SDA) | - | DDC I2C, 2.2kΩ PU |
| S905X4 | F2 | HDMI_SCL | J6 (HDMI) | 15 (SCL) | - | DDC I2C, 2.2kΩ PU |
| - | - | HDMI_5V | J6 (HDMI) | 18 (+5V) | - | 5V rail, ferrit bead |
| - | - | GND | J6 (HDMI) | 2,5,8,11,14,17 | - | Shield + signal GND |
| U7 (ESD) | 1-8 | ESD_D2±,D1±,D0±,CLK± | J6 pins | TMDS pins | - | IP4791CZ12, SOT-886 |

---

## 4. ETHERNET BAĞLANTILARI

### S905X4 → RTL8211F-CG (U6, QFN-40) → HR911105A (J5, RJ45)

| Kaynak IC | Kaynak Pin | Sinyal Adı | Hedef IC | Hedef Pin | Not |
|-----------|-----------|------------|----------|----------|-----|
| S905X4 | J1 | ETH_TXD0 | U6 (RTL8211F) | 37 (TXD0) | 49.9Ω seri R |
| S905X4 | J2 | ETH_TXD1 | U6 (RTL8211F) | 38 (TXD1) | 49.9Ω seri R |
| S905X4 | K1 | ETH_TXD2 | U6 (RTL8211F) | 39 (TXD2) | 49.9Ω seri R |
| S905X4 | K2 | ETH_TXD3 | U6 (RTL8211F) | 40 (TXD3) | 49.9Ω seri R |
| S905X4 | L1 | ETH_TX_CLK | U6 (RTL8211F) | 42 (TXC) | 125MHz RGMII |
| S905X4 | L2 | ETH_TX_EN | U6 (RTL8211F) | 41 (TXCTL) | |
| S905X4 | J3 | ETH_RXD0 | U6 (RTL8211F) | 32 (RXD0) | 49.9Ω seri R |
| S905X4 | J4 | ETH_RXD1 | U6 (RTL8211F) | 31 (RXD1) | 49.9Ω seri R |
| S905X4 | K3 | ETH_RXD2 | U6 (RTL8211F) | 30 (RXD2) | 49.9Ω seri R |
| S905X4 | K4 | ETH_RXD3 | U6 (RTL8211F) | 29 (RXD3) | 49.9Ω seri R |
| S905X4 | L3 | ETH_RX_CLK | U6 (RTL8211F) | 35 (RXC) | 125MHz RGMII |
| S905X4 | L4 | ETH_RX_DV | U6 (RTL8211F) | 33 (RXCTL) | |
| S905X4 | M1 | ETH_MDC | U6 (RTL8211F) | 44 (MDC) | Management |
| S905X4 | M2 | ETH_MDIO | U6 (RTL8211F) | 43 (MDIO) | 1.5kΩ PU to 3.3V |
| S905X4 | GPIOH_5 | ETH_RST# | U6 (RTL8211F) | 48 (PHYRST#) | 10kΩ PU, 10ms delay |
| U6 | 47 | ETH_INT# | S905X4 GPIOH_6 | - | 10kΩ PU, open-drain |

### RTL8211F → RJ45 Jack (HR911105A)

| Kaynak IC | Kaynak Pin | Sinyal Adı | Hedef | Hedef Pin | Not |
|-----------|-----------|------------|-------|----------|-----|
| U6 (RTL8211F) | 5 | MDI0_P (TXP_A) | J5 (RJ45) | 1 (TX+) | Manyetik entegre |
| U6 (RTL8211F) | 4 | MDI0_N (TXN_A) | J5 (RJ45) | 2 (TX-) | |
| U6 (RTL8211F) | 8 | MDI1_P (RXP_B) | J5 (RJ45) | 3 (RX+) | |
| U6 (RTL8211F) | 7 | MDI1_N (RXN_B) | J5 (RJ45) | 6 (RX-) | |
| U6 (RTL8211F) | 11 | MDI2_P (BID_C+) | J5 (RJ45) | 4 (BI_C+) | Gigabit |
| U6 (RTL8211F) | 10 | MDI2_N (BID_C-) | J5 (RJ45) | 5 (BI_C-) | |
| U6 (RTL8211F) | 14 | MDI3_P (BID_D+) | J5 (RJ45) | 7 (BI_D+) | Gigabit |
| U6 (RTL8211F) | 13 | MDI3_N (BID_D-) | J5 (RJ45) | 8 (BI_D-) | |
| U6 (RTL8211F) | 16 | LED_ACT | J5 (RJ45) | LED1 (Green) | Aktiflik LED |
| U6 (RTL8211F) | 17 | LED_LINK | J5 (RJ45) | LED2 (Yellow) | Link LED |

### RTL8211F Kristal

| Bağlantı | Pin | Not |
|----------|-----|-----|
| U6 Pin 22 (XTAL_IN) → Y1 (25MHz) Pin 1 | 22pF yükleme kapasitörler | |
| U6 Pin 21 (XTAL_OUT) → Y1 (25MHz) Pin 2 | C=22pF to GND her iki uç | |

### RTL8211F Güç

| Pin | Rail | Bypass |
|-----|------|--------|
| AVDD33 (Pin 1,2,3) | 3.3V | 100nF + 10µF |
| DVDD10 (internal) | - | 1µF + 100nF (Pin 23,24) |
| DVDDIO (Pin 45,46) | 3.3V (RGMII I/O) | 100nF |

### RTL8211F Strap Pins (Adres ve Mod Ayarı)

| Pin | Bağlantı | Değer | Açıklama |
|-----|----------|-------|----------|
| RXDV/PHYAD0 (Pin 33) | Pull-down 4.7kΩ | 0 | PHY Address bit 0 = 0 |
| RXD0/PHYAD1 (Pin 32) | Pull-down 4.7kΩ | 0 | PHY Address bit 1 = 0 |
| RXD1/PHYAD2 (Pin 31) | Pull-down 4.7kΩ | 0 | PHY Address bit 2 = 0 → Addr = 0x00 |
| RXD2/SELRGV (Pin 30) | Pull-up 4.7kΩ | 1 | RGMII mode seçimi |
| RXD3/INTSEL (Pin 29) | Pull-down 4.7kΩ | 0 | INT active low |
| TXDLY (Pin 26) | Pull-up 4.7kΩ | 1 | TX clock delay enable (RGMII) |
| RXDLY (Pin 27) | Pull-up 4.7kΩ | 1 | RX clock delay enable (RGMII) |

---

## 5. DVB-S2 FRONTEND BAĞLANTILARI

### S905X4 → DVB-S2 NIM (BSBE2 uyumlu veya STV0910)

| Kaynak IC | Kaynak Pin | Sinyal Adı | Hedef IC | Hedef Pin | Not |
|-----------|-----------|------------|----------|----------|-----|
| S905X4 | D7 | I2C0_SDA | NIM/STV0910 | SDA | 4.7kΩ PU to 3.3V |
| S905X4 | D8 | I2C0_SCL | NIM/STV0910 | SCL | 4.7kΩ PU to 3.3V |
| S905X4 | E7 | TS_CLK | NIM/STV0910 | TS_CLK | Parallel TS clock |
| S905X4 | E8 | TS_VALID | NIM/STV0910 | TS_VALID | Data valid |
| S905X4 | F7 | TS_SYNC | NIM/STV0910 | TS_SYNC | Sync byte marker |
| S905X4 | F8 | TS_D0 | NIM/STV0910 | TS_DATA0 | |
| S905X4 | G7 | TS_D1 | NIM/STV0910 | TS_DATA1 | |
| S905X4 | G8 | TS_D2 | NIM/STV0910 | TS_DATA2 | |
| S905X4 | H7 | TS_D3 | NIM/STV0910 | TS_DATA3 | |
| S905X4 | H8 | TS_D4 | NIM/STV0910 | TS_DATA4 | |
| S905X4 | E9 | TS_D5 | NIM/STV0910 | TS_DATA5 | |
| S905X4 | F9 | TS_D6 | NIM/STV0910 | TS_DATA6 | |
| S905X4 | G9 | TS_D7 | NIM/STV0910 | TS_DATA7 | |
| S905X4 | GPIOH_7 | NIM_RST# | NIM/STV0910 | RESET# | 10kΩ PU, active low |
| - | - | NIM_VCC | NIM | VCC | 5V veya 3.3V (modüle göre) |

### LNBH26PQR Bağlantıları (U4)

| Kaynak IC | Kaynak Pin | Sinyal Adı | Hedef | Hedef Pin | Not |
|-----------|-----------|------------|-------|----------|-----|
| S905X4 | D7 | I2C0_SDA | U4 (LNBH26) | 10 (SDA) | Paylaşımlı I2C0 bus |
| S905X4 | D8 | I2C0_SCL | U4 (LNBH26) | 9 (SCL) | I2C addr: 0x08 |
| U4 | 3 (VOUT) | LNB_POWER | J2 (F-Conn) | Center | 13V veya 18V |
| U4 | 4 (DSQOUT) | DISEQC_OUT | J2 (F-Conn) | Center | 22kHz+DiSEqC, AC coupled |
| U4 | 5 (DSQIN) | DISEQC_IN | J2 (F-Conn) | Center | DiSEqC reply detect |
| U4 | 1 (VIN) | 12V | 12V rail | - | Doğrudan 12V besleme |
| U4 | 8 (EN) | LNBH_EN | S905X4 GPIO | - | Enable, 10kΩ PU to 3.3V |
| U4 | 7 (OCP#) | LNB_OCP | S905X4 GPIO | - | Overcurrent flag |
| - | - | GND | U4 | 2,6,11,EP | Termal pad + GND |

### LNBH26 Bypass Kapasitörler

| Pin | Kapasitör | Not |
|-----|-----------|-----|
| VIN (Pin 1) | 100nF + 10µF (25V) | Giriş bypass |
| VOUT (Pin 3) | 100nF + 22µF (25V) | Çıkış bypass |

---

## 6. USB BAĞLANTILARI

### S905X4 → USB Konnektörler + ESD

| Kaynak IC | Kaynak Pin | Sinyal Adı | ESD IC | Konnektör | Not |
|-----------|-----------|------------|--------|-----------|-----|
| S905X4 | A5 | USB3_SSTX_P | U8a (IP4220) | J7 Pin 3 (SSTX+) | 90Ω diff |
| S905X4 | A6 | USB3_SSTX_N | U8a | J7 Pin 4 (SSTX-) | |
| S905X4 | B5 | USB3_SSRX_P | U8a | J7 Pin 5 (SSRX+) | 90Ω diff |
| S905X4 | B6 | USB3_SSRX_N | U8a | J7 Pin 6 (SSRX-) | |
| S905X4 | A7 | USB3_DP | U8a | J7 Pin 2 (D+) | 90Ω diff (USB2.0 companion) |
| S905X4 | A8 | USB3_DM | U8a | J7 Pin 3 (D-) | |
| S905X4 | B7 | USB2H1_DP | U8b (IP4220) | J8a Pin 2 (D+) | USB 2.0 Host 1 |
| S905X4 | B8 | USB2H1_DM | U8b | J8a Pin 3 (D-) | |
| S905X4 | C7 | USB2H2_DP | U8b | J8b Pin 2 (D+) | USB 2.0 Host 2 |
| S905X4 | C8 | USB2H2_DM | U8b | J8b Pin 3 (D-) | |
| S905X4 | D3 | USB_OTG_DP | U8c (IP4220) | J9 (USB-C) A6/B6 | OTG port |
| S905X4 | D4 | USB_OTG_DM | U8c | J9 (USB-C) A7/B7 | |
| S905X4 | D5 | USB_OTG_ID | - | J9 (USB-C) | CC pin ile belirle |
| - | - | VBUS_USB3 | J7 Pin 1 | 5V | 500mA polyfuse |
| - | - | VBUS_USB2 | J8a/b Pin 1 | 5V | 500mA polyfuse each |

---

## 7. WiFi / BLUETOOTH BAĞLANTILARI

### S905X4 → RTL8822CS (U5)

| Kaynak IC | Kaynak Pin | Sinyal Adı | Hedef IC | Hedef Pin | Not |
|-----------|-----------|------------|----------|----------|-----|
| S905X4 | G1 | SDIO_CLK | U5 (RTL8822CS) | SDIO_CLK | SDIO 3.0, max 208MHz |
| S905X4 | G2 | SDIO_CMD | U5 (RTL8822CS) | SDIO_CMD | 10kΩ PU |
| S905X4 | G3 | SDIO_D0 | U5 (RTL8822CS) | SDIO_D0 | 10kΩ PU |
| S905X4 | G4 | SDIO_D1 | U5 (RTL8822CS) | SDIO_D1 | 10kΩ PU |
| S905X4 | H1 | SDIO_D2 | U5 (RTL8822CS) | SDIO_D2 | 10kΩ PU |
| S905X4 | H2 | SDIO_D3 | U5 (RTL8822CS) | SDIO_D3 | 10kΩ PU |
| S905X4 | H3 | UART_A_TX | U5 (RTL8822CS) | BT_UART_RX | BT HCI, 3Mbps |
| S905X4 | H4 | UART_A_RX | U5 (RTL8822CS) | BT_UART_TX | |
| S905X4 | H5 | UART_A_CTS | U5 (RTL8822CS) | BT_UART_RTS | HW flow control |
| S905X4 | H6 | UART_A_RTS | U5 (RTL8822CS) | BT_UART_CTS | |
| S905X4 | GPIOH_6 | WIFI_EN | U5 (RTL8822CS) | CHIP_EN | WiFi power enable |
| S905X4 | GPIOH_10 | WL_WAKE | U5 (RTL8822CS) | WL_HOST_WAKE | WiFi wake interrupt |
| S905X4 | GPIOH_11 | BT_WAKE | U5 (RTL8822CS) | BT_HOST_WAKE | BT wake interrupt |
| U5 | ANT1 | RF_2G4 | J4a (u.FL) | Center | 2.4GHz anten |
| U5 | ANT2 | RF_5G | J4b (u.FL) | Center | 5GHz anten |
| - | - | VDD_WIFI | U5 VDD pins | 3.3V | 100nF + 10µF bypass |

---

## 8. AUDIO / IR / LED / GPIO BAĞLANTILARI

### Mikrofon (INMP441 x2)

| Kaynak IC | Kaynak Pin | Sinyal Adı | Hedef IC | Hedef Pin | Not |
|-----------|-----------|------------|----------|----------|-----|
| S905X4 | P1 | I2S_BCLK_IN | U9a/U9b | SCK | Bit clock (ortak) |
| S905X4 | P2 | I2S_LRCLK_IN | U9a/U9b | WS | Word select (ortak) |
| U9a | SD | I2S_DIN_L | S905X4 Q1 | I2S_DIN | Sol kanal (WS=LOW) |
| U9b | SD | I2S_DIN_R | S905X4 Q1 | I2S_DIN | Sağ kanal (WS=HIGH) |
| U9a | L/R | MIC_SEL_L | GND | - | Sol = GND |
| U9b | L/R | MIC_SEL_R | 3.3V | - | Sağ = VDD |

### IR Alıcı (TSOP38238)

| Bağlantı | Pin | Not |
|----------|-----|-----|
| TSOP38238 Pin 1 (OUT) → S905X4 GPIOD_5 | - | Open collector, 10kΩ PU to 3.3V |
| TSOP38238 Pin 2 (GND) → GND | - | |
| TSOP38238 Pin 3 (VCC) → 3.3V | - | 100nF + 4.7µF bypass |

### LED'ler (GPIO → R → LED → GND)

| GPIO | Sinyal | Seri R | LED | Renk |
|------|--------|--------|-----|------|
| S905X4 GPIOD_10 | LED_PWR | 1kΩ | D3 | Kırmızı |
| S905X4 GPIOD_11 | LED_STATUS | 1kΩ | D4 | Yeşil |
| S905X4 GPIOD_12 | LED_BT | 1kΩ | D5 | Mavi |

### Fan PWM

| Bağlantı | Not |
|----------|-----|
| S905X4 GPIOH_4 (PWM_E) → Q1 (AO3400A) Gate | 10kΩ pull-down |
| Q1 Drain → FAN- (30mm fan negatif) | |
| Q1 Source → GND | |
| FAN+ → 5V rail | |
| 1N4148 fly-back diode: FAN+ → FAN- (katot → anot) | Motor koruması |

### Debug UART Header (J_DBG, 4-pin, 2.54mm)

| Header Pin | SoC Pin | Sinyal | Not |
|-----------|---------|--------|-----|
| 1 | - | GND | |
| 2 | UART_AO_TX | TX | 3.3V CMOS, 115200 baud |
| 3 | UART_AO_RX | RX | 3.3V CMOS |
| 4 | - | 3.3V | Referans (bağlama opsiyonel) |

### Kristal Osilatörler

| Kristal | Frekans | SoC Pinleri | Yükleme Cap | Not |
|---------|---------|-------------|-------------|-----|
| Y2 (24MHz) | 24.000 MHz | XTAL_IN, XTAL_OUT | 2x 22pF to GND | Ana SoC clock |
| Y3 (32.768kHz) | 32.768 kHz | RTC_CLK_IN, RTC_CLK_OUT | 2x 6.8pF to GND | RTC |
| Y1 (25MHz) | 25.000 MHz | RTL8211F Pin 22/21 | 2x 22pF to GND | Ethernet PHY |

---

## 9. BYPASS KAPASİTÖR ATAMA TABLOSU

| IC | Pin Grubu | Kapasitör | Değer | Sayı | Yerleşim |
|----|-----------|-----------|-------|------|----------|
| S905X4 | VDDCORE (0.9V) | C_CORE | 100nF 0402 | 8 | Her VDD pin yanında |
| S905X4 | VDDCORE (0.9V) | C_CORE_BULK | 10µF 0805 | 2 | SoC kenarı |
| S905X4 | VDDGPU (1.1V) | C_GPU | 100nF 0402 | 4 | Her VDD pin yanında |
| S905X4 | VDDGPU (1.1V) | C_GPU_BULK | 10µF 0805 | 1 | SoC kenarı |
| S905X4 | VDDIO_3.3V | C_IO33 | 100nF 0402 | 6 | |
| S905X4 | VDDIO_1.8V | C_IO18 | 100nF 0402 | 4 | |
| S905X4 | AVDD (analog) | C_AVDD | 100nF + 1µF | 2+2 | Sessiz bölge |
| DDR4 x4 | VDD, VDDQ | C_DDR | 100nF 0402 | 16 | Her chip, her pin |
| DDR4 x4 | VDD, VDDQ | C_DDR_BULK | 10µF 0805 | 4 | Her chip 1 adet |
| eMMC | VCC, VCCQ | C_EMMC | 100nF + 10µF | 2+2 | IC yanında |
| RTL8211F | AVDD, DVDDIO | C_ETH | 100nF 0402 | 6 | Her güç pin |
| RTL8822CS | VDD | C_WIFI | 100nF + 10µF | 2+1 | Modül yanında |
| LNBH26 | VIN, VOUT | C_LNB | 100nF + 22µF | 2+2 | Giriş/çıkış |
| MP2315 | IN, OUT | C_BUCK5V | 22µF + 100µF | 1+1 | Giriş/çıkış |
| SY8088 | IN, OUT | C_BUCK09 | 22µF + 100µF | 1+1 | |
| MP8759 | IN, OUT | C_BUCK11 | 22µF + 100µF | 1+1 | |

**Toplam bypass kapasitör: ~90 adet**
