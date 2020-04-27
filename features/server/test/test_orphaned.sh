#!/usr/bin/env bash

set -e 

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

echo "testing for unneeded/orphaned packages"
run_in_chroot ${rootfsDir} chroot_orphaned.sh
