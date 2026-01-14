#!/usr/bin/env bash

RED="\033[1;31m"
GREEN="\033[0;32m"
RESET="\033[0m"
DETAILS_FILE=$(mktemp /tmp/virtualization_disabled_XXXX.log)
virt_enabled=false

append_section_plain() {
  {
    echo "===== /proc/cpuinfo (vmx or svm) ====="
    if [ -z $(grep -E 'vmx|svm' /proc/cpuinfo) ];then
	echo "No presence of virtualization"
    fi
    echo
  } >> "$DETAILS_FILE"
}

append_section_plain
echo "ATTACHMENT: $DETAILS_FILE"

if grep -E -q 'vmx|svm' /proc/cpuinfo; then
    if dmesg | grep -qi "disabled by bios"; then
        echo -e "Virtualization detected but disabled in BIOS"
        exit 1
    else
        virt_enabled=true
    fi
else
    echo -e "No virtualization support found in CPU"
    exit 1
fi


if [ "$virt_enabled" = true ]; then
    echo -e "Virtualization is enabled"
    exit 0
fi
