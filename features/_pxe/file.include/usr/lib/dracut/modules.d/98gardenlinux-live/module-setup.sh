#!/bin/bash

check() {
    [[ $mount_needs ]] && return 1
    return 0
}

depends() {
    echo "fs-lib dracut-systemd systemd-networkd"
}

install() {
    #inst_multiple grep sfdisk growpart udevadm awk mawk sed rm readlink
    inst_multiple curl grep sfdisk awk mawk file sha256sum
   
    inst_simple "$moddir/live-get-squashfs.service" ${systemdsystemunitdir}/live-get-squashfs.service
    inst_script "$moddir/live-get-squashfs.sh" /sbin/live-get-squashfs
    inst_script "$moddir/live-sysroot-generator.sh" $systemdutildir/system-generators/live-sysroot-generator
    inst_script "$moddir/live-overlay-setup.sh" $systemdutildir/system-generators/live-overlay-setup
    systemctl -q --root "$initdir" add-wants initrd-root-fs.target live-get-squashfs.service 
    
    # for ignition
    inst_simple "$moddir/is-live-image.sh" "/usr/bin/is-live-image"

    inst_simple "/usr/lib/file/magic.mgc" "/usr/lib/file/magic.mgc"
}
