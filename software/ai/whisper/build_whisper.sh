#!/bin/bash
# ─────────────────────────────────────────────────────────────────
# APEXSAT AI - Whisper.cpp Cross-Compile Script
# Amlogic S905X4 (aarch64) için Whisper.cpp derlemesi
# ─────────────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"
WHISPER_DIR="${BUILD_DIR}/whisper.cpp"
MODELS_DIR="${SCRIPT_DIR}/models"
OUTPUT_DIR="${BUILD_DIR}/output"

# Cross-compile toolchain
CROSS_COMPILE="${CROSS_COMPILE:-aarch64-linux-gnu-}"
CC="${CROSS_COMPILE}gcc"
CXX="${CROSS_COMPILE}g++"

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ─── Bağımlılık Kontrolü ────────────────────────────────────────

check_dependencies() {
    log_info "Bağımlılıklar kontrol ediliyor..."

    local missing=()

    if ! command -v git &> /dev/null; then missing+=("git"); fi
    if ! command -v cmake &> /dev/null; then missing+=("cmake"); fi
    if ! command -v make &> /dev/null; then missing+=("make"); fi

    # Cross-compiler kontrolü
    if ! command -v ${CC} &> /dev/null; then
        log_warn "Cross-compiler bulunamadı: ${CC}"
        log_info "Yüklemek için: sudo apt install gcc-aarch64-linux-gnu g++-aarch64-linux-gnu"
        log_info "Native derleme yapılacak (test amaçlı)..."
        CC="gcc"
        CXX="g++"
        CROSS_COMPILE=""
    fi

    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Eksik bağımlılıklar: ${missing[*]}"
        log_info "Yüklemek için: sudo apt install ${missing[*]}"
        exit 1
    fi

    log_info "Tüm bağımlılıklar mevcut ✓"
}

# ─── Whisper.cpp İndir ───────────────────────────────────────────

download_whisper() {
    log_info "Whisper.cpp indiriliyor..."
    mkdir -p "${BUILD_DIR}"

    if [ -d "${WHISPER_DIR}" ]; then
        log_info "Whisper.cpp zaten mevcut, güncelleniyor..."
        cd "${WHISPER_DIR}" && git pull
    else
        git clone https://github.com/ggerganov/whisper.cpp.git "${WHISPER_DIR}"
    fi

    log_info "Whisper.cpp hazır ✓"
}

# ─── Model İndir ────────────────────────────────────────────────

download_models() {
    log_info "Whisper modelleri indiriliyor..."
    mkdir -p "${MODELS_DIR}"

    # Türkçe dil desteği olan modeller
    # tiny: ~75MB (hızlı, düşük doğruluk)
    # base: ~142MB (dengeli)
    # small: ~466MB (iyi doğruluk)
    # medium: ~1.5GB (yüksek doğruluk - ÖNERİLEN)

    local BASE_URL="https://huggingface.co/ggerganov/whisper.cpp/resolve/main"

    # Varsayılan: small model (466MB - NPU için uygun)
    local models=("ggml-small.bin" "ggml-base.bin" "ggml-tiny.bin")

    for model in "${models[@]}"; do
        if [ -f "${MODELS_DIR}/${model}" ]; then
            log_info "Model zaten mevcut: ${model}"
        else
            log_info "İndiriliyor: ${model}..."
            curl -L "${BASE_URL}/${model}" -o "${MODELS_DIR}/${model}" || {
                log_warn "${model} indirilemedi, devam ediliyor..."
            }
        fi
    done

    # INT8 quantized model (NPU için optimize)
    local q_models=("ggml-small-q5_1.bin" "ggml-base-q5_1.bin")
    for model in "${q_models[@]}"; do
        if [ -f "${MODELS_DIR}/${model}" ]; then
            log_info "Quantized model mevcut: ${model}"
        else
            log_info "İndiriliyor: ${model}..."
            curl -L "${BASE_URL}/${model}" -o "${MODELS_DIR}/${model}" 2>/dev/null || {
                log_warn "${model} bulunamadı (opsiyonel)"
            }
        fi
    done

    log_info "Modeller hazır ✓"
    ls -lh "${MODELS_DIR}/"*.bin 2>/dev/null || log_warn "Model dosyası bulunamadı"
}

# ─── Cross-Compile ──────────────────────────────────────────────

build_whisper() {
    log_info "Whisper.cpp derleniyor (${CC})..."

    mkdir -p "${OUTPUT_DIR}"
    cd "${WHISPER_DIR}"

    # CMake ile cross-compile
    mkdir -p build && cd build

    if [ -n "${CROSS_COMPILE}" ]; then
        # Cross-compile modu
        cmake .. \
            -DCMAKE_C_COMPILER="${CC}" \
            -DCMAKE_CXX_COMPILER="${CXX}" \
            -DCMAKE_SYSTEM_NAME=Linux \
            -DCMAKE_SYSTEM_PROCESSOR=aarch64 \
            -DWHISPER_NO_ACCELERATE=ON \
            -DWHISPER_OPENBLAS=OFF \
            -DCMAKE_BUILD_TYPE=Release \
            -DBUILD_SHARED_LIBS=OFF
    else
        # Native derleme (test için)
        cmake .. \
            -DCMAKE_BUILD_TYPE=Release \
            -DBUILD_SHARED_LIBS=OFF
    fi

    make -j$(nproc)

    # Çıktıları kopyala
    cp -f bin/whisper-cli "${OUTPUT_DIR}/" 2>/dev/null || cp -f bin/main "${OUTPUT_DIR}/whisper-cli" 2>/dev/null || true
    cp -f bin/whisper-server "${OUTPUT_DIR}/" 2>/dev/null || cp -f bin/server "${OUTPUT_DIR}/whisper-server" 2>/dev/null || true
    cp -f libwhisper.a "${OUTPUT_DIR}/" 2>/dev/null || true
    cp -f libwhisper.so "${OUTPUT_DIR}/" 2>/dev/null || true

    log_info "Derleme tamamlandı ✓"
    ls -lh "${OUTPUT_DIR}/"
}

