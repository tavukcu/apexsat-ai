#!/bin/bash
# APEXSAT AI - Post-build script

TARGET_DIR="$1"

echo "APEXSAT AI post-build calistiriliyor..."

# Servis aktive et
mkdir -p "${TARGET_DIR}/etc/systemd/system/multi-user.target.wants"
ln -sf /etc/systemd/system/apexsat.service \
    "${TARGET_DIR}/etc/systemd/system/multi-user.target.wants/apexsat.service"

# Versiyon bilgisi
echo "APEXSAT AI v1.0.0 ($(date +%Y%m%d))" > "${TARGET_DIR}/opt/apexsat/version"

echo "Post-build tamamlandi"
