#!/bin/bash

check() {
    [[ $mount_needs ]] && return 1
    return 0
}

depends() {
    echo "fs-lib dracut-systemd"
}

install() {
    inst_multiple grep awk mawk file
   
    inst_simple "$moddir/prepare-squashfs.service" ${systemdsystemunitdir}/prepare-squashfs.service
    inst_script "$moddir/prepare-squashfs.sh" /sbin/prepare-squashfs
    inst_script "$moddir/live-sysroot-generator.sh" $systemdutildir/system-generators/live-sysroot-generator
    inst_script "$moddir/squash-mount-generator.sh" $systemdutildir/system-generators/squash-mount-generator
    inst_script "$moddir/live-overlay-setup.sh" $systemdutildir/system-generators/live-overlay-setup
    inst_hook initqueue/finished 90 "$moddir/prepare-squashfs.sh"
    inst_rules 60-cdrom_id.rules
    dracut_need_initqueue
}
