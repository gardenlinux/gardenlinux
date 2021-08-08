#!/bin/sh

set -x
set -e
target=${1:-/dev/sda}

apt-get update
apt-get install -y dosfstools lvm2 kexec-tools

echo 'label: gpt
type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, name="EFI", size=512MiB
type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, name="ROOT", size=20GiB
type=E6D6D379-F507-44C2-A23C-238F2A3DF928, name="DATA"
' | sfdisk $target

umount -R /mnt || /bin/true
mkfs.vfat -I -n EFI ${target}1
mkfs.ext4 -F -L ROOT -E lazy_itable_init=0,lazy_journal_init=0,quotatype=usrquota:grpquota:prjquota ${target}2
pvcreate -y --pvmetadatacopies=2 ${target}3

mount ${target}2 /mnt
mkdir -p /mnt/efi
mount ${target}1 /mnt/efi
mkdir -p /mnt/efi/Default

mkdir -p /tmp/aa
mount -t overlay ovl /tmp/aa -o lowerdir=/run/rootfs,upperdir=/run/sysroot.ovl/upper,workdir=/run/sysroot.ovl/work
tar c --xattrs -C /tmp/aa . | tar xv --xattrs-include='*.*' -C /mnt
umount /tmp/aa

mount -t proc proc /mnt/proc
mount -t sysfs sys /mnt/sys
mount --bind /dev  /mnt/dev
mount -t efivarfs efivarfs /mnt/sys/firmware/efi/efivars

cat << EOF >> /mnt/etc/systemd/system/efi.mount
[Unit]
After=blockdev@dev-disk-by\x2dlabel-EFI.target

[Mount]
Where=/efi
What=/dev/disk/by-label/EFI
Type=vfat
Options=umask=0077

[Install]
WantedBy=local-fs.target
EOF

cat << EOF >> /mnt/etc/systemd/system/remount-root.service
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
chroot /mnt systemctl enable efi.mount remount-root.service

echo "omit_dracutmodules+=\" gardenlinux-live \"" >> /mnt/etc/dracut.conf
chroot /mnt dracut --force

chroot /mnt /etc/kernel/postinst.d/zz-kernel-install 5.10.0-6-amd64
chroot /mnt bootctl install

kexec -l /mnt/efi/Default/5.10.0-6-amd64/linux --initrd=/mnt/efi/Default/5.10.0-6-amd64/initrd.img-5.10.0-6-amd64 --command-line="root=LABEL=ROOT ro console=ttyS1,115200n8 console=tty0 earlyprintk=ttyS1,115200n8 consoleblank=0"
kexec -e
