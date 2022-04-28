# 1.2.2 Ensure APT GPG keys are configured (Not scored)
#

set -e # One error, it's over
set -u # One variable unset, it's over

# shellcheck disable=2034
HARDENING_LEVEL=1
# shellcheck disable=2034
DESCRIPTION="GPG APT Key are present"

# This function will be called if the script status is on enabled / audit mode
audit() {
    get_apt_gpg
    if [ "$FNRET" = 0 ]; then
        ok "APT policy looks good"
    else
        crit "APT policy is broken"
    fi

    get_apt_gl_gpg
    if [ "$FNRET" = 0 ]; then 
        ok "Garden Linux repository is configured"
    else    
        crit "Garden Linux repository is not configured" 
    fi
}

# This function will check config parameters required
check_config() {
    :
}

# Get APT GPG 
get_apt_gpg() {
    STATUS=$(apt-key list)
    retVal=$?
    if [ $retVal > 0  ]; then
        FNRET=0
    else
        FNRET=1
    fi
}

# Get GL key from APT GPG
get_apt_gl_gpg() {
    OUTPUT=$(apt-key list | grep "Garden Linux Automatic Signing Key" | awk {'print $4 $5'})
    if [ $OUTPUT == "GardenLinux" ]; then
        FNRET=0
    else
        FNRET=1
    fi
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
