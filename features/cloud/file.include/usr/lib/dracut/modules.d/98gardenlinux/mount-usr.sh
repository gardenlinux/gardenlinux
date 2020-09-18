#!/bin/sh
# based on usrmount module from dracut with slight changes to make it suitable for a .mount
type info >/dev/null 2>&1 || . /lib/dracut-lib.sh
type fsck_single >/dev/null 2>&1 || . /lib/fs-lib.sh

fsck_usr()
{
    local _dev=$1
    local _fs=$2
    local _fsopts=$3
    local _fsckoptions

    if [ -f "$NEWROOT"/fsckoptions ]; then
        _fsckoptions=$(cat "$NEWROOT"/fsckoptions)
    fi

    if [ -f "$NEWROOT"/forcefsck ] || getargbool 0 forcefsck ; then
        _fsckoptions="-f $_fsckoptions"
    elif [ -f "$NEWROOT"/.autofsck ]; then
        [ -f "$NEWROOT"/etc/sysconfig/autofsck ] && . "$NEWROOT"/etc/sysconfig/autofsck
        if [ "$AUTOFSCK_DEF_CHECK" = "yes" ]; then
            AUTOFSCK_OPT="$AUTOFSCK_OPT -f"
        fi
        if [ -n "$AUTOFSCK_SINGLEUSER" ]; then
            warn "*** Warning -- the system did not shut down cleanly. "
            warn "*** Dropping you to a shell; the system will continue"
            warn "*** when you leave the shell."
            emergency_shell
        fi
        _fsckoptions="$AUTOFSCK_OPT $_fsckoptions"
    fi

    fsck_single "$_dev" "$_fs" "$_fsopts" "$_fsckoptions"
}

mount_usr()
{
    local _dev _mp _fs _opts _rest _usr_found _ret _freq _passno

    # if present in fstab, then it's already handled
    if [ -e /sysroot/etc/fstab ]; then
        result=$(awk '(! /^\s*#/) && ($2 == "/usr") {print "defined in fstab"}' /sysroot/etc/fstab)
        if [ -n "$result" ]; then
            return 0
        fi
    fi

    if ismounted "$NEWROOT/usr"; then
	    return 0
    fi

    # TODO - switch to systemd unit in initramfs
    # try to find via .mount file
    if [ -e "$NEWROOT"/etc/systemd/system/usr.mount ]; then
	    _mount="$NEWROOT"/etc/systemd/system/usr.mount
	    _dev=$(grep What= "$_mount")
	    _dev=${_dev#*=}
	    _mp=$(grep Where= "$_mount")
	    _mp=${_mp#*=}
	    _fs=$(grep Type= "$_mount")
	    _fs=${_fs#*=}
	    _opts=$(grep Options= "$_mount")
	    _opts=${_opts#*=}
            echo "${_dev} ${NEWROOT}${_mp} ${_fs} rw 0 0" >> /etc/fstab
	    _usr_found=1
    fi

    if [ "$_usr_found" != "" ]; then
        # we have to mount /usr
        _fsck_ret=0
        if ! getargbool 0 rd.skipfsck; then
            if [ "0" != "${_passno:-0}" ]; then
                fsck_usr "$_dev" "$_fs" "$_opts"
                _fsck_ret=$?
                [ $_fsck_ret -ne 255 ] && echo $_fsck_ret >/run/initramfs/usr-fsck
            fi
        fi

        info "Mounting /usr with -o $_opts"
        mount "$NEWROOT/usr" 2>&1 | vinfo

        if ! ismounted "$NEWROOT/usr"; then
            warn "Mounting /usr to $NEWROOT/usr failed"
            warn "*** Dropping you to a shell; the system will continue"
            warn "*** when you leave the shell."
            emergency_shell
        fi
    fi
}

mount_usr
