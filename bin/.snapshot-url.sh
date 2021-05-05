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
archive="${1:-debian}"; shift || true
base="${1:-archive}"

t="$(date --date "$timestamp" '+%Y%m%dT%H%M%SZ')"

# use caching proxy to avoid throttling, if available
if wget -t1 -qO/dev/null http://localhost/$base/$archive/; then
	echo "http://localhost/$base/$archive/$t"
elif wget -t1 -qO/dev/null http://172.17.0.1/$base/$archive/; then
	echo "http://172.17.0.1/$base/$archive/$t"
#elif wget -t1 -qO/dev/null http://repo.gardenlinux.io/gardenlinux/archive/$archive/; then
#	echo "http://repo.gardenlinux.io/gardenlinux/archive/$archive/$t"
# this is for the snapshot cache ($base = archive)
elif wget -t1 -qO/dev/null http://45.86.152.1/gardenlinux/$base/$archive/; then
	echo "http://45.86.152.1/gardenlinux/$base/$archive/$t"
# this is for the gardenlinux-local packages ($base = gardenlinux/)
elif wget -t1 -qO/dev/null http://45.86.152.1/$base/; then
	echo "http://45.86.152.1/$base/"
elif wget -t1 -qO/dev/null https://snapshot-cache.ci.gardener.cloud/$base/$archive/; then
	echo "https://snapshot-cache.ci.gardener.cloud/$base/$archive/$t"
else
	echo "https://snapshot.debian.org/$base/$archive/$t"
fi
