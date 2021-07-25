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
#  --image-size     Image size in GB
#  --read-only-usr  Make usr partition read only
#---help---

if [ ! ${EUID} -eq 0 ]; then
  echo 'must be run as root'
  exit 1
fi

help() {
	sed -En '/^#---help---/,/^#---help---/p' "$0" | sed -E 's/^# ?//; 1d;$d;'
	exit 1
}


# Run fsck 3 times on an ext4 image. Sometimes once is just not enough, but give up 
# if it takes more than 3 times.
fsckExt4() {

  local device=$1 ; shift
  local retries=0

  while ! fsck.ext4 -f -a -E discard,inode_count_fullmap -D ${device} ; do
    echo Errors detected, retrying the fsck.
    retries=$(($retries + 1))
    if [ $retries -gt 3 ]; then
      return 1
    fi
  done

}

target="bios,uefi"
fs_check=1
force=0
imagesz=2G
read_only_usr=0

while true; do
    flag=$1;
    case "$flag" in
        --grub-target) shift; target=$1; shift;;
        --force) shift; force=1;;
        --image-size) shift; imagesz=$1; shift;;
        --read-only-usr) shift; read_only_usr=1;;
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
type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, name="EFI", size=16MiB
type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, name="USR", size=1GiB
type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, name="ROOT"' | sfdisk $loopback --no-reread --no-tell-kernel
losetup -d $loopback
sync
while [ -n "$(losetup -l | grep $loopback)" ]; do sleep 1; echo -n "."; done; echo
loopback=$(losetup -f --partscan --show ${raw_image})
echo "### reconnected loopback to ${loopback}"

echo "### creating filesystems"
mkfs.vfat -n EFI ${loopback}p2
mkfs.ext4 -L USR  -E lazy_itable_init=0,lazy_journal_init=0 ${loopback}p3
mkfs.ext4 -L ROOT -E lazy_itable_init=0,lazy_journal_init=0 -I 256 ${loopback}p4
# part of debian-cloud-images, I am sure we want that :-) -> it is default
#tune2fs -c 0 -i 0 ${loopback}p3

echo "### mounting filesystems"
mkdir -p ${dir_name}          && mount ${loopback}p4 ${dir_name}
mkdir -p ${dir_name}/boot/efi && mount ${loopback}p2 ${dir_name}/boot/efi
mkdir -p ${dir_name}/usr      && mount ${loopback}p3 ${dir_name}/usr

echo "### copying $rootfs"
tar xf ${rootfs} --xattrs-include='*.*' -C ${dir_name}

mkdir -p ${dir_name}/proc	&& mount -t proc proc ${dir_name}/proc
mkdir -p ${dir_name}/sys	&& mount -t sysfs sys ${dir_name}/sys
mkdir -p ${dir_name}/dev	&& mount --bind /dev  ${dir_name}/dev
mount | grep $dir_name

if [ ${read_only_usr} == 1 ]; then
    opts_usr="defaults,discard,ro"
else
    opts_usr="defaults,discard,rw"
fi

#echo "### generating fstab"
#cat << EOF >> ${dir_name}/etc/fstab
## <file system>	<mount point>	<type>	<options>		<dump>	<pass>
#LABEL=ROOT	/		ext4	errors=remount-ro,x-systemd.growfs,prjquota 0	1
#LABEL=EFI	/boot/efi	vfat	umask=0077		0 	2
#$fstab_usr
#/dev/sr0	/media/cdrom0	udf,iso9660 user,noauto		0	0
#EOF

echo "### generating mount units - using blank fstab"
# Systemd mount units - not using fstab anymore
# rootfs
# old fstab entry : LABEL=ROOT	/		ext4	errors=remount-ro,x-systemd.growfs,prjquota 0	1
cat << EOF >> ${dir_name}/etc/systemd/system/remount-root.service
# This is used to mount the rootfs with proper mount options
[Unit]
Description=Remount rootfs when no fstab is in
DefaultDependencies=no
Conflicts=shutdown.target
Before=local-fs-pre.target local-fs.target shutdown.target
Wants=local-fs-pre.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/mount -o remount,rw,errors=remount-ro,prjquota,discard /

[Install]
WantedBy=local-fs.target
EOF

# handle x-systemd.growfs
cat << EOF >> ${dir_name}/etc/systemd/system/grow-root.service
[Unit]
Description=Grow root filesystem
DefaultDependencies=no
Conflicts=shutdown.target
Before=shutdown.target local-fs.target
After=remount-root.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/lib/systemd/systemd-growfs /
TimeoutSec=0

[Install]
WantedBy=local-fs.target
EOF

# usr
# old fstab entry : LABEL=USR   /usr        ext4    defaults,rw     0   2
cat << EOF >> ${dir_name}/etc/systemd/system/usr.mount
[Unit]
Wants=systemd-fsck@dev-disk-by\x2dlabel-USR.service
After=systemd-fsck@dev-disk-by\x2dlabel-USR.service
After=blockdev@dev-disk-by\x2dlabel-USR.target

[Mount]
Where=/usr
What=/dev/disk/by-label/USR
Type=ext4
Options=$opts_usr

[Install]
WantedBy=local-fs.target
EOF

# boot efi
# old fstab entry : LABEL=EFI	/boot/efi	vfat	umask=0077		0 	2
cat << EOF >> ${dir_name}/etc/systemd/system/boot-efi.mount
[Unit]
After=blockdev@dev-disk-by\x2dlabel-EFI.target

[Mount]
Where=/boot/efi
What=/dev/disk/by-label/EFI
Type=vfat
Options=umask=0077

[Install]
WantedBy=local-fs.target
EOF

# enable the systemd units
chroot ${dir_name} systemctl enable boot-efi.mount remount-root.service grow-root.service

echo "### installing grub"
for t in "${grub_target[@]}"
do
    case "$t" in
        bios) if [ -e ${dir_name}/usr/sbin/grub-install ]; then
		chroot ${dir_name} grub-install --recheck --target=i386-pc $loopback
	      else
		echo "no legacy support"
	      fi ;;
        uefi) if [ -e ${dir_name}/usr/sbin/grub-install ]; then
	        chroot ${dir_name} grub-install --recheck --target=x86_64-efi --no-nvram  $loopback
	      else
		chroot ${dir_name} bootctl --no-variables install 
	      fi ;;
        *) echo "Unknown target ${t}";;
    esac
done
if [ -e ${dir_name}/usr/sbin/grub-install ]; then
  mv ${dir_name}/etc/grub.d/30_uefi-firmware ${dir_name}/etc/grub.d/30_uefi-firmware~
  chroot ${dir_name} update-grub
  mv ${dir_name}/etc/grub.d/30_uefi-firmware~ ${dir_name}/etc/grub.d/30_uefi-firmware
fi

echo "### unmouting"
umount -R ${dir_name}

echo "### final fsck, just to be sure"
fsck.vfat -f -a ${loopback}p2
fsckExt4  ${loopback}p3
fsckExt4  ${loopback}p4
sync

tune2fs -Q usrquota,grpquota,prjquota ${loopback}p4
sync

losetup -d $loopback

rmdir ${dir_name}
