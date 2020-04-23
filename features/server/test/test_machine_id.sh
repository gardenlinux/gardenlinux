#!/usr/bin/env bash

rootfsDir=$1
targetBaseDir=$2

rc=0

# machine-id needs to be 0 in size
# /var/lib/dbus/machine-id must not exist
# more information : https://wiki.debian.org/MachineId

echo "checking the machine-id"

if [[ -f ${rootfsDir}/etc/machine-id && -s ${rootfsDir}/etc/machine-id ]]; then
	rc=0
else
	echo "machine-id doesn't exist or is not empty!"
	rc=1
fi

if [[ -f ${rootfsDir}/var/lib/dbus/machine-id ]]; then
	echo "/var/lib/dbus/machine-id exists!"
	rc=1
fi

exit $rc
