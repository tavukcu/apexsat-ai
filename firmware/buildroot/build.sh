#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# APEXSAT AI - Buildroot İmaj Oluşturma Scripti
# ═══════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
BUILDROOT_DIR="${SCRIPT_DIR}/buildroot-src"
BUILDROOT_VERSION="2024.02.1"
BUILDROOT_URL="https://buildroot.org/downloads/buildroot-${BUILDROOT_VERSION}.tar.xz"
OUTPUT_DIR="${SCRIPT_DIR}/output"
EXTERNAL_DIR="${SCRIPT_DIR}/external"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${GREEN}[APEXSAT]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ─── Buildroot İndir ────────────────────────────────────────

download_buildroot() {
    if [ -d "${BUILDROOT_DIR}" ]; then
        log "Buildroot zaten mevcut: ${BUILDROOT_DIR}"
        return
    fi

    log "Buildroot ${BUILDROOT_VERSION} indiriliyor..."
    mkdir -p "${SCRIPT_DIR}"
    cd "${SCRIPT_DIR}"

    wget -c "${BUILDROOT_URL}" -O "buildroot-${BUILDROOT_VERSION}.tar.xz"
    tar xf "buildroot-${BUILDROOT_VERSION}.tar.xz"
    mv "buildroot-${BUILDROOT_VERSION}" "${BUILDROOT_DIR}"

    log "Buildroot indirildi ✓"
}

# ─── External Tree Hazırla ──────────────────────────────────

