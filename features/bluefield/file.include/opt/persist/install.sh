#!/usr/bin/env bash

set -e

thisDir=$(readlink -f $(dirname "${BASH_SOURCE[0]}"))

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

kernel=$(uname -r)
target=/opt/onmetal-install

#TODO: add check for existing ROOT/EFI partitions
#TODO: check if targetDisk is valid
#NOTE: for the time being we consider LABEL=PARTLABEL

cat install.part | sfdisk $targetDisk
rootDev="/dev/disk/by-partlabel/ROOT"
efiDev="/dev/disk/by-partlabel/EFI"
udevadm settle --timeout=30

for f in $(cat install.fstab | awk '$3=="vfat"{print $1}' | awk -F= '{ print $2}'); do
        mkfs.vfat -I -n $f "/dev/disk/by-partlabel/${f}"
done
for f in $(cat install.fstab | awk '$3=="ext4"{print $1}' | awk -F= '{ print $2}'); do
        mkfs.ext4 -F -L $f -E quotatype=usrquota:grpquota:prjquota "/dev/disk/by-partlabel/${f}"
done

cat "${thisDir}/install.fstab" | awk -v pref="${target}" '{$2=pref$2;print $0}' > /etc/fstab

for f in $(cat "${thisDir}/install.fstab" | awk '$2=="none"{next}{print $2}' | tr -s '/' | awk -F/ '{ print NF-1" "$0}' | sort -k 1 | awk '{ print $2}'); do
        mkdir -p "${target}/${f}"
        mount "${target}/${f}"
done

# remove all other boot loaders 
echo "removing other bootloaders ..."
for i in $(efibootmgr | grep "Linux Boot Manager" | sed "s/Boot\([0-9A-Z]*\)\*\? .*/\1/"); do
    efibootmgr -B -b $i > /dev/null
    echo
done
for i in $(efibootmgr | grep "UEFI OS" | sed "s/Boot\([0-9A-Z]*\)\*\? .*/\1/"); do
    efibootmgr -B -b $i > /dev/null
    echo
done
for i in $(efibootmgr | grep "debian" | sed "s/Boot\([0-9A-Z]*\)\*\? .*/\1/"); do
    efibootmgr -B -b $i > /dev/null
    echo
done
tar c --xattrs -C /run/rootfs . | tar xv --xattrs-include='*.*' -C ${target}/

mount -t proc proc ${target}/proc
mount -t sysfs sys ${target}/sys
mount --bind /dev  ${target}/dev
mount --bind /run  ${target}/run
mount -t efivarfs efivarfs ${target}/sys/firmware/efi/efivars

chroot ${target} systemd-machine-id-setup
chroot ${target} bootctl --esp-path=/efi --make-machine-id-directory=yes install
# TODO: regen initrd and reinstall kernels for the bootloader
#chroot ${target} /etc/kernel/postinst.d/zz-kernel-install ${kernel}

# change root password
echo
echo "Please provide a password for the root user"
chroot ${target} passwd

echo "Cleaning up"

chroot ${target} rm -rf /etc/systemd/system/getty@tty1.service.d /etc/systemd/system/serial-getty@.service.d

cp "${thisDir}/install.fstab" ${target}/etc/fstab
chmod 0644 ${target}/etc/fstab

rm -f ${target}/root/{install,install,part}
umount -l -R ${target}

echo "Safe to reboot now"
