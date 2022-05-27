#!/bin/bash

# run-shellcheck
#
# CIS Debian Hardening
#

#
# 1.7.1.4 Ensure SELinux is activated (Scored)
#

set -e # One error, it's over
set -u # One variable unset, it's over

# shellcheck disable=2034
HARDENING_LEVEL=3
# shellcheck disable=2034
DESCRIPTION="Ensure SELinux is enforcing."

# This function will be called if the script status is on enabled / audit mode
audit() {
    ERROR=0
    get_selinux_status
    if [ "$FNRET" != 0 ]; then
        crit "SELinux is not active."
        ERROR=1
    else
        ok "SELinux is active."
    fi
}

# Get SELinux status 
get_selinux_status() {
    STATUS=$(getenforce)
    if [ $STATUS == "Enforcing" ]; then
        FNRET=0
    else
        FNRET=1
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
