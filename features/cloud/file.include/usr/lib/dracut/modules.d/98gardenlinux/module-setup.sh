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
    # FIXME: remove tr, base should include it
    inst_multiple tr grep sfdisk growpart udevadm awk mawk sed rm readlink systemd-detect-virt systemd-cat
   
    # grow root
    if [ -f "$moddir/growroot.sh" ]; then
        inst_hook pre-mount 00 "$moddir/growroot.sh"
    fi

    # clock source
    if [ -f "$moddir/clocksource-setup.sh" ]; then
        inst_hook pre-pivot 00 "$moddir/clocksource-setup.sh"
    fi
}
