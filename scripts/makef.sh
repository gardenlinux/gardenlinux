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
imagesz=2G

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
echo "### Generating sparsed image file ${raw_image} with ${imagesz}"
dd if=/dev/zero of=${raw_image} bs=1 count=0 seek=${imagesz}
loopback=$(losetup -f --show ${raw_image})
#trap "[ -n $loopback ] && losetup -d $loopback" EXIT

echo "### using ${loopback}"
echo 'label: gpt
type=21686148-6449-6E6F-744E-656564454649, name="BIOS", size=1MiB
type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, name="EFI",  size=16MiB
type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, name="ROOT"' | sfdisk $loopback --no-reread --no-tell-kernel
losetup -d $loopback
sync
while [ -n "$(losetup -l | grep $loopback)" ]; do sleep 1; echo -n "."; done; echo
loopback=$(losetup -f --partscan --show ${raw_image})
echo "### reconnected loopback to ${loopback}"

echo "### creating filesystems"
mkfs.vfat -n EFI ${loopback}p2
mkfs.ext4 -L ROOT -E lazy_itable_init=0,lazy_journal_init=0 ${loopback}p3
if [[ $fs_check == 0 ]]; then
    # part of debian-cloud-images, I am sure we want that :-)
    tune2fs -c 0 -i 0 ${loopback}p3
fi

echo "### mounting filesystems"
mkdir -p ${dir_name}		&& mount ${loopback}p3 ${dir_name}
mkdir -p ${dir_name}/boot/efi	&& mount ${loopback}p2 ${dir_name}/boot/efi
mkdir -p ${dir_name}/proc	&& mount -t proc proc ${dir_name}/proc
mkdir -p ${dir_name}/sys	&& mount -t sysfs sys ${dir_name}/sys
mkdir -p ${dir_name}/dev	&& mount --bind /dev  ${dir_name}/dev
mount | grep $dir_name

echo "### copying $rootfs"
tar xf ${rootfs} --xattrs-include='*.*' -C ${dir_name} --exclude proc --exclude sys --exclude dev

echo "### generating fstab"
cat << EOF >> ${dir_name}/etc/fstab
# <file system>	<mount point>	<type>	<options>		<dump>	<pass>
LABEL=ROOT	/		ext4	errors=remount-ro,x-systemd.growfs 0	1
LABEL=EFI	/boot/efi	vfat	umask=0077		0 	2
/dev/sr0	/media/cdrom0	udf,iso9660 user,noauto		0	0
EOF

echo "### installing grub"
for t in "${grub_target[@]}"
do
    case "$t" in
        bios) chroot ${dir_name} grub-install --recheck --target=i386-pc $loopback;;
        uefi) chroot ${dir_name} grub-install --recheck --target=x86_64-efi --no-nvram  $loopback ;;
        *) echo "Unknown target ${t}";;
    esac
done
mv ${dir_name}/etc/grub.d/30_uefi-firmware ${dir_name}/etc/grub.d/30_uefi-firmware~
chroot ${dir_name} update-grub
mv ${dir_name}/etc/grub.d/30_uefi-firmware~ ${dir_name}/etc/grub.d/30_uefi-firmware

echo "### unmouting"
umount -R ${dir_name}
sync

echo "### final fsck, just to be sure"
fsck.vfat -f -a ${loopback}p2
fsck.ext4 -f -a -E discard,inode_count_fullmap -D ${loopback}p3
sync

losetup -d $loopback

rmdir ${dir_name}
