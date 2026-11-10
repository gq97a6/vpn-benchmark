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
    --archive-areas "main contrib non-free-firmware" \
    --bootappend-live "boot=live components locales=en_US.UTF-8 keyboard-layouts=us quiet splash live-noconfig=networking intel_pstate=disable amd_pstate=disable initcall_blacklist=amd_pstate_init toram isolcpus=4-15 nohz_full=4-15 rcu_nocbs=4-15" \
    --binary-images iso-hybrid \
    --bootloaders "grub-pc,grub-efi"

# ============================================================================
echo "================================================== Configure packages"

cat <<EOF > config/package-lists/package.list.chroot
htop
nano
curl
screen
python3-pip
python3-venv
linux-cpupower
sysstat
stress-ng
linux-perf
lsb-release
gnupg
ca-certificates
rsync
live-boot
qemu-kvm
libvirt-daemon-system
libvirt-clients
bridge-utils
virtinst
virt-manager
live-config
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
mv *.iso "$SCRIPT_DIR/host.iso"

# ============================================================================
echo "================================================== Clean up"
cd "$SCRIPT_DIR"
rm -rf .tmp