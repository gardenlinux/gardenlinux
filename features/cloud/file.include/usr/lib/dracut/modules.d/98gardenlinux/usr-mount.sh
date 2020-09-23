#!/bin/sh

mountUnit="/sysroot/etc/systemd/system/usr.mount"

FSTYPE=$(awk -F= '/^Type=/ { print $2}' "$mountUnit")
DEVICE=$(awk -F= '/^What=/ { print $2}' "$mountUnit")
OPTIONS=$(awk -F= '/^Options=/ { print $2}' "$mountUnit") 

DEVNAME=$(systemd-escape -p "$DEVICE")
# create the mount unit in ramdisk
{
echo "[Unit]"
echo "Before=initrd-root-fs.target"
echo "Requires=systemd-fsck@${DEVNAME}.service"
echo "After=sysroot.mount"
echo "[Mount]"
echo "Where=/sysroot/usr"
echo "What=$DEVICE"
echo "Options=$OPTIONS"
echo "Type=$FSTYPE"
} > /etc/systemd/system/sysroot-usr.mount

systemctl -q add-wants initrd-fs.target sysroot-usr.mount
