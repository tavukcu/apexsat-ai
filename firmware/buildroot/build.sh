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

    # Standalone dosyalardan kopyala (kaynak: external/ dizini)
    local SRC_EXT="${SCRIPT_DIR}/external"

    if [ ! -d "${SRC_EXT}" ]; then
        error "external/ dizini bulunamadı: ${SRC_EXT}"
        exit 1
    fi

    mkdir -p "${EXTERNAL_DIR}"/{configs,package,rootfs_overlay}
    mkdir -p "${EXTERNAL_DIR}/rootfs_overlay/opt/apexsat"/{bin,lib,models,config}

    # Konfigürasyonu kopyala
    cp "${SCRIPT_DIR}/apexsat_defconfig" "${EXTERNAL_DIR}/configs/"

    # External tree dosyalarını kopyala
    cp "${SRC_EXT}/external.desc" "${EXTERNAL_DIR}/"
    cp "${SRC_EXT}/external.mk" "${EXTERNAL_DIR}/"
    cp "${SRC_EXT}/Config.in" "${EXTERNAL_DIR}/"
    cp "${SRC_EXT}/post_build.sh" "${EXTERNAL_DIR}/"
    chmod +x "${EXTERNAL_DIR}/post_build.sh"

    # Custom package'ları kopyala
    cp -r "${SRC_EXT}/package/"* "${EXTERNAL_DIR}/package/"

    # Root filesystem overlay kopyala
    cp -r "${SRC_EXT}/rootfs_overlay/"* "${EXTERNAL_DIR}/rootfs_overlay/"
    chmod +x "${EXTERNAL_DIR}/rootfs_overlay/opt/apexsat/bin/apexsat-launcher"

    log "External tree hazır ✓"
}

# ─── Kernel Config ──────────────────────────────────────────

setup_kernel_config() {
    log "Kernel konfigürasyonu hazırlanıyor..."

    mkdir -p "${EXTERNAL_DIR}/kernel"
    cp "${SCRIPT_DIR}/kernel/apexsat_kernel_defconfig" "${EXTERNAL_DIR}/kernel/"

    log "Kernel config hazır ✓"
}

# ─── Device Tree ────────────────────────────────────────────

setup_device_tree() {
    log "Device tree hazırlanıyor..."

    mkdir -p "${EXTERNAL_DIR}/devicetree"
    cp "${SCRIPT_DIR}/devicetree/apexsat-s905x4.dts" "${EXTERNAL_DIR}/devicetree/"

    log "Device tree hazır ✓"
}

# ─── Post-Build Script ──────────────────────────────────────

create_post_build() {
    # post_build.sh zaten setup_external()'da kopyalandi
    log "Post-build script hazır (external/post_build.sh)"
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
