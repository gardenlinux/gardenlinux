#!/usr/bin/env bash

set -e

rootfsDir=$1
rc=0
# machine-id needs to be 0 in size
# /var/lib/dbus/machine-id must not exist
# more information : https://wiki.debian.org/MachineId

absPath=$(readlink -f $(dirname "${BASH_SOURCE[0]}"))
if [[ -z ${absPath} ]]; then
	echo "FATAL - can't determine working directory"
	exit 1
fi

source ${absPath}/helpers

if ! check_rootdir "${rootfsDir}"; then
	exit 1
fi

echo "checking the machine-id"

if [[ -f ${rootfsDir}/etc/machine-id && ! -s ${rootfsDir}/etc/machine-id ]]; then
	echo "OK - machine-id is as expected"
	rc=0
else
	echo "FAIL - machine-id doesn't exist or is not empty!"
	rc=1
fi

if [[ -f ${rootfsDir}/var/lib/dbus/machine-id ]]; then
	echo "FAIL - /var/lib/dbus/machine-id exists!"
	rc=1
fi

exit $rc
