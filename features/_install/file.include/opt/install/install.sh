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
	echo "Using the following partition configuration:"
	cat "${thisDir}/install.part"
	echo
	echo "Using the following fstab:"
	cat "${thisDir}/install.fstab"
	echo
	echo "THIS WILL DESTROY ALL DATA ON PROVIDED TARGET!"
	echo

	read -n 1 -r -s -p $'Press any key to continue...\n'
	read -n 1 -r -s -p $'One more time...\n'
fi

echo "Starting installation..."
kernel=$(uname -r)
target=/opt/install

echo "Partitioning $targetDisk..."

#TODO: add check for existing ROOT/EFI partitions
#TODO: check if targetDisk is valid
#NOTE: for the time being we consider LABEL=PARTLABEL

# Save install files to /tmp before they become inaccessible
cp "${thisDir}/install.fstab" /tmp/install.fstab

cat "${thisDir}/install.part" | sfdisk $targetDisk
echo "Partition table created successfully"
rootDev="/dev/disk/by-partlabel/ROOT"
efiDev="/dev/disk/by-partlabel/EFI"
udevadm settle --timeout=30

echo "Formatting partitions..."
for f in $(cat "${thisDir}/install.fstab" | awk '$3=="vfat"{print $1}' | awk -F= '{ print $2}'); do
	echo "  Formatting $f (vfat)..."
	mkfs.vfat -I -n $f "/dev/disk/by-partlabel/${f}"
done
for f in $(cat "${thisDir}/install.fstab" | awk '$3=="ext4"{print $1}' | awk -F= '{ print $2}'); do
	echo "  Formatting $f (ext4)..."
	mkfs.ext4 -F -L $f -E quotatype=usrquota:grpquota:prjquota "/dev/disk/by-partlabel/${f}"
done

echo "Mounting filesystems..."
cat "${thisDir}/install.fstab" | awk -v pref="${target}" '{$2=pref$2;print $0}' > /etc/fstab

for f in $(cat "${thisDir}/install.fstab" | awk '$2=="none"{next}{print $2}' | tr -s '/' | awk -F/ '{ print NF-1" "$0}' | sort -k 1 | awk '{ print $2}'); do
	mkdir -p "${target}/${f}"
	mount "${target}/${f}"
done

echo "Copying system files from $rootfs_source (this may take several minutes)..."
tar c --xattrs -C "$rootfs_source" . 2>/dev/null | tar x --xattrs-include='*.*' -C ${target}/ 2>/dev/null

echo "Setting up chroot environment..."
mount -t proc proc ${target}/proc
mount -t sysfs sys ${target}/sys
mount --bind /dev  ${target}/dev
mount --bind /run  ${target}/run

if mount -t efivarfs efivarfs ${target}/sys/firmware/efi/efivars; then
  echo "UEFI install selected"
  hasefi=1
else
  echo "Legacy install selected"
  hasefi=0
fi

rm -rf ${target}/usr/lib/dracut/modules.d/98gardenlinux-live
echo "Rebuilding initrd (this takes several minutes)..."
echo 'omit_dracutmodules+=" gardenlinux-live "' > ${target}/etc/dracut.conf.d/disable-gllive.conf
chroot ${target}/ /etc/kernel/postinst.d/dracut ${kernel}

echo "Installing bootloader..."
echo "persistent_policy=by-label" > ${target}/etc/dracut.conf.d/20-policy.conf
if [ "$hasefi" == "1" ]; then
  echo "  Installing UEFI bootloader..."
  chroot ${target} systemd-machine-id-setup
  
  # Get machine ID
  machine_id=$(cat ${target}/etc/machine-id 2>/dev/null || echo "default")
  
  # Copy kernel and initrd to the EFI partition using Boot Loader Specification layout
  echo "  Creating boot loader entries..."
  mkdir -p ${target}/boot/efi/${machine_id}/${kernel}
  cp ${target}/boot/vmlinuz-${kernel} ${target}/boot/efi/${machine_id}/${kernel}/linux
  cp ${target}/boot/initrd.img-${kernel} ${target}/boot/efi/${machine_id}/${kernel}/initrd
  
  # Create loader entry following Boot Loader Specification
  mkdir -p ${target}/boot/efi/loader/entries
  cat > ${target}/boot/efi/loader/entries/${machine_id}-${kernel}.conf <<BOOT_ENTRY
