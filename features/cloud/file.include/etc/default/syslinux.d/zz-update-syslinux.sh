#!/usr/bin/env bash

set -xeuoE pipefail

which syslinux &> /dev/null || exit 0

eval set -- "$DEB_MAINT_PARAMS"
if [ -z "$1" ] || [ "$1" != "configure" ]; then
        exit 0
fi

exit 0
