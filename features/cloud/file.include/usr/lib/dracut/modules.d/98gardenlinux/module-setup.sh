#!/bin/bash

check() {
    [[ $mount_needs ]] && return 1
    return 0
}

depends() {
    echo 'fs-lib'
}

install() {
    inst_multiple grep sfdisk growpart udevadm awk mawk sed rm readlink
    inst_hook pre-pivot 50 "$moddir/mount-usr.sh"
    inst_hook pre-pivot 00 "$moddir/grow-root.sh"
}
