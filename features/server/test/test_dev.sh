#!/usr/bin/env bash

# checking if the files in /dev corespond to a minimum set of requirements - special character devices, symlinks, file ownership, type, etc.
# stdout,0,0,symbolic link,0,0,/proc/self/fd/1
# tty,0,0,character special file,5,0,tty
# file, owner user id, group owner id, file type, major device type, minor device type, file name or symlink target if symlink 

rc=0

rootfsDir=$1
targetBaseDir=$2

echo "testing /dev contents"
nr_files=$(wc -l dev_files | cut -d " " -f 1)
nr_dev=$(nr=($rootfsDir/dev/*); echo ${#nr[@]})

# check if the number of files in /dev is the same as in dev_files
if [[ "$nr_files" -ne "$nr_dev" ]]; then
	echo "number of dev files do not match!"
	echo "expects: $(awk -F, '{ printf "%s ",$1}' dev_files)"
	echo "got:     $(echo rootfs/dev/*)"  
	rc=1
	exit 1
fi

# go over the predefined settings and verify if they match
while read -r line; do
	dev_name=${line%%,*}
	if ! stat ${rootfsDir}/dev/${dev_name} > /dev/null; then
		echo "${dev_name} doesn't exist!"
		rc=1
	fi
	to_test=$(echo ${dev_name}","$(stat -c %u,%g,%F,%t,%T, ${rootfsDir}/dev/${dev_name})$(readlink ${rootfsDir}/dev/${dev_name} || echo ${dev_name}))
	if [[ "$to_test" != "$line" ]]; then
		rc=1
		echo "expects: ${line}"
		echo "got:     ${to_test}"
		echo
	fi
done < dev_files

exit $rc
