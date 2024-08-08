#!/usr/bin/env bash

type getarg >/dev/null 2>&1 || . /lib/dracut-lib.sh
type info >/dev/null 2>&1 || . /lib/dracut-lib.sh
type warn >/dev/null 2>&1 || . /lib/dracut-lib.sh


# download extra ignition

url=$(getarg gl.ignext=)
if [ -z "${url#gl.ignext=}" ]; then
	info "gl.ignext not defined, skipping"
	exit 0
fi

uuid=$(cat /sys/devices/virtual/dmi/id/product_uuid)
ignUrl="${url}/${uuid}"

mkdir -p /usr/lib/ignition/base.platform.d/metal
if ! curl --globoff --location --retry 3 --fail --show-error "${ignUrl}" --output "/usr/lib/ignition/base.platform.d/metal/10-ignition-service.ign"; then
       warn "can't fetch the extra ignition config ${url#gl.url=}"
       exit 1
fi       
exit 0
