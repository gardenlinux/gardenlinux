#!/usr/bin/env bash

rootfsDir=$1

absPath=$(readlink -f $(dirname "${BASH_SOURCE[0]}"))
if [ -z ${absPath} ]; then
	echo "FATAL - can't determine working directory"
	exit 1
fi

source ${absPath}/helpers

if ! check_rootdir "${rootfsDir}"; then
	exit 1
fi

run_in_chroot ${rootfsDir} chroot_world_writable_paths.sh
