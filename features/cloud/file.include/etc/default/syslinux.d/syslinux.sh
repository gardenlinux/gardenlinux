#!/usr/bin/env bash

set -uoeE pipefail

bootDir="/boot/efi"
kernelDir="$bootDir/Default"
configDir="/etc/default/syslinux.d"
configFile="/boot/efi/syslinux/syslinux.cfg"

check_version() {
	local v=$1
	if [ ! -d "$kernelDir/$v" ]; then 
		return 1
	fi
	if [ ! -f "$kernelDir/$v/linux" ]; then
		return 1
	fi
	if [ ! -f "$kernelDir/$v/initrd.img-$v" ]; then
		return 1
	fi
	return 0
}
# preliminary checks
if ! mountpoint -q ${bootDir}; then
	echo "${bootDir} is not a mountpoint" 1>&2
	exit 1
fi

if ! which syslinux &> /dev/null; then
	exit 0
fi

# load defaults
source /etc/default/syslinux

# load extra stuff
for i in "${configDir}"/*-*.cfg; do
	[ -e "$i" ] || continue
	source $i
done

versions=()
# kernel / initrd
for kernel in /boot/vmlinuz-*; do 
	if check_version "${kernel#*-}"; then
		versions+=("${kernel#*-}")
	fi
done

if [ "${#versions[@]}" == "0" ]; then
	echo "no valid kernels found" 1>&2
	exit 1
fi

readarray -t vSorted < <(printf '%s\n' "${versions[@]}" | sort -rV)
{
	echo "UI menu.c32"
	echo "PROMPT 0"
	echo
	echo "MENU TITLE Gardenlinux" 
	echo "TIMEOUT $SYSLINUX_TIMEOUT"
	echo "DEFAULT ${vSorted[0]}" 
	echo
	for v in "${vSorted[@]}"; do
		echo "LABEL Linux $v"
		echo " LINUX ../Default/$v/linux"
		echo " APPEND root=${SYSLINUX_DEVICE} ${SYSLINUX_CMDLINE_LINUX}"
		echo " INITRD ../Default/${v}/initrd.img-${v}"
		echo
	done
} > "${bootDir}/syslinux/syslinux.cfg.new" 

mv "${bootDir}/syslinux/syslinux.cfg.new" "${bootDir}/syslinux/syslinux.cfg"
