#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ============================================================================
echo "================================================== Prepare workspace"

rm -rf "$SCRIPT_DIR/.tmp"
mkdir -p "$SCRIPT_DIR/.tmp"
cd "$SCRIPT_DIR/.tmp"

# ============================================================================
echo "================================================== Initialize project"

lb config \
    --mirror-bootstrap "http://deb.debian.org/debian/" \
    --mirror-chroot "http://deb.debian.org/debian/" \
    --mirror-binary "http://deb.debian.org/debian/" \
    --parent-mirror-bootstrap "http://deb.debian.org/debian/" \
    --parent-mirror-chroot "http://deb.debian.org/debian/" \
    --parent-mirror-binary "http://deb.debian.org/debian/" \
    --keyring-packages debian-archive-keyring \
    --distribution trixie \
    --architecture amd64 \
    --archive-areas "main contrib non-free non-free-firmware" \
    --bootappend-live "boot=live components locales=en_US.UTF-8 keyboard-layouts=us console=ttyS0,115200 quiet splash live-noconfig=networking toram" \
    --binary-images iso-hybrid \
    --bootloaders "grub-pc,grub-efi"

# ============================================================================
echo "================================================== Configure packages"

cat <<EOF > config/package-lists/package.list.chroot
nebula
openvpn
wireguard
wireguard-tools
iputils-ping
flent
iproute2
iperf3
netperf
live-boot
live-config
sysstat
systemd-sysv
openssh-server
EOF

# ============================================================================
echo "================================================== Copy static configuration"

cp -r "$SCRIPT_DIR/config/includes.chroot/." "config/includes.chroot"
cp -r "$SCRIPT_DIR/config/hooks/." "config/hooks"
chmod -R 700 config/includes.chroot/root/.ssh
chmod -R +x config/hooks

# ============================================================================
echo "================================================== Build"

lb build

# ============================================================================
echo "================================================== Extract result"

mv *.iso "$SCRIPT_DIR/guest.iso"

# ============================================================================
echo "================================================== Clean up"

cd "$SCRIPT_DIR"
rm -rf .tmp