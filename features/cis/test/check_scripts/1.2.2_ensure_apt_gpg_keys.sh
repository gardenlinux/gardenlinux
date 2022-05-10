#!/bin/bash

# run-shellcheck
#
# CIS Debian Hardening
#

#
# 1.2.2 Ensure APT GPG Keys (not scored)
#

set -e # One error, it's over
set -u # One variable unset, it's over

# shellcheck disable=2034
HARDENING_LEVEL=0
# shellcheck disable=2034
DESCRIPTION="Check for GPG key in repo list."

FILES="/etc/apt/sources.list"
DIRECTORY="/etc/apt"
PATTERN='signed-by=/etc/apt/trusted.gpg.d/gardenlinux.asc'

# This function will be called if the script status is on enabled / audit mode
audit() {
    FILES="$FILES $($SUDO_CMD find $DIRECTORY -type f)"
    FOUND=0
    for FILE in $FILES; do
        does_pattern_exist_in_file "$FILE" "$PATTERN"
        if [ "$FNRET" = 0 ]; then
            FOUND=1
        fi
    done
    if [ $FOUND = 1 ]; then
        ok "$PATTERN is present in $FILES"
    else
        crit "$PATTERN is not present in $FILES"
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
