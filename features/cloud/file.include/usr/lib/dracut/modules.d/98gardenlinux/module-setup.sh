#!/bin/bash

check() {
    [[ $mount_needs ]] && return 1
    return 0
}

depends() {
    echo "fs-lib"
    echo "dracut-systemd"
}

install() {
    inst_multiple grep sfdisk growpart udevadm awk mawk sed rm readlink
   
    # grow root
    if [ -f "$moddir/growroot.sh" ]; then
        inst_hook pre-mount 00 "$moddir/growroot.sh"
    fi

    # handle usr mounting
    if [[ -f "$moddir/usr-mount.service" ]] && [[ -f "$moddir/usr-mount.sh" ]]; then
        inst_simple "$moddir/usr-mount.service" ${systemdsystemunitdir}/usr-mount.service
        inst_simple "$moddir/sysroot-usr-fsck.service" ${systemdsystemunitdir}/sysroot-usr-fsck.service
        inst_simple "$moddir/sysroot-usr.mount" ${systemdsystemunitdir}/sysroot-usr.mount
        inst_script "$moddir/usr-mount.sh" /bin/usr-mount.sh
        systemctl -q --root "$initdir" add-wants initrd-root-fs.target usr-mount.service
        systemctl -q --root "$initdir" add-wants initrd-root-fs.target sysroot-usr-fsck.service 
        systemctl -q --root "$initdir" add-wants initrd-root-fs.target sysroot-usr.mount 
    fi
}
