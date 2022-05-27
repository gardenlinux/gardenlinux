#!/bin/bash

set -Eeuo pipefail

CGROUP_CMDLINE="/etc/kernel/cmdline.d/80-cgroup.cfg"
CGROUP_GARDENER="/var/lib/gardener-gardenlinux/etc/cgroup_version"

function get_fs_of_directory {
    [ -z "$1" -o ! -d "$1" ] && return
    echo -n "$(stat -c %T -f "$1")"
}

function check_current_cgroup {
    # determining if the system is running cgroupv1 or cgroupv2
    # using systemd approach as in
    # https://github.com/systemd/systemd/blob/d6d450074ff7729d43476804e0e19c049c03141d/src/basic/cgroup-util.c#L2105-L2149

    CGROUP_ID="cgroupfs"
    CGROUP2_ID="cgroup2fs"
    TMPFS_ID="tmpfs"

    cgroup_dir_fs="$(get_fs_of_directory /sys/fs/cgroup)"

    if [[ "$cgroup_dir_fs" == "$CGROUP2_ID" ]]; then
        echo "v2"
        return
    elif [[ "$cgroup_dir_fs" == "$TMPFS_ID" ]]; then
        if [[ "$(get_fs_of_directory /sys/fs/cgroup/unified)" == "$CGROUP2_ID" ]]; then
            echo "v1 (cgroupv2systemd)"
            return
        fi
        if [[ "$(get_fs_of_directory /sys/fs/cgroup/systemd)" == "$CGROUP2_ID" ]]; then
            echo "v1 (cgroupv2systemd232)"
            return
        fi
        if [[ "$(get_fs_of_directory /sys/fs/cgroup/systemd)" == "$CGROUP_ID" ]]; then
            echo "v1"
            return
        fi
    fi
    # if we came this far despite all those returns, it means something went wrong
    echo "failed to determine cgroup version for this system" >&2
    exit 1
}

# no need to run if Gardener did not place a configuration for cgroups
[ ! -f "$CGROUP_GARDENER" ] && exit 0

desired_cgroup=$(cat "$CGROUP_GARDENER")
current_cgroup=$(check_current_cgroup)

if [[ "$desired_cgroup" == "v1" ]]; then
    echo "configuring system to use cgroup v1"
    cat << '__EOF' > "$CGROUP_CMDLINE"
# Disable cgroup v2 support

CMDLINE_LINUX="$CMDLINE_LINUX systemd.unified_cgroup_hierarchy=0"
__EOF

elif [[ "$desired_cgroup" == "v2" ]]; then
    echo "configuring system to use cgroup v2"
    cat << '__EOF' > "$CGROUP_CMDLINE"
# Enable cgroup v2 support

CMDLINE_LINUX="$CMDLINE_LINUX systemd.unified_cgroup_hierarchy=1"
__EOF

else
    echo "desired cgroup version $desired_cgroup cannot be enabled, leaving system with $current_cgroup"
    exit 1
fi

# update bootloader
/usr/local/sbin/update-syslinux

if [[ "$desired_cgroup" == "${current_cgroup%% *}" ]]; then
    echo "system already running with cgroup $desired_cgroup - not triggering a reboot"
    exit 0
else
    echo "scheduling a reboot to activate cgroup $desired_cgroup"
    mkdir -p /var/run/gardener-gardenlinux
    touch /var/run/gardener-gardenlinux/restart-required
fi
