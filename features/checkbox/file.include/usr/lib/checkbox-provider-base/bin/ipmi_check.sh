#!/usr/bin/env bash

DETAILS_FILE=$(mktemp /tmp/ipmi_check_XXXX.txt)
ipmi_ok="no"

# Skip IPMI check on virtual machines — no BMC present
if systemd-detect-virt --quiet 2>/dev/null; then
    virt=$(systemd-detect-virt 2>/dev/null || echo "unknown")
    echo "SKIP: Running in virtualized environment ($virt) — IPMI/BMC not applicable" | tee -a "$DETAILS_FILE"
    echo "ATTACHMENT: $DETAILS_FILE"
    exit 0
fi

echo "===== Loading IPMI kernel modules =====" >> "$DETAILS_FILE"
for mod in ipmi_si ipmi_devintf ipmi_msghandler; do
    if modprobe "$mod" 2>/dev/null; then
        echo "Loaded: $mod" >> "$DETAILS_FILE"
    else
        echo "Could not load: $mod (may already be built-in)" >> "$DETAILS_FILE"
    fi
done

echo "" >> "$DETAILS_FILE"
echo "===== IPMI device nodes =====" >> "$DETAILS_FILE"
if ls /dev/ipmi* /dev/ipmi 2>/dev/null | head -5 >> "$DETAILS_FILE"; then
    ipmi_ok="yes"
    echo "IPMI device node found" >> "$DETAILS_FILE"
else
    echo "No /dev/ipmi* device nodes found" >> "$DETAILS_FILE"
fi

echo "" >> "$DETAILS_FILE"
echo "===== BMC chassis status (ipmitool) =====" >> "$DETAILS_FILE"
if command -v ipmitool >/dev/null 2>&1; then
    if timeout 15 ipmitool chassis status >> "$DETAILS_FILE" 2>&1; then
        ipmi_ok="yes"
        echo "ipmitool chassis status: OK" >> "$DETAILS_FILE"
    else
        echo "ipmitool chassis status: FAILED (BMC may not be present or accessible)" >> "$DETAILS_FILE"
    fi
else
    echo "ipmitool not available" >> "$DETAILS_FILE"
fi

echo "" >> "$DETAILS_FILE"
echo "===== BMC info =====" >> "$DETAILS_FILE"
if command -v ipmitool >/dev/null 2>&1; then
    timeout 15 ipmitool bmc info >> "$DETAILS_FILE" 2>&1 || true
fi

echo "" >> "$DETAILS_FILE"
echo "===== Sensor list (first 20) =====" >> "$DETAILS_FILE"
if command -v ipmitool >/dev/null 2>&1; then
    timeout 15 ipmitool sensor list 2>/dev/null | head -20 >> "$DETAILS_FILE" || true
fi

echo "ATTACHMENT: $DETAILS_FILE"

if [ "$ipmi_ok" = "yes" ]; then
    echo "RESULT: PASS — IPMI/BMC interface detected and responsive"
    exit 0
else
    echo "RESULT: FAIL — No IPMI/BMC interface detected"
    exit 1
fi
