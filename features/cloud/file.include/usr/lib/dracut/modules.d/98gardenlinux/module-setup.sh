#!/bin/bash

check() {
    return 0
}

depends() {
    echo "dracut-systemd"
}

install() {
    # FIXME: remove tr, base should include it
    inst_multiple systemd-detect-virt systemd-cat
   
    # clock source
    if [ -f "$moddir/clocksource-setup.sh" ]; then
        inst_hook pre-pivot 00 "$moddir/clocksource-setup.sh"
    fi
}
