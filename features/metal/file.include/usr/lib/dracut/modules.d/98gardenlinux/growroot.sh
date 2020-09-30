#!/bin/sh

type getarg >/dev/null 2>&1 || . /lib/dracut-lib.sh
type info >/dev/null 2>&1 || . /lib/dracut-lib.sh
type warn >/dev/null 2>&1 || . /lib/dracut-lib.sh

# rootdev detection based on 98dracut-systemd/rootfs-generator

root=$(getarg root=)

case "$root" in
    block:LABEL=*|LABEL=*)
        root="${root#block:}"
        root="$(echo $root | sed 's,/,\\x2f,g')"
        root="/dev/disk/by-label/${root#LABEL=}"
        rootok=1 ;;
    block:UUID=*|UUID=*)
        root="${root#block:}"
        root="/dev/disk/by-uuid/${root#UUID=}"
        rootok=1 ;;
    block:PARTUUID=*|PARTUUID=*)
        root="${root#block:}"
        root="/dev/disk/by-partuuid/${root#PARTUUID=}"
        rootok=1 ;;
    block:PARTLABEL=*|PARTLABEL=*)
        root="${root#block:}"
        root="/dev/disk/by-partlabel/${root#PARTLABEL=}"
        rootok=1 ;;
    /dev/nfs) # ignore legacy /dev/nfs
        ;;
    /dev/*)
        root="${root}"
        rootok=1 ;;
esac

if [ "$rootok" != 1 ]; then
	info "GROWROOT: Can't determine the root device"
	exit 1
fi

ROOTDELAY=$(getarg rd.timeout)

# wait for dev to be populated, otherwise the real rootdev might not be properly determined
udevadm settle --timeout ${ROOTDELAY:-30}

rootdev=$(readlink -f ${root})

case "${rootdev}" in
    *[0-9]) : ;;
    # the root is a disk, not a partition (does not end in a digit)
    # no need to do anything in this case, kernel already knows the full size.
    *) exit 0;;
esac

# remove all consective numbers from the end of rootdev to get 'rootdisk'
rootdisk=${rootdev}
while [ "${rootdisk%[0-9]}" != "${rootdisk}" ]; do
    rootdisk=${rootdisk%[0-9]};
done
partnum=${rootdev#${rootdisk}}

# account for devnameNpP devices (like mmcblk0p1).
if [ "${rootdisk%[0-9]p}" != "${rootdisk}" ] &&
    [ -b "${rootdisk%p}" ]; then
    rootdisk="${rootdisk%p}"
fi

# if the basename of the root device (ie 'xvda1' or 'sda1') exists
# in /sys/block/ then it is a block device, not a partition
# (xen xvda1 is an example of such a funny named block device)
[ -e "/sys/block/${rootdev##*/}" ] && exit 0

info "GROWROOT: trying to grow partition ${rootdisk}"

# if growpart fails, exit.
# we capture stderr because on success of dry-run, it writes
# to stderr what it would do.
out=$(growpart --dry-run "${rootdisk}" "${partnum}" 2>&1) ||
    { info "${out}"; exit 1; }

# if growpart would change something, --dry-run will write something like
#  CHANGE: partition=1 start=2048 old: size=1024000 end=1026ma048 new: size=2089192,end=2091240
# anything else, exit
case "${out}" in
    CHANGE:*) :;;
    *) exit 0;;
esac

# There was something to do, resize

# Wait for any of the initial udev events to finish
# This is to avoid any other processes using the block device that the
# root partition is on, which would cause the sfdisk 'BLKRRPART' to fail.
udevadm settle --timeout ${ROOTDELAY:-30} ||
    { warn "GROWROOT: udevadm settle prior to growpart failed"; exit 1; }

if out=$(growpart "${rootdisk}" "${partnum}" 2>&1); then
    case "$out" in
        CHANGED:*) info "GROWROOT: $out";;
        NOCHANGE:*)
            warn "GROWROOT: expected to grow partition, but did not";;
        *) warn "GROWROOT: unexpected output: ${out}"
    esac
else
    warn "GROWROOT: resize failed: $out"
fi

# Wait for the partition re-read events to complete 
# so that the root partition is available when we try and mount it.
udevadm settle --timeout ${ROOTDELAY:-30}
