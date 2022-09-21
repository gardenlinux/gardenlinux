#!/bin/bash

depends() {
    echo "ignition"
}

install() {
    # ignition environment
    inst_script "$moddir/ignition-env-generator.sh" $systemdutildir/system-generators/ignition-env-generator
    inst_simple "$moddir/ignition-files.env" /etc/ignition-files.env
}
