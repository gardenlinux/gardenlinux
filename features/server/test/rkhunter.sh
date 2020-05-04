#!/usr/bin/env bash

set -ue

thisDir=$(readlink -f $(dirname "${BASH_SOURCE[0]}"))

# check if config files are available
if [[ ! -f "${thisDir}/rkhunter.conf" ]]; then
	echo "FATAIL: missing config files"
	exit 1
fi

apt-get install -y -qq rkhunter 2> /dev/null 

# run propupd just to avoid extra warnings in the log
rkhunter --configfile "${thisDir}/rkhunter.conf" --propupd -q 
rkhunter --configfile "${thisDir}/rkhunter.conf" --enable system_configs_ssh,group_accounts,filesystem,group_changes,passwd_changes,startup_malware,system_configs_ssh,properties -q --rwo --noappend-log 2>/dev/null

if  err=$(grep -w Warning: /var/log/rkhunter.log); then
	echo "rkhunter detected the following issues"
	echo "$err" | cut -d" " -f 2-
	exit 1
else
	echo "OK - rkhunter didn't detect any issues"
	exit 0
fi
