#!/usr/bin/env bash

type getarg >/dev/null 2>&1 || . /lib/dracut-lib.sh
type info >/dev/null 2>&1 || . /lib/dracut-lib.sh
type warn >/dev/null 2>&1 || . /lib/dracut-lib.sh


shaFile="/root.squashfs.sha256sum"
squashFile="/tmp/root.squashfs"

# download squashfs

url=$(getarg gl.url=)
if [ -z "${url#gl.url=}" ]; then
	info "gl.url not defined, skipping"
	exit 0
fi

if ! curl --globoff --location --retry 10 --retry-delay 3 --retry-max-time 30 --fail --show-error "${url}" --output "${squashFile}"; then
       warn "can't fetch the squashfs from ${url#gl.url=}"
       exit 1
fi       

# verify sha256
if [ ! -f "${shaFile}" ]; then
	warn "no sha256sum file exists - exiting"
	exit 1
fi

if ! echo "$(grep . ${shaFile}) ${squashFile}" | sha256sum --status --check; then
	warn "the hash verification of the squashfs has failed - exiting"
	exit 1
fi

# move image to proper place
mv "${squashFile}" /run/root.squashfs

exit 0
