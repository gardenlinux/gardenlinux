#!/bin/bash

check() {
    return 0
}

install() {
    # gardenlinux immutability
    inst_simple "$moddir/gardenlinux-immutability.service" $systemdutildir/system/gardenlinux-immutability.service
    ln_r ../gardenlinux-immutability.service $systemdutildir/system/initrd-root-device.target.wants/gardenlinux-immutability.service
    inst_script "$moddir/reset-system" /usr/local/sbin/reset-system
    inst_simple "$moddir/reset-system.cfg" /etc/reset-system.cfg
}