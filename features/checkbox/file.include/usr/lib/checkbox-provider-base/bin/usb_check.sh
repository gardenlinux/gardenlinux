#!/usr/bin/env bash

DETAILS_FILE=$(mktemp /tmp/usb_check_XXXX.txt)
usb_ok="no"

echo "===== USB controllers (lspci) =====" >> "$DETAILS_FILE"
if command -v lspci >/dev/null 2>&1; then
    usb_controllers=$(lspci 2>/dev/null | grep -i "usb")
    if [ -n "$usb_controllers" ]; then
        echo "$usb_controllers" >> "$DETAILS_FILE"
        usb_ok="yes"
    else
        echo "No USB controllers found via lspci" >> "$DETAILS_FILE"
    fi
else
    echo "lspci not available (pciutils not installed)" >> "$DETAILS_FILE"
fi

echo "" >> "$DETAILS_FILE"
echo "===== USB device enumeration (lsusb) =====" >> "$DETAILS_FILE"
if command -v lsusb >/dev/null 2>&1; then
    lsusb >> "$DETAILS_FILE" 2>&1 || true
    usb_ok="yes"
else
    echo "lsusb not available (usbutils not installed)" >> "$DETAILS_FILE"
fi

echo "" >> "$DETAILS_FILE"
echo "===== USB sysfs entries =====" >> "$DETAILS_FILE"
if ls /sys/bus/usb/devices/ >/dev/null 2>&1; then
    ls /sys/bus/usb/devices/ >> "$DETAILS_FILE"
    usb_ok="yes"
else
    echo "No /sys/bus/usb/devices/ entries found" >> "$DETAILS_FILE"
fi

echo "ATTACHMENT: $DETAILS_FILE"

if [ "$usb_ok" = "yes" ]; then
    echo "RESULT: PASS — USB controller/bus detected"
    exit 0
else
    echo "RESULT: FAIL — No USB controller detected"
    exit 1
fi
