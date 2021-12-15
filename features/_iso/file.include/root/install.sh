#!/usr/bin/env bash

set -e

echo "Please provide the device where you would like to install e.g. /dev/sda:"
read targetDisk 

echo "You are about to install to $targetDisk"
echo
echo "Using the following partition configuration:"
cat install.part
echo
echo "Using the following fstab:"
cat install.fstab
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

cat install.fstab | awk -v pref="${target}" '{$2=pref$2;print $0}' > /etc/fstab 

for f in $(cat install.fstab | awk '$2=="none"{next}{print $2}' | tr -s '/' | awk -F/ '{ print NF-1" "$0}' | sort -k 1 | awk '{ print $2}'); do
	mkdir -p "${target}/${f}"
	mount "${target}/${f}"
done

tar c --xattrs -C /run/rootfs . | tar xv --xattrs-include='*.*' -C ${target}/

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

# disable selinux
rm -f ${target}/.autorelabel
rm -f ${target}/etc/kernel/cmdline.d/90-selinux.cfg
chroot ${target} update-kernel-cmdline

rm -rf ${target}/usr/lib/dracut/modules.d/98gardenlinux-live
chroot ${target}/ /etc/kernel/postinst.d/dracut ${kernel}

echo "persistent_policy=by-label" > ${target}/etc/dracut.conf.d/20-policy.conf
if [ "$hasefi" == "1" ]; then
  mkdir -p ${target}/boot/efi/Default
  chroot ${target} /etc/kernel/postinst.d/zz-kernel-install ${kernel}
  chroot ${target} bootctl --esp-path=/boot/efi --make-machine-id-directory=no install
else
  chroot ${target} sfdisk --part-attrs ${targetDisk} 1 LegacyBIOSBootable
  chroot ${target} dd if="/usr/lib/SYSLINUX/gptmbr.bin" of=${targetDisk} bs=440 count=1 conv=notrunc
  chroot ${target} mkdir -p /boot/efi/syslinux
  chroot ${target} cp /usr/lib/syslinux/modules/bios/menu.c32 /boot/efi/syslinux/
  chroot ${target} cp /usr/lib/syslinux/modules/bios/libutil.c32 /boot/efi/syslinux/
  chroot ${target} syslinux --directory syslinux --install ${efiDev}
  chroot ${target} update-syslinux
fi
rm -f ${target}/etc/dracut.conf.d/20-policy.conf

# change root password
echo
echo "Please provide a password for the root user"
chroot ${target} passwd 

echo "Cleaning up"

chroot ${target} rm -rf /etc/systemd/system/getty@tty1.service.d /etc/systemd/system/serial-getty@.service.d

mv install.fstab ${target}/etc/fstab
chmod 0644 ${target}/etc/fstab

rm -f ${target}/root/{install,install,part}
echo "yes" >  ${target}/iso-installed
umount -l -R ${target}

echo "Safe to reboot now"
