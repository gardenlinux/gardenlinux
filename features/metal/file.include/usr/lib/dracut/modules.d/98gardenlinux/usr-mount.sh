#!/bin/sh

mountUnit="/sysroot/etc/systemd/system/usr.mount"

FSTYPE=$(awk -F= '/^Type=/ { print $2}' "$mountUnit")
DEVICE=$(awk -F= '/^What=/ { print $2}' "$mountUnit")
OPTIONS=$(awk -F= '/^Options=/ { print $2}' "$mountUnit") 

echo "FSTYPE=${FSTYPE}
DEVICE=${DEVICE}
OPTIONS=${OPTIONS}
DEVNAME=${DEVNAME}" > /run/systemd/sysroot-usr.env