setup_external() {
    log "External tree hazırlanıyor..."

    mkdir -p "${EXTERNAL_DIR}"/{configs,package,rootfs_overlay}
    mkdir -p "${EXTERNAL_DIR}/rootfs_overlay/opt/apexsat"/{bin,lib,models,config}
    mkdir -p "${EXTERNAL_DIR}/rootfs_overlay/etc"

    # Konfigürasyonu kopyala
    cp "${SCRIPT_DIR}/apexsat_defconfig" "${EXTERNAL_DIR}/configs/"

    # External tree descriptor
    cat > "${EXTERNAL_DIR}/external.desc" << 'EOF'
name: APEXSAT
desc: APEXSAT AI - DVB-S2 Akilli Uydu Alicisi
EOF

    # External makefile
    cat > "${EXTERNAL_DIR}/external.mk" << 'EOF'
include $(sort $(wildcard $(BR2_EXTERNAL_APEXSAT_PATH)/package/*/*.mk))
EOF

    # Config.in
    cat > "${EXTERNAL_DIR}/Config.in" << 'EOF'
source "$BR2_EXTERNAL_APEXSAT_PATH/package/whisper-cpp/Config.in"
source "$BR2_EXTERNAL_APEXSAT_PATH/package/piper-tts/Config.in"
source "$BR2_EXTERNAL_APEXSAT_PATH/package/apexsat-app/Config.in"
EOF

    # ─── Custom Package: whisper-cpp ─────────────────────────
    mkdir -p "${EXTERNAL_DIR}/package/whisper-cpp"

    cat > "${EXTERNAL_DIR}/package/whisper-cpp/Config.in" << 'EOF'
config BR2_PACKAGE_WHISPER_CPP
    bool "whisper-cpp"
    depends on BR2_INSTALL_LIBSTDCPP
    help
      OpenAI Whisper ses tanima modeli C/C++ implementasyonu.
      APEXSAT AI sesli asistan icin kullanilir.
      https://github.com/ggerganov/whisper.cpp
EOF

    cat > "${EXTERNAL_DIR}/package/whisper-cpp/whisper-cpp.mk" << 'EOF'
WHISPER_CPP_VERSION = 1.5.4
WHISPER_CPP_SITE = https://github.com/ggerganov/whisper.cpp/archive/refs/tags/v$(WHISPER_CPP_VERSION).tar.gz
WHISPER_CPP_LICENSE = MIT
WHISPER_CPP_INSTALL_TARGET = YES

WHISPER_CPP_CONF_OPTS = \
    -DBUILD_SHARED_LIBS=ON \
    -DWHISPER_NO_ACCELERATE=ON

$(eval $(cmake-package))
EOF

    # ─── Custom Package: piper-tts ───────────────────────────
    mkdir -p "${EXTERNAL_DIR}/package/piper-tts"

    cat > "${EXTERNAL_DIR}/package/piper-tts/Config.in" << 'EOF'
config BR2_PACKAGE_PIPER_TTS
    bool "piper-tts"
    depends on BR2_INSTALL_LIBSTDCPP
    help
      Piper - hizli, yerel TTS (Text-to-Speech) motoru.
      Turkce ses sentezi icin kullanilir.
      https://github.com/rhasspy/piper
EOF

    cat > "${EXTERNAL_DIR}/package/piper-tts/piper-tts.mk" << 'EOF'
PIPER_TTS_VERSION = 2023.11.14-2
PIPER_TTS_SITE = https://github.com/rhasspy/piper/archive/refs/tags/$(PIPER_TTS_VERSION).tar.gz
PIPER_TTS_LICENSE = MIT
PIPER_TTS_INSTALL_TARGET = YES

PIPER_TTS_DEPENDENCIES = onnxruntime

$(eval $(cmake-package))
EOF

    # ─── Custom Package: apexsat-app ─────────────────────────
    mkdir -p "${EXTERNAL_DIR}/package/apexsat-app"

    cat > "${EXTERNAL_DIR}/package/apexsat-app/Config.in" << 'EOF'
config BR2_PACKAGE_APEXSAT_APP
    bool "apexsat-app"
    depends on BR2_PACKAGE_PYTHON3
    depends on BR2_PACKAGE_QT6DECLARATIVE
    help
      APEXSAT AI ana uygulama paketi.
      DVB tarama, EPG, AI oneri, sesli asistan, UI.
EOF

    cat > "${EXTERNAL_DIR}/package/apexsat-app/apexsat-app.mk" << 'APPMK'
APEXSAT_APP_VERSION = 1.0.0
APEXSAT_APP_SITE = $(BR2_EXTERNAL_APEXSAT_PATH)/../../software
APEXSAT_APP_SITE_METHOD = local
APEXSAT_APP_LICENSE = Proprietary
APEXSAT_APP_INSTALL_TARGET = YES

define APEXSAT_APP_INSTALL_TARGET_CMDS
    mkdir -p $(TARGET_DIR)/opt/apexsat
    cp -r $(@D)/dvb $(TARGET_DIR)/opt/apexsat/
    cp -r $(@D)/media $(TARGET_DIR)/opt/apexsat/
    cp -r $(@D)/ai $(TARGET_DIR)/opt/apexsat/
    cp -r $(@D)/ui $(TARGET_DIR)/opt/apexsat/
    cp -r $(@D)/iptv $(TARGET_DIR)/opt/apexsat/
    cp -r $(@D)/iot $(TARGET_DIR)/opt/apexsat/
endef

$(eval $(generic-package))
APPMK

    # ─── Root Filesystem Overlay ─────────────────────────────

    # Hostname
    echo "apexsat" > "${EXTERNAL_DIR}/rootfs_overlay/etc/hostname"

    # APEXSAT systemd service
    mkdir -p "${EXTERNAL_DIR}/rootfs_overlay/etc/systemd/system"

    cat > "${EXTERNAL_DIR}/rootfs_overlay/etc/systemd/system/apexsat.service" << 'EOF'
[Unit]
Description=APEXSAT AI - DVB-S2 Uydu Alicisi
After=network.target graphical.target
Wants=network.target

[Service]
Type=simple
ExecStart=/opt/apexsat/bin/apexsat-launcher
Restart=always
RestartSec=5
User=root
Environment=QT_QPA_PLATFORM=eglfs
Environment=QT_QPA_EGLFS_INTEGRATION=eglfs_kms
Environment=XDG_RUNTIME_DIR=/run/user/0

[Install]
WantedBy=multi-user.target
EOF

    # Launcher script
    cat > "${EXTERNAL_DIR}/rootfs_overlay/opt/apexsat/bin/apexsat-launcher" << 'EOF'
#!/bin/bash
# APEXSAT AI Launcher
export PYTHONPATH="/opt/apexsat"
export LD_LIBRARY_PATH="/opt/apexsat/lib:$LD_LIBRARY_PATH"

echo "═══════════════════════════════════════"
echo "  APEXSAT AI v1.0 baslatiliyor..."
echo "  Dincer Tavukculuk / APEX Serisi"
echo "═══════════════════════════════════════"

# Qt/QML UI'ı başlat
cd /opt/apexsat/ui
exec python3 main.py --fullscreen
EOF
    chmod +x "${EXTERNAL_DIR}/rootfs_overlay/opt/apexsat/bin/apexsat-launcher"

    log "External tree hazır ✓"
}

# ─── Kernel Config ──────────────────────────────────────────

setup_kernel_config() {
    log "Kernel konfigürasyonu hazırlanıyor..."

    mkdir -p "${EXTERNAL_DIR}/kernel"
    cat > "${EXTERNAL_DIR}/kernel/apexsat_kernel_defconfig" << 'EOF'
# APEXSAT AI - Linux Kernel Config (S905X4)
# Base: arm64 defconfig + DVB + V4L2

# Architecture
CONFIG_ARCH_MESON=y

# DVB subsystem
CONFIG_MEDIA_SUPPORT=y
CONFIG_MEDIA_DIGITAL_TV_SUPPORT=y
CONFIG_DVB_CORE=y
CONFIG_DVB_DEMUX_SECTION_LOSS_LOG=y

# DVB Frontend drivers
CONFIG_DVB_STV0910=m
CONFIG_DVB_CX24116=m
CONFIG_DVB_SI2166=m
CONFIG_DVB_STV6111=m
CONFIG_DVB_LNBH25=m

# DVB Tuner drivers
CONFIG_MEDIA_TUNER=y
CONFIG_MEDIA_TUNER_SI2157=m
CONFIG_MEDIA_TUNER_R820T=m

# V4L2 (Video4Linux2) - HW decode
CONFIG_VIDEO_V4L2=y
CONFIG_VIDEO_DEV=y

# Amlogic VDEC
CONFIG_VIDEO_MESON_VDEC=y

# USB DVB adapters (PoC aşaması için)
CONFIG_DVB_USB=m
CONFIG_DVB_USB_V2=m
CONFIG_DVB_USB_TBS5580=m
CONFIG_DVB_USB_DVBSKY=m

# Filesystem
CONFIG_EXT4_FS=y
CONFIG_SQUASHFS=y
CONFIG_SQUASHFS_XZ=y
CONFIG_NTFS_FS=m
CONFIG_VFAT_FS=y
CONFIG_EXFAT_FS=m
CONFIG_FUSE_FS=y

# USB
CONFIG_USB_SUPPORT=y
CONFIG_USB_XHCI_HCD=y
CONFIG_USB_EHCI_HCD=y
CONFIG_USB_STORAGE=y
CONFIG_USB_UAS=y

# Network
CONFIG_NET=y
CONFIG_INET=y
CONFIG_IPV6=y
CONFIG_NETFILTER=y
CONFIG_CFG80211=m
CONFIG_MAC80211=m

# Bluetooth
CONFIG_BT=m
CONFIG_BT_HCIBTUSB=m
CONFIG_BT_HCIUART=m
CONFIG_BT_RFCOMM=m

# Sound
CONFIG_SOUND=y
CONFIG_SND=y
CONFIG_SND_SOC=y
CONFIG_SND_SOC_MESON_AXG_SOUND_CARD=y

# GPIO / I2C / SPI
CONFIG_GPIOLIB=y
CONFIG_I2C=y
CONFIG_I2C_MESON=y
CONFIG_SPI=y
CONFIG_SPI_MESON_SPICC=y

# PWM (fan kontrolü)
CONFIG_PWM=y
CONFIG_PWM_MESON=y

# HDMI
CONFIG_DRM=y
CONFIG_DRM_MESON=y
CONFIG_DRM_MESON_DW_HDMI=y

# IR remote
CONFIG_IR_MESON=y
CONFIG_RC_CORE=y
CONFIG_RC_DECODERS=y
CONFIG_IR_NEC_DECODER=y
CONFIG_IR_RC5_DECODER=y

# Thermal
CONFIG_THERMAL=y
CONFIG_CPU_THERMAL=y
CONFIG_AMLOGIC_THERMAL=y

# Watchdog
CONFIG_WATCHDOG=y
CONFIG_MESON_GXBB_WATCHDOG=y

# RTC
CONFIG_RTC_CLASS=y
EOF

    log "Kernel config hazır ✓"
}

# ─── Device Tree ────────────────────────────────────────────

setup_device_tree() {
    log "Device tree hazırlanıyor..."

    mkdir -p "${EXTERNAL_DIR}/devicetree"
    cat > "${EXTERNAL_DIR}/devicetree/apexsat-s905x4.dts" << 'EOF'
// SPDX-License-Identifier: (GPL-2.0+ OR MIT)
/*
 * APEXSAT AI - Amlogic S905X4 Device Tree
 * Halil Dincer - Dincer Tavukculuk / APEX Serisi
 */

/dts-v1/;

#include "meson-s4-s905x4.dtsi"

/ {
    compatible = "apexsat,ai-v1", "amlogic,s905x4", "amlogic,meson-s4";
    model = "APEXSAT AI DVB-S2 Receiver v1.0";

    aliases {
        serial0 = &uart_AO;
        ethernet0 = &ethmac;
    };

    chosen {
        stdout-path = "serial0:115200n8";
    };

    memory@0 {
        device_type = "memory";
        reg = <0x0 0x0 0x0 0x100000000>; /* 4GB DDR4 */
    };

    /* 5V ana güç */
    vcc_5v: regulator-vcc-5v {
        compatible = "regulator-fixed";
        regulator-name = "VCC_5V";
        regulator-min-microvolt = <5000000>;
        regulator-max-microvolt = <5000000>;
        regulator-always-on;
    };

    /* 3.3V güç */
    vcc_3v3: regulator-vcc-3v3 {
        compatible = "regulator-fixed";
        regulator-name = "VCC_3V3";
        regulator-min-microvolt = <3300000>;
        regulator-max-microvolt = <3300000>;
        vin-supply = <&vcc_5v>;
        regulator-always-on;
    };

    /* WiFi 32K clock */
    wifi_32k: wifi-32k {
        compatible = "pwm-clock";
        #clock-cells = <0>;
        clock-frequency = <32768>;
        pwms = <&pwm_ef 0 30518 0>;
    };

    /* HDMI ses */
    hdmi_sound: hdmi-sound {
        compatible = "amlogic,axg-sound-card";
        model = "APEXSAT-HDMI";
        status = "okay";
    };

    /* IR alıcı */
    ir_receiver: ir-receiver {
        compatible = "gpio-ir-receiver";
        gpios = <&gpio GPIOD_5 GPIO_ACTIVE_LOW>;
        linux,rc-map-name = "rc-apexsat";
    };

    /* Fan PWM kontrolü */
    cooling_fan: cooling-fan {
        compatible = "pwm-fan";
        #cooling-cells = <2>;
        pwms = <&pwm_ef 1 40000 0>;
        cooling-levels = <0 64 128 192 255>;
    };

    /* LED'ler */
    leds {
        compatible = "gpio-leds";

        led_power: led-power {
            label = "apexsat:red:power";
            gpios = <&gpio GPIOD_10 GPIO_ACTIVE_HIGH>;
            default-state = "on";
        };

        led_status: led-status {
            label = "apexsat:green:status";
            gpios = <&gpio GPIOD_11 GPIO_ACTIVE_HIGH>;
            linux,default-trigger = "heartbeat";
        };
    };
};

/* UART debug konsolu */
&uart_AO {
    status = "okay";
    pinctrl-0 = <&uart_ao_a_pins>;
    pinctrl-names = "default";
};

/* HDMI çıkış */
&hdmi_tx {
    status = "okay";
    pinctrl-0 = <&hdmitx_hpd_pins>, <&hdmitx_ddc_pins>;
    pinctrl-names = "default";
    hdmi-supply = <&vcc_5v>;
};

/* Ethernet (Gigabit) */
&ethmac {
    status = "okay";
    pinctrl-0 = <&eth_rgmii_pins>;
    pinctrl-names = "default";
    phy-handle = <&external_phy>;
    phy-mode = "rgmii-id";

    mdio {
        #address-cells = <1>;
        #size-cells = <0>;

        external_phy: ethernet-phy@0 {
            compatible = "ethernet-phy-id001c.c916";  /* RTL8211F */
            reg = <0>;
            max-speed = <1000>;
        };
    };
};

/* USB 3.0 */
&usb3_pcie_phy {
    status = "okay";
};

&usb {
    status = "okay";
    dr_mode = "host";
};

/* SD kart */
&sd_emmc_b {
    status = "okay";
    pinctrl-0 = <&sdcard_pins>;
    pinctrl-names = "default";
    bus-width = <4>;
    cap-sd-highspeed;
    sd-uhs-sdr50;
    max-frequency = <100000000>;
    vmmc-supply = <&vcc_3v3>;
};

/* eMMC */
&sd_emmc_c {
    status = "okay";
    pinctrl-0 = <&emmc_pins>;
    pinctrl-names = "default";
    bus-width = <8>;
    cap-mmc-highspeed;
    mmc-hs200-1_8v;
    max-frequency = <200000000>;
    vmmc-supply = <&vcc_3v3>;
    non-removable;
};

/* I2C bus (tuner kontrolü, mikrofon, sensörler) */
&i2c0 {
    status = "okay";
    pinctrl-0 = <&i2c0_pins>;
    pinctrl-names = "default";
    clock-frequency = <400000>;

    /* NIM modülü tuner kontrolü */
    /* Adres NIM modülüne göre değişir */
};

&i2c1 {
    status = "okay";
    clock-frequency = <100000>;

    /* OLED ekran (SSD1306) */
    oled_display: ssd1306@3c {
        compatible = "solomon,ssd1306fb-i2c";
        reg = <0x3c>;
        solomon,width = <128>;
        solomon,height = <64>;
    };
};

/* SPI (opsiyonel flash, sensör) */
&spicc0 {
    status = "okay";
    pinctrl-0 = <&spicc0_pins>;
    pinctrl-names = "default";
};

/* PWM (fan, backlight) */
&pwm_ef {
    status = "okay";
    pinctrl-0 = <&pwm_e_pins>;
    pinctrl-names = "default";
};

/* Termal yönetim */
&cpu_thermal {
    trips {
        cpu_passive: cpu-passive {
            temperature = <70000>;
            hysteresis = <5000>;
            type = "passive";
        };

        cpu_hot: cpu-hot {
            temperature = <80000>;
            hysteresis = <5000>;
            type = "hot";
        };

        cpu_critical: cpu-critical {
            temperature = <95000>;
            hysteresis = <2000>;
            type = "critical";
        };
    };

    cooling-maps {
        map0 {
            trip = <&cpu_passive>;
            cooling-device = <&cooling_fan 0 1>;
        };
        map1 {
            trip = <&cpu_hot>;
            cooling-device = <&cooling_fan 2 3>;
        };
    };
};
EOF

    log "Device tree hazır ✓"
}

# ─── Post-Build Script ──────────────────────────────────────

create_post_build() {
    cat > "${EXTERNAL_DIR}/post_build.sh" << 'POSTBUILD'
#!/bin/bash
# APEXSAT AI - Post-build script

TARGET_DIR="$1"

echo "APEXSAT AI post-build çalıştırılıyor..."

# Servis aktive et
mkdir -p "${TARGET_DIR}/etc/systemd/system/multi-user.target.wants"
ln -sf /etc/systemd/system/apexsat.service \
    "${TARGET_DIR}/etc/systemd/system/multi-user.target.wants/apexsat.service"

# Versiyon bilgisi
echo "APEXSAT AI v1.0.0 ($(date +%Y%m%d))" > "${TARGET_DIR}/opt/apexsat/version"

echo "Post-build tamamlandı ✓"
POSTBUILD
    chmod +x "${EXTERNAL_DIR}/post_build.sh"
}

# ─── Build ──────────────────────────────────────────────────

build_image() {
    log "Buildroot imajı oluşturuluyor..."

    cd "${BUILDROOT_DIR}"

    # External tree tanımla
    make BR2_EXTERNAL="${EXTERNAL_DIR}" apexsat_defconfig

    # Paralel derleme
    NPROC=$(nproc)
    log "Derleme başlıyor (${NPROC} çekirdek)..."
    make -j${NPROC}

    # Çıktıları kopyala
    mkdir -p "${OUTPUT_DIR}"
    cp -f "${BUILDROOT_DIR}/output/images/rootfs.squashfs" "${OUTPUT_DIR}/" 2>/dev/null || true
    cp -f "${BUILDROOT_DIR}/output/images/rootfs.ext4" "${OUTPUT_DIR}/" 2>/dev/null || true
    cp -f "${BUILDROOT_DIR}/output/images/Image" "${OUTPUT_DIR}/" 2>/dev/null || true
    cp -f "${BUILDROOT_DIR}/output/images/"*.dtb "${OUTPUT_DIR}/" 2>/dev/null || true

    log "═══════════════════════════════════════"
    log "  İmaj oluşturuldu! ✓"
    log "  Çıktı: ${OUTPUT_DIR}/"
    log "═══════════════════════════════════════"
    ls -lh "${OUTPUT_DIR}/"
}

# ─── Ana Akış ────────────────────────────────────────────────

usage() {
    echo "APEXSAT AI - Buildroot Build Script"
    echo ""
    echo "Kullanım: $0 [komut]"
    echo ""
    echo "Komutlar:"
    echo "  all          Tümünü çalıştır (indir + hazırla + derle)"
    echo "  download     Buildroot indir"
    echo "  setup        External tree hazırla"
    echo "  menuconfig   Buildroot menuconfig aç"
    echo "  build        İmaj oluştur"
    echo "  clean        Temizle"
}

case "${1:-help}" in
    all)
        download_buildroot
        setup_external
        setup_kernel_config
        setup_device_tree
        create_post_build
        build_image
        ;;
    download)
        download_buildroot
        ;;
    setup)
        setup_external
        setup_kernel_config
        setup_device_tree
        create_post_build
        log "Setup tamamlandı ✓"
        ;;
    menuconfig)
        cd "${BUILDROOT_DIR}"
        make BR2_EXTERNAL="${EXTERNAL_DIR}" menuconfig
        ;;
    build)
        build_image
        ;;
    clean)
        log "Temizleniyor..."
        rm -rf "${BUILDROOT_DIR}/output" "${OUTPUT_DIR}"
        log "Temizlendi ✓"
        ;;
    *)
        usage
        ;;
esac
