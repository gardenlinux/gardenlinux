#!/usr/bin/env bash
set -Eeuo pipefail

thisDir="$(dirname "$(readlink -f "$BASH_SOURCE")")"
source "$thisDir/.constants.sh" \
	'<target-dir>' \
	'rootfs'

eval "$dgetopt"
while true; do
	flag="$1"; shift
	dgetopt-case "$flag"
	case "$flag" in
		--) break ;;
		*) eusage "unknown flag '$flag'" ;;
	esac
done

targetDir="${1:-}"; shift || eusage 'missing target-dir'
[ -n "$targetDir" ]

"$thisDir/garden-chroot" "$targetDir" bash -c '
	dpkg-query --show --showformat "\${Version}\n" apt
'
