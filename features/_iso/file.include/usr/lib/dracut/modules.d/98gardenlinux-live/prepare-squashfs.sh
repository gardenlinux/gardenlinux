#!/usr/bin/env bash

type getarg >/dev/null 2>&1 || . /lib/dracut-lib.sh
type info >/dev/null 2>&1 || . /lib/dracut-lib.sh
type warn >/dev/null 2>&1 || . /lib/dracut-lib.sh

set -e 

udevadm settle --timeout=30 --exit-if-exists=/dev/disk/by-label/GardenlinuxISO
mkdir /run/cdrom
mount /dev/disk/by-label/GardenlinuxISO /run/cdrom

ram=$(getarg gl.ram=)
ram="${ram#gl.ram=}"

case "$ram" in
	no,false,0,disabled,disable)
            ln -s /run/root.squashfs /run/cdrom/squashfs.img
            exit 1
            ;;
        *)
            cp /run/cdrom/squashfs.img /run/root.squashfs
	    umount /run/cdrom
            ;;
esac


exit 0