title      Garden Linux
version    ${kernel}
machine-id ${machine_id}
linux      /${machine_id}/${kernel}/linux
initrd     /${machine_id}/${kernel}/initrd
options    root=LABEL=ROOT ro console=ttyS0 console=tty0
BOOT_ENTRY

  # Create loader.conf to set default entry
  cat > ${target}/boot/efi/loader/loader.conf <<LOADER_CONF
default ${machine_id}-${kernel}.conf
timeout 3
console-mode max
editor no
LOADER_CONF

  # Install systemd-boot (after entries are in place)
  echo "  Installing bootctl..."
  chroot ${target} bootctl --esp-path=/boot/efi --make-machine-id-directory=yes install
else
  echo "  Installing BIOS bootloader (syslinux)..."
  chroot ${target} sfdisk --part-attrs ${targetDisk} 1 LegacyBIOSBootable
  chroot ${target} dd if="/usr/lib/SYSLINUX/gptmbr.bin" of=${targetDisk} bs=440 count=1 conv=notrunc
  chroot ${target} mkdir -p /boot/efi/syslinux
  chroot ${target} cp /usr/lib/syslinux/modules/bios/menu.c32 /boot/efi/syslinux/
  chroot ${target} cp /usr/lib/syslinux/modules/bios/libutil.c32 /boot/efi/syslinux/
  chroot ${target} syslinux --directory syslinux --install ${efiDev}
  
  # Create manual syslinux configuration (update-syslinux expects loader entries that don't exist in BIOS mode)
  echo "  Creating syslinux configuration..."
  
  # Find the kernel and initrd in /boot
  kernel_file=$(ls ${target}/boot/vmlinuz* 2>/dev/null | head -1 | xargs -r basename)
  initrd_file=$(ls ${target}/boot/initrd.img* 2>/dev/null | head -1 | xargs -r basename)
  
  if [ -n "$kernel_file" ] && [ -n "$initrd_file" ]; then
    echo "  Found kernel: $kernel_file"
    echo "  Found initrd: $initrd_file"
    
    # Copy kernel and initrd to /boot/efi for syslinux to access
    echo "  Copying kernel and initrd to /boot/efi..."
    cp ${target}/boot/$kernel_file ${target}/boot/efi/
    cp ${target}/boot/$initrd_file ${target}/boot/efi/
    
    cat > ${target}/boot/efi/syslinux/syslinux.cfg <<SYSLINUX_EOF
UI menu.c32
PROMPT 0
MENU TITLE Garden Linux
TIMEOUT 50
DEFAULT Garden Linux

LABEL Garden Linux
 LINUX /$kernel_file
 APPEND root=LABEL=ROOT ro console=ttyS0 console=tty0
 INITRD /$initrd_file
SYSLINUX_EOF
    echo "  Syslinux configuration created successfully"
  else
    echo "  ERROR: Could not find kernel or initrd files!"
    echo "  Contents of ${target}/boot:"
    ls -la ${target}/boot/ || true
    echo "  Contents of ${target}/boot/efi:"
    ls -la ${target}/boot/efi/ || true
    exit 1
  fi
fi
rm -f ${target}/etc/dracut.conf.d/20-policy.conf

# change root password (only in interactive mode)
if [ -z "${GL_INSTALL_TARGET:-}" ]; then
	echo
	echo "Please provide a password for the root user"
	chroot ${target} passwd
fi

echo "Finalizing installation..."

chroot ${target} rm -rf /etc/systemd/system/getty@tty1.service.d /etc/systemd/system/serial-getty@.service.d

cp /tmp/install.fstab ${target}/etc/fstab
chmod 0644 ${target}/etc/fstab

rm -f ${target}/root/{install,install,part}
echo "yes" > ${target}/.installed
