#!/usr/bin/env bash

set -Eeuo pipefail

#---help---
# usage: makef [options] <raw image file> <rootfs>
#
# Arguments:
#  <raw image file> Image file that will be created (without extension=
#  <rootfs>         Archive that contains the root file system
# Options:
#  --gub-target     Comma separeted list of targets: bios, uefi
#  --fs-check-off   Disable possible file system
#  --image-type     Comma separated list of types: raw, vmdk TODO
#---help---

if [ ! ${EUID} -eq 0 ]; then
  echo 'must be run as root'
  exit 1
fi

help() {
	sed -En '/^#---help---/,/^#---help---/p' "$0" | sed -E 's/^# ?//; 1d;$d;'
	exit 1
}

target="bios,uefi"
fs_check=1
force=0

while true; do
    flag=$1;
    case "$flag" in
        --grub-target) shift; target=$1; shift;;
        --fs-check-off) shift; fs_check=0;;
        --force) shift; force=1;;
        *) break
    esac
done

IFS="," read -r -a grub_target <<< "$target"

raw_image=${1}.raw
dir_name=$1
rootfs=$2

if [[ -e ${raw_image} && ${force} == 0 ]]; then
    echo "Raw image ${raw_image} exists."
    exit 1
fi

if [[ ! -f ${rootfs} ]] ; then
    echo "Root file system archive ${rootfs} does not exist."
    exit 1
fi

# note: the debian-cloud-image build has 30G for Azrue and 2
# for all others, we need to maek that configurable... No idea
# why that is
dd if=/dev/zero of=${raw_image} seek=2048 bs=1 count=0 seek=2G
loopback=$(losetup -f --show ${raw_image})

echo 'label: gpt
type=21686148-6449-6E6F-744E-656564454649, name="BIOS", size=1MiB
type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, name="EFI", size=127MiB
type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, name="ROOT"' | sfdisk $loopback
partprobe $loopback

mkfs.vfat ${loopback}p2 -n EFI
mkfs.ext4 ${loopback}p3 -L ROOT

if [[ $fs_check == 0 ]]; then
    # part of debian-cloud-images, I am sure we want that :-)
    tune2fs -c 0 -i 0 ${loopback}p3
fi

mkdir -p ${dir_name}
mount ${loopback}p3 ${dir_name}
mkdir -p ${dir_name}/boot/efi
mount ${loopback}p2 ${dir_name}/boot/efi

tar xf ${rootfs} -C ${dir_name}

mount -t proc proc ${dir_name}/proc
mount -t sysfs sys ${dir_name}/sys
mount --bind /dev  ${dir_name}/dev

cat << EOF >> ${dir_name}/etc/fstab
# <file system>	<mount point>	<type>	<options>		<dump>	<pass>
LABEL=ROOT	/		ext4	errors=remount-ro,x-systemd.growfs 0	1
LABEL=EFI	/boot/efi	vfat	umask=0077		0 	2
/dev/sr0	/media/cdrom0	udf,iso9660 user,noauto		0	0
EOF

for t in "${grub_target[@]}"
do
    case "$t" in
        bios) chroot ${dir_name} grub-install --target=i386-pc $loopback;;
        uefi) chroot ${dir_name} grub-install --target=x86_64-efi --no-nvram  $loopback ;;
        *) echo "Unknown target ${t}";;
    esac
done

chroot ${dir_name} update-grub
sleep 2
umount -l ${dir_name}/dev
umount -l ${dir_name}/sys
umount -l ${dir_name}/proc
umount -l ${dir_name}/boot/efi
sleep 2
umount -l ${dir_name}
fsck.vfat -a ${loopback}p2
fsck.ext4 -a ${loopback}p3
sleep 2
losetup -d $loopback

rmdir ${dir_name}
