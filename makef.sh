#!/bin/sh

dd if=/dev/zero of=$1.raw seek=2048 bs=1 count=0 seek=2G
loopback=$(losetup -f --show $1.raw)

echo 'label: gpt
type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, name="EFI", size=128MiB
type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, name="ROOT"' | sfdisk $loopback
partprobe $loopback

mkfs.vfat ${loopback}p1 -n EFI
mkfs.ext4 ${loopback}p2 -L ROOT

mkdir -p $1
mount ${loopback}p2 $1
mkdir -p $1/boot/efi
mount ${loopback}p1 $1/boot/efi

tar xf $2 -C $1

mount -t proc proc $1/proc
mount -t sysfs sys $1/sys
mount --bind /dev  $1/dev



