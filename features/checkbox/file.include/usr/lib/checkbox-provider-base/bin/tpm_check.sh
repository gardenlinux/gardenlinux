#!/usr/bin/env bash

DETAILS_FILE=$(mktemp /tmp/tpm_check_XXXX.txt)
tpm_present="no"

if [ -e /dev/tpm0 ] || [ -e /dev/tpmrm0 ]; then
    tpm_present="yes"
    echo "TPM device node found: $(ls /dev/tpm* 2>/dev/null)" >> "$DETAILS_FILE"
else
    echo "No TPM device nodes found in /dev" >> "$DETAILS_FILE"
fi

if [ -d /sys/class/tpm ]; then
    echo "TPM sysfs entries:" >> "$DETAILS_FILE"
    if ls /sys/class/tpm/* >/dev/null 2>&1; then
        ls -1 /sys/class/tpm >> "$DETAILS_FILE"
    else
        echo "(no entries)" >> "$DETAILS_FILE"
    fi
else
    echo "No /sys/class/tpm directory" >> "$DETAILS_FILE"
fi

if command -v tpm_version >/dev/null 2>&1; then
    echo "TPM version (tpm_version):" >> "$DETAILS_FILE"
    tpm_version >> "$DETAILS_FILE" 2>&1
elif command -v tpm2_getcap >/dev/null 2>&1; then
    echo "TPM 2.0 capabilities:" >> "$DETAILS_FILE"
    tpm2_getcap properties-fixed >> "$DETAILS_FILE" 2>&1
fi

echo "ATTACHMENT: $DETAILS_FILE"

if [ "$tpm_present" = "yes" ]; then
    echo -e "RESULT: PASS — TPM is enabled and accessible"
    exit 0
else
    echo -e "RESULT: FAIL — No TPM detected. It must be enabled in BIOS/UEFI"
    exit 1
fi
