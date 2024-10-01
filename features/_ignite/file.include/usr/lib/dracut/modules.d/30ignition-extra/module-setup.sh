#!/bin/bash

depends() {
    echo "ignition"
}

install() {
    # ignition environment
    inst_script "$moddir/ignition-env-generator.sh" $systemdutildir/system-generators/ignition-env-generator
    inst_simple "$moddir/ignition-files.env" /etc/ignition-files.env
    inst_simple "$moddir/after-net-online.conf" "/etc/systemd/system/ignition-fetch.service.d/after-net-online.conf"
}
