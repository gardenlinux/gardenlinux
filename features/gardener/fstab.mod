#!/usr/bin/env bash
set -Eeuo pipefail

currentfstab="$(cat)"

if [ -n "$currentfstab" ]; then
	# delete any predefinition of a usr partition
	sed '/^[^[:space:]]\+[[:space:]]\+\/usr[[:space:]]\+/d' <<< "$currentfstab"

	# make usr a readonly setup
	printf "LABEL=USR          /usr         ext4      ro\n"
fi
