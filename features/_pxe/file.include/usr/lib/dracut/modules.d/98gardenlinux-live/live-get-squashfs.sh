#!/usr/bin/env bash

type getarg >/dev/null 2>&1 || . /lib/dracut-lib.sh
type info >/dev/null 2>&1 || . /lib/dracut-lib.sh
type warn >/dev/null 2>&1 || . /lib/dracut-lib.sh


# download squashfs

url=$(getarg gl.url=)
if [ -z "${url#gl.url=}" ]; then
	info "gl.url not defined, skipping"
	exit 0
fi

if ! (cd /tmp; curl --globoff --location --retry 3 --fail --show-error "${url}" --output rootfs.squash); then
       warn "can't fetch the squashfs from ${url#gl.url=}"
       exit 1
fi       

# check if the file is a squashfs
if ! file -m /usr/lib/file/magic.mgc -b /tmp/rootfs.squash | grep -q "Squashfs filesystem" ; then
	warn "the provided image via gl.url is not a valid squashfs image"
	exit 1
fi

# TODO add check for contents

# move image to proper place
mv /tmp/rootfs.squash /run/rootfs

exit 0
