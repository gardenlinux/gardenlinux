#!/bin/bash

# called by dracut
check() {
    return 255
}

# called by dracut
depends() {
    echo -n "kernel-network-modules "

    is_qemu_virtualized && echo -n "qemu-net "

    if ! dracut_module_included "systemd-networkd" && [ -x "$dracutsysrootdir/usr/libexec/nm-initrd-generator" ] ; then
        echo "systemd-networkd"
    else
        echo "systemd-networkd"
    fi
    return 0
}

# called by dracut
installkernel() {
    return 0
}

# called by dracut
install() {
    local _arch _i _dir

    inst_script "$moddir/netroot.sh" "/sbin/netroot"
    inst_simple "$moddir/net-lib.sh" "/lib/net-lib.sh"
    inst_hook pre-udev 50 "$moddir/ifname-genrules.sh"
    inst_hook cmdline 91 "$moddir/dhcp-root.sh"

    dracut_need_initqueue
}
