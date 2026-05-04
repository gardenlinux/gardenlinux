#!/usr/bin/env bash

DETAILS_FILE=$(mktemp /tmp/bios_info_check_XXXX.txt)
bios_ok="yes"

echo "===== BIOS/Firmware info (dmidecode type 0) =====" >> "$DETAILS_FILE"
if command -v dmidecode >/dev/null 2>&1; then
    dmidecode -t bios >> "$DETAILS_FILE" 2>&1
else
    echo "dmidecode not available" >> "$DETAILS_FILE"
    bios_ok="no"
fi

echo "" >> "$DETAILS_FILE"
echo "===== System info (dmidecode type 1) =====" >> "$DETAILS_FILE"
if command -v dmidecode >/dev/null 2>&1; then
    dmidecode -t system >> "$DETAILS_FILE" 2>&1
fi

echo "" >> "$DETAILS_FILE"
echo "===== Baseboard info (dmidecode type 2) =====" >> "$DETAILS_FILE"
if command -v dmidecode >/dev/null 2>&1; then
    dmidecode -t baseboard >> "$DETAILS_FILE" 2>&1
fi

echo "" >> "$DETAILS_FILE"
echo "===== Firmware info via sysfs =====" >> "$DETAILS_FILE"
if [ -f /sys/class/dmi/id/bios_version ]; then
    echo "BIOS vendor:  $(cat /sys/class/dmi/id/bios_vendor 2>/dev/null)" >> "$DETAILS_FILE"
    echo "BIOS version: $(cat /sys/class/dmi/id/bios_version 2>/dev/null)" >> "$DETAILS_FILE"
    echo "BIOS date:    $(cat /sys/class/dmi/id/bios_date 2>/dev/null)" >> "$DETAILS_FILE"
    echo "System vendor:  $(cat /sys/class/dmi/id/sys_vendor 2>/dev/null)" >> "$DETAILS_FILE"
    echo "Product name:   $(cat /sys/class/dmi/id/product_name 2>/dev/null)" >> "$DETAILS_FILE"
    echo "Product version:$(cat /sys/class/dmi/id/product_version 2>/dev/null)" >> "$DETAILS_FILE"
    echo "Product serial: $(cat /sys/class/dmi/id/product_serial 2>/dev/null)" >> "$DETAILS_FILE"
    bios_ok="yes"
else
    echo "/sys/class/dmi/id/ not accessible" >> "$DETAILS_FILE"
    if ! command -v dmidecode >/dev/null 2>&1; then
        bios_ok="no"
    fi
fi

echo "" >> "$DETAILS_FILE"
echo "===== UEFI/EFI detection =====" >> "$DETAILS_FILE"
if [ -d /sys/firmware/efi/efivars ]; then
    efivar_count=$(ls /sys/firmware/efi/efivars/ 2>/dev/null | wc -l)
    echo "UEFI firmware detected (efivars present, $efivar_count variables)" >> "$DETAILS_FILE"
else
    echo "No UEFI efivars found (legacy BIOS or no EFI access)" >> "$DETAILS_FILE"
fi

echo "ATTACHMENT: $DETAILS_FILE"

if [ "$bios_ok" = "yes" ]; then
    echo "RESULT: PASS — BIOS/firmware/DMI information retrieved successfully"
    exit 0
else
    echo "RESULT: FAIL — Unable to retrieve BIOS/firmware information (dmidecode missing and sysfs DMI unavailable)"
    exit 1
fi
