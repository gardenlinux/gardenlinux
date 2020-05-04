#!/usr/bin/env bash

set -e

thisDir=$(readlink -f $(dirname "${BASH_SOURCE[0]}"))

if [[ ! -f "${thisDir}/tigerrc" ]]; then
	echo "FATAIL: missing config files"
	exit 1
fi

apt-get install -y --no-install-recommends -qq tiger 2> /dev/null

# fake it when running inside a chroot environment
if [[ "done" == $(tail -1 /usr/lib/tiger/systems/Linux/default/gen_mounts) ]]; then
	echo 'echo "/ ext4 /dev/fake1"' >> /usr/lib/tiger/systems/Linux/default/gen_mounts 
fi

tiger -c "${thisDir}/tigerrc" -l ${thisDir} -q > /dev/null

if err=$(grep -hw FAIL "${thisDir}"/security.report.*); then
	echo "tiger detected the following errors"
	echo "$err"
	rm -f "${thisDir}"/security.report.*
	exit 1
else
	rm -f "${thisDir}"/security.report.*
	exit 1
fi