# ─── Test ────────────────────────────────────────────────────────

test_whisper() {
    log_info "Whisper testi çalıştırılıyor..."

    local whisper_bin="${OUTPUT_DIR}/whisper-cli"
    local model="${MODELS_DIR}/ggml-tiny.bin"

    if [ ! -f "${whisper_bin}" ]; then
        log_error "whisper-cli bulunamadı: ${whisper_bin}"
        return 1
    fi

    if [ ! -f "${model}" ]; then
        log_warn "Test modeli bulunamadı: ${model}"
        return 0
    fi

    # Test ses dosyası oluştur (1 saniye sessizlik)
    local test_wav="/tmp/apexsat_test.wav"
    if command -v ffmpeg &> /dev/null; then
        ffmpeg -y -f lavfi -i "sine=frequency=440:duration=2" -ar 16000 -ac 1 "${test_wav}" 2>/dev/null
        log_info "Test çalıştırılıyor..."
        "${whisper_bin}" -m "${model}" -l tr -f "${test_wav}" 2>&1 | head -20
    else
        log_warn "ffmpeg bulunamadı, test atlanıyor"
    fi

    log_info "Test tamamlandı ✓"
}

# ─── Deployment Paketi Oluştur ───────────────────────────────────

create_deploy_package() {
    log_info "Deployment paketi oluşturuluyor..."

    local DEPLOY_DIR="${BUILD_DIR}/deploy"
    mkdir -p "${DEPLOY_DIR}/bin"
    mkdir -p "${DEPLOY_DIR}/models"
    mkdir -p "${DEPLOY_DIR}/lib"

    # Binary'ler
    cp -f "${OUTPUT_DIR}/whisper-cli" "${DEPLOY_DIR}/bin/" 2>/dev/null || true
    cp -f "${OUTPUT_DIR}/whisper-server" "${DEPLOY_DIR}/bin/" 2>/dev/null || true
    cp -f "${OUTPUT_DIR}/libwhisper.so" "${DEPLOY_DIR}/lib/" 2>/dev/null || true

    # Modeller (sadece small - NPU için ideal)
    for model in "${MODELS_DIR}/"*.bin; do
        [ -f "$model" ] && cp "$model" "${DEPLOY_DIR}/models/"
    done

    # Deployment script
    cat > "${DEPLOY_DIR}/install.sh" << 'INSTALL_EOF'
#!/bin/bash
# APEXSAT AI - Whisper Kurulum Scripti (Hedef cihaz)
set -e
INSTALL_DIR="/opt/apexsat/whisper"
mkdir -p "${INSTALL_DIR}"/{bin,models,lib}
cp -f bin/* "${INSTALL_DIR}/bin/"
cp -f models/* "${INSTALL_DIR}/models/"
cp -f lib/* "${INSTALL_DIR}/lib/" 2>/dev/null || true
chmod +x "${INSTALL_DIR}/bin/"*
echo "✅ Whisper kurulumu tamamlandı: ${INSTALL_DIR}"
INSTALL_EOF
    chmod +x "${DEPLOY_DIR}/install.sh"

    # Tar paketi
    cd "${BUILD_DIR}"
    tar czf apexsat-whisper-aarch64.tar.gz -C deploy .
    log_info "Paket oluşturuldu: ${BUILD_DIR}/apexsat-whisper-aarch64.tar.gz"

    du -sh "${BUILD_DIR}/apexsat-whisper-aarch64.tar.gz"
}

# ─── Ana Akış ────────────────────────────────────────────────────

usage() {
    echo "APEXSAT AI - Whisper.cpp Build Script"
    echo ""
    echo "Kullanım: $0 [komut]"
    echo ""
    echo "Komutlar:"
    echo "  all          Tümünü çalıştır (indir + derle + test + paketle)"
    echo "  download     Whisper.cpp kaynak kodunu indir"
    echo "  models       Whisper modellerini indir"
    echo "  build        Cross-compile et"
    echo "  test         Test çalıştır"
    echo "  package      Deployment paketi oluştur"
    echo "  clean        Build dosyalarını temizle"
    echo ""
    echo "Ortam değişkenleri:"
    echo "  CROSS_COMPILE  Cross-compile prefix (varsayılan: aarch64-linux-gnu-)"
}

case "${1:-all}" in
    all)
        check_dependencies
        download_whisper
        download_models
        build_whisper
        test_whisper
        create_deploy_package
        echo ""
        log_info "═══════════════════════════════════════"
        log_info "  Tüm adımlar tamamlandı! ✓"
        log_info "═══════════════════════════════════════"
        ;;
    download)
        check_dependencies
        download_whisper
        ;;
    models)
        download_models
        ;;
    build)
        check_dependencies
        build_whisper
        ;;
    test)
        test_whisper
        ;;
    package)
        create_deploy_package
        ;;
    clean)
        log_info "Temizleniyor..."
        rm -rf "${BUILD_DIR}"
        log_info "Temizlendi ✓"
        ;;
    *)
        usage
        ;;
esac
