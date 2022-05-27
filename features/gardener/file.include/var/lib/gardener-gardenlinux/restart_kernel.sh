#!/bin/bash

RESTART_CONTROL_FILE="/var/run/gardener-gardenlinux/restart-required"

set -Euo pipefail

systemctl status kubelet.service > /dev/null 2>&1
if [ "$?" -eq 0 ]; then
    echo "kubelet is running, not restarting the kernel" >&2
    exit 5
fi

if [ ! -e "$RESTART_CONTROL_FILE" ]; then
    echo "restart of kernel not requested, exiting happily"
    exit 0
fi

set -e

kernel="/boot/vmlinuz-$(uname -r)"
initrd="/boot/initrd.img-$(uname -r)"
cmdline="/etc/kernel/cmdline"

if [ ! -e "$kernel" ]; then
    echo "kernel could not be found at $kernel" >&2
    exit 1
fi

if [ ! -e "$initrd" ]; then
    echo "kernel could not be found at $initrd" >&2
    exit 2
fi

if [ ! -e "$cmdline" ]; then
    echo "kernel command line could not be found at $cmdline" >&2
    exit 3
fi

# we seem to have everything so lets restart the kernel with kexec
rm -f "$RESTART_CONTROL_FILE"

# kexec would be nice because it is fast but at the moment, it seems to be failing on some
# systems due to initrd size or acpi or something else, so commenting it out for now
#kexec -a --initrd="$initrd" --command-line="\"$(cat "$cmdline")\"" "$kernel"

# and rely on good old shutdown (even though that may take ages on systems w/ lots of ram)
shutdown --no-wall -r now
