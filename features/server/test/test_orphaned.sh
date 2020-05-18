#!/usr/bin/env bash

set -e 

echo "testing for unneeded/orphaned packages"
rootfsDir=$1
absPath=$(readlink -f $(dirname "${BASH_SOURCE[0]}"))

if [[ -z ${absPath} || ! -d ${absPath} ]]; then
	echo "FATAL - can't determine working directory"
	exit 1
fi

source ${absPath}/helpers

if ! check_rootdir "${rootfsDir}"; then
	exit 1
fi

if [[ "$UID" -ne 0 ]]; then
	echo "FATAL - must be run as root"
	exit 1
else
	run_in_chroot ${rootfsDir} chroot_orphaned.sh
fi

