#!/usr/bin/env bash
set -Eeuo pipefail

thisDir="$(dirname "$(readlink -f "$BASH_SOURCE")")"
source "$thisDir/.constants.sh" \
	'<timestamp> [archive]' \
	'2017-05-08T00:00:00Z debian-security'

eval "$dgetopt"
while true; do
	flag="$1"; shift
	dgetopt-case "$flag"
	case "$flag" in
		--) break ;;
		*) eusage "unknown flag '$flag'" ;;
	esac
done

timestamp="${1:-}"; shift || eusage 'missing timestamp'
archive="${1:-debian}"

t="$(date --date "$timestamp" '+%Y%m%dT%H%M%SZ')"

# use caching proxy to avoid throttling, if available
if wget -t1 -qO/dev/null http://localhost/archive/$archive/; then
	echo "http://localhost/archive/$archive/$t"
elif wget -t1 -qO/dev/null http://172.17.0.1/archive/$archive/; then
	echo "http://172.17.0.1/archive/$archive/$t"
elif wget -t1 -qO/dev/null http://192.168.10.1/gardenlinux/archive/$archive/; then
	echo "http://192.168.10.1/gardenlinux/archive/$archive/$t"
elif wget -t1 -qO/dev/null https://snapshot-cache.ci.gardener.cloud/archive/$archive/; then
	echo "https://snapshot-cache.ci.gardener.cloud/archive/$archive/$t"
else
	echo "https://snapshot.debian.org/archive/$archive/$t"
fi
