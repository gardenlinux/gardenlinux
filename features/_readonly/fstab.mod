#!/usr/bin/env bash
set -Eeuo pipefail

# delete any predefinition of a overlay, root, usr and EFI partition
sed '/^[^[:space:]]\+[[:space:]]\+\/overlay[[:space:]]\+/d;/^[^[:space:]]\+[[:space:]]\+\/[[:space:]]\+/d;/^[^[:space:]]\+[[:space:]]\+\/usr[[:space:]]\+/d;/^[^[:space:]]\+[[:space:]]\+\/boot\/efi[[:space:]]\+/d'

# make usr a readonly setup
cat << EOF
LABEL=EFI    /boot/efi    vfat    ro,umask=0077    type=uefi,size=128MiB
LABEL=USR    /usr         ext4    ro               verity
REPART=00    /            ext4    rw               ephemeral_cryptsetup
EOF
