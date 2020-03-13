#!/bin/sh -x


# note: the debian-cloud-image build has 30G for Azrue and 2 
# for all others, we need to maek that configurable... No idea
# why that is
dd if=/dev/zero of=$1.raw seek=2048 bs=1 count=0 seek=2G
loopback=$(losetup -f --show $1.raw)

echo 'label: gpt
type=21686148-6449-6E6F-744E-656564454649, name="BIOS", size=1MiB
type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, name="EFI", size=127MiB
type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, name="ROOT"' | sfdisk $loopback
partprobe $loopback

mkfs.vfat ${loopback}p2 -n EFI
mkfs.ext4 ${loopback}p3 -L ROOT

mkdir -p $1
mount ${loopback}p3 $1
mkdir -p $1/boot/efi
mount ${loopback}p2 $1/boot/efi

tar xf $2 -C $1

mount -t proc proc $1/proc
mount -t sysfs sys $1/sys
mount --bind /dev  $1/dev

chroot $1 grub-install --target=i386-pc /dev/loop0
chroot $1 grub-install --target=x86_64-efi /dev/loop0 --no-nvram
chroot $1 update-grub
sleep 5
umount -l $1/dev
umount -l $1/sys
umount -l $1/proc
umount -l $1/boot/efi
sleep 5
umount -l $1
sleep 5
losetup -d $loopback
