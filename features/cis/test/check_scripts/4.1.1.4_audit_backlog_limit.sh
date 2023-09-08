#!/bin/bash

# run-shellcheck
#
# CIS Debian Hardening
#

#
# 4.1.1.4 Ensure audit_backlog_limit is sufficient (Scored)
#

set -u # One variable unset, it's over

# shellcheck disable=2034
HARDENING_LEVEL=4
# shellcheck disable=2034
DESCRIPTION="Configure audit_backlog_limit to be sufficient."

GRUB='/etc/default/grub'
SYSLINUX='/efi/syslinux/syslinux.cfg'
GRUB_OPTIONS='^GRUB_CMDLINE_LINUX=".*audit_backlog_limit=8192'
SYSLINUX_OPTIONS='^\sAPPEND root=.*audit_backlog_limit=8192.'

# This function will be called if the script status is on enabled / audit mode
audit() {

    FILE_ERR=1
    BOOTLOADER="NONE"

    does_file_exist "$GRUB"
    if [ "$FNRET" -eq 0 ]; then
        FILE_ERR=0
        BOOTLOADER="GRUB"
        OUTPUT=$(grep -E "$GRUB_OPTIONS" "$GRUB")
        retVal=$?
        if [ $retVal -eq 0  ]; then
            ok "Audit log backlog limit is set in GRUB bootloader"
        else
            crit "Audit log backlog limit is not set in GRUB bootloader"
        fi
    fi

    does_file_exist "$SYSLINUX"
    if [ "$FNRET" -eq 0 ]; then
        FILE_ERR=0
        BOOTLOADER="SYSLINUX"
        OUTPUT=$(grep -E "$SYSLINUX_OPTIONS" "$SYSLINUX")
        retVal=$?
        if [ $retVal -eq 0  ]; then
            ok "Audit log backlog limit is set in SYSLINUX bootloader"
        else
            crit "Audit log backlog limit is not set in SYSLINUX bootloader"
        fi
    fi
    if [ "$FILE_ERR" -gt 0 ]; then
        crit "No bootloader file found"
    else
        ok "Bootloader $BOOTLOADER found"
    fi

}

# This function will check config parameters required
check_config() {
    :
}

# Source Root Dir Parameter
if [ -r /etc/default/cis-hardening ]; then
    # shellcheck source=../../debian/default
    . /etc/default/cis-hardening
fi
if [ -z "$CIS_ROOT_DIR" ]; then
    echo "There is no /etc/default/cis-hardening file nor cis-hardening directory in current environment."
    echo "Cannot source CIS_ROOT_DIR variable, aborting."
    exit 128
fi

# Main function, will call the proper functions given the configuration (audit, enabled, disabled)
if [ -r "$CIS_ROOT_DIR"/lib/main.sh ]; then
    # shellcheck source=../../lib/main.sh
    . "$CIS_ROOT_DIR"/lib/main.sh
else
    echo "Cannot find main.sh, have you correctly defined your root directory? Current value is $CIS_ROOT_DIR in /etc/default/cis-hardening"
    exit 128
fi
