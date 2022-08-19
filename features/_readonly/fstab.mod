#!/usr/bin/env bash
set -Eeuo pipefail

# delete any predefinition of a overlay, root, usr and EFI partition
sed '/^[^[:space:]]\+[[:space:]]\+\/overlay[[:space:]]\+/d;/^[^[:space:]]\+[[:space:]]\+\/[[:space:]]\+/d;/^[^[:space:]]\+[[:space:]]\+\/usr[[:space:]]\+/d;/^[^[:space:]]\+[[:space:]]\+\/boot\/efi[[:space:]]\+/d'

# make usr a readonly setup
printf "LABEL=EFI          /boot/efi    vfat      umask=0077   type=uefi,size=128MiB\n"
printf "LABEL=ROOT         /            ext4      ro           verity\n"
printf "LABEL=USR          /usr         ext4      ro           verity\n"
printf "LABEL=OVERLAY      /overlay     ext4      rw,discard,x-initrd.mount    size=512MiB\n"
