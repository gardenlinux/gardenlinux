#!/usr/bin/env bash
set -Eeuo pipefail

while read -r line; do
	read -r source target fs options args <<< "$line"
	if [ "$target" = "/efi" ]; then
		args="$args,size=128MiB"
		echo "$source $target $fs $options $args"
	else
		echo "$line"
	fi
done

cat << EOF
REPART=00    /home    ext4    rw    tpm2
REPART=01    /tmp     ext4    rw    tpm2   
EOF
