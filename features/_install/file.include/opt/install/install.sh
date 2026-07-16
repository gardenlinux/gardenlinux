#!/usr/bin/env bash

set -e

thisDir=$(readlink -f $(dirname "${BASH_SOURCE[0]}"))

# Auto-detect rootfs source (ISO uses /run/rootfsbase, PXE uses /run/rootfs)
if [ -d /run/rootfsbase ]; then
	rootfs_source="/run/rootfsbase"
	echo "Detected ISO live environment (source: /run/rootfsbase)"
elif [ -d /run/rootfs ]; then
	rootfs_source="/run/rootfs"
	echo "Detected PXE live environment (source: /run/rootfs)"
else
	echo "ERROR: Cannot find rootfs source (neither /run/rootfsbase nor /run/rootfs exist)"
	exit 1
fi

# Non-interactive mode: if GL_INSTALL_TARGET is set, use it and skip prompts
if [ -n "${GL_INSTALL_TARGET:-}" ]; then
	targetDisk="$GL_INSTALL_TARGET"
	echo "Non-interactive install to $targetDisk"
else
	echo "Please provide the device where you would like to install e.g. /dev/sda:"
	read targetDisk

	echo "You are about to install to $targetDisk"
	echo
	echo "THIS WILL DESTROY ALL DATA ON PROVIDED TARGET!"
	echo

	read -n 1 -r -s -p $'Press any key to continue...\n'
	read -n 1 -r -s -p $'One more time...\n'
fi

echo "Starting installation..."
kernel=$(uname -r)
target=/tmp/install

# remove all HD related boot entries
echo "Removing all HD related boot entries..."
for e in $(efibootmgr | awk '$NF ~ /^HD/ { print $1 }' | sed "s/Boot\([0-9A-F]*\)./\1/"); do
  echo "Removing entry $e"
  efibootmgr -B -b "$e" > /dev/null
done


#TODO: check if targetDisk is valid
echo "Zapping $targetDisk..."
wipefs -a "$targetDisk"

echo "Partitioning $targetDisk..."
# need to bind mount this to be writable
mount --bind /tmp ${rootfs_source}/tmp
systemd-repart --empty=force --definitions "${thisDir}/repart/" --json=pretty --dry-run=off --copy-source=${rootfs_source} --generate-fstab=/tmp/fstab --append-fstab=replace "$targetDisk"

udevadm settle --timeout=30

echo "Mounting filesystems..."
mkdir -p "${target}"
mount /dev/disk/by-label/ROOT "${target}"
mount /dev/disk/by-label/ESP "${target}/efi"

echo "Setting up chroot environment..."
mount -t proc /proc ${target}/proc
mount -t sysfs /sys ${target}/sys
mount --bind /dev  ${target}/dev
mount --bind /run  ${target}/run

echo "Copying fstab..."
cp ${rootfs_source}/tmp/fstab ${target}/etc

if [ -d ${target}/usr/lib/dracut/modules.d/98gardenlinux-live ]; then
  echo "Removing _pxe feature specifics..."
  rm -rf ${target}/usr/lib/dracut/modules.d/98gardenlinux-live ${target}/etc/dracut.conf.d/20-gl-live.conf
  rm -f ${target}/etc/kernel/cmdline.d/80-pxe.cfg
  echo "Rebuilding initrd (this takes several minutes)..."
  chroot ${target}/ /etc/kernel/postinst.d/dracut ${kernel}
  echo "Generating systemd-boot loader entries..."
  # Ensure /etc/machine-id exists so kernel-install selects the BLS layout and
  # uses the 'Default' entry-token from /etc/kernel/entry-token.
  chroot ${target}/ bash -c '[ -s /etc/machine-id ] || systemd-machine-id-setup'
  # Ensure the entry-token directory exists under the ESP.
  chroot ${target}/ mkdir -p /efi/Default
  # Invoke the feature's own regeneration chain (update-kernel-cmdline →
  # kernel-install add per vmlinuz → update-syslinux) with the ESP path
  # exported. This mirrors the proven runtime path used for kernel updates.
  chroot ${target}/ env SYSTEMD_ESP_PATH=/efi update-bootloaders
else
  # For non-PXE installs (like ISO), copy boot entries from live system
  echo "Copying systemd-boot entries..."
  cp -r /efi/{Default,loader} ${target}/efi
fi

if mount -t efivarfs efivarfs ${target}/sys/firmware/efi/efivars >/dev/null; then
  echo "UEFI install selected"
  hasefi=1
else
  echo "Legacy install selected"
  hasefi=0
fi

echo "Installing bootloader..."
if [ "$hasefi" == "1" ]; then
  echo "  Installing UEFI bootloader..."
  chroot "${target}" bootctl install
else
  echo "  Installing BIOS bootloader (syslinux)..."
  chroot ${target} sfdisk --part-attrs ${targetDisk} 1 LegacyBIOSBootable
  chroot ${target} dd if="/usr/lib/SYSLINUX/gptmbr.bin" of=${targetDisk} bs=440 count=1 conv=notrunc
  chroot ${target} mkdir -p /efi/syslinux
  chroot ${target} cp /usr/lib/syslinux/modules/bios/menu.c32 /efi/syslinux/
  chroot ${target} cp /usr/lib/syslinux/modules/bios/libutil.c32 /efi/syslinux/
  chroot ${target} syslinux --directory syslinux --install /dev/disk/by-label/ESP
  chroot "${target}" update-syslinux
fi

# change root password (only in interactive mode)
if [ -z "${GL_INSTALL_TARGET:-}" ]; then
	echo
	echo "Please provide a password for the root user"
	chroot ${target} passwd
fi

echo "Finalizing installation..."
echo "Removing _iso feature specifics..."
rm -rf ${target}/etc/systemd/system/getty@tty1.service.d ${target}/etc/systemd/system/serial-getty@.service.d
echo "Removing _install feature specifics..."
rm -rf ${target}/opt/install
echo "Removing _autoinstall feature specifics..."
rm -rf ${target}/usr/local/sbin/gl-autoinstall ${target}/etc/systemd/system/gl-autoinstall.service
date --iso-8601=s > ${target}/.installed

if [ "${GL_INSTALL_UMOUNT:-true}" == "true" ]; then
  echo "Unmounting installation target..."
  umount -l ${target}/{dev,efi,proc,run,sys} ${target}
fi

echo "Installation completed successfully!"
