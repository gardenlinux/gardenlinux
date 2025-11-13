#!/usr/bin/env bash
set -ue

thisDir=$(readlink -f $(dirname "${BASH_SOURCE[0]}"))

targetDisk="$1"

pushd "$thisDir"

# remove all HD related boot entries
for e in $(efibootmgr | awk '$NF ~ /^HD/ { print $1 }' | sed "s/Boot\([0-9A-F]*\)./\1/"); do
  echo "Removing entry $e"
  efibootmgr -B -b "$e" > /dev/null
done

# prepare disk for repart
sgdisk -Z "$targetDisk"
sgdisk -o "$targetDisk"

# actually partition and populate with data
systemd-repart --definitions repart/ --json=pretty --dry-run=off --copy-source=/run/source/ --generate-fstab=/etc/fstab --append-fstab=replace "$targetDisk"

sleep 5

# prepare mounts for chroot env
target="/run/chroot"
mkdir "$target" 
mount /dev/disk/by-label/ROOT "$target" 
mount /dev/disk/by-label/ESP "$target/efi"

# prepare extra mounts
pushd "$target" > /dev/null
mount -t proc proc proc
mount -t sysfs sys sys
mount --bind /dev dev

# regenerate initrd and generate loader entries
chroot "$target" dracut /boot/initrd.img-"$(uname -r)"
chroot "$target" kernel-install add "$(uname -r)" "/boot/vmlinuz-$(uname -r)" "/boot/initrd.img-$(uname -r)"

if mount --bind /sys/firmware/efi/efivars "$target/sys/firmware/efi/efivars"; then
	# efi
	chroot "$target" bootctl install
else
	# legacy
	chroot "${target}" sfdisk --part-attrs "${targetDisk}" 1 LegacyBIOSBootable
	chroot "${target}" dd if="/usr/lib/SYSLINUX/gptmbr.bin" of="${targetDisk}" bs=440 count=1 conv=notrunc
	chroot "${target}" mkdir -p /efi/syslinux
	chroot "${target}" cp /usr/lib/syslinux/modules/bios/menu.c32 /efi/syslinux/
	chroot "${target}" cp /usr/lib/syslinux/modules/bios/libutil.c32 /efi/syslinux/
	chroot "${target}" syslinux --directory syslinux --install /dev/disk/by-label/ESP
	chroot "${target}" update-syslinux
fi

echo "Safe to reboot"
