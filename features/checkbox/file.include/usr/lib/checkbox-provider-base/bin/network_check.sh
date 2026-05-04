#!/usr/bin/env bash

DETAILS_FILE=$(mktemp /tmp/network_check_XXXX.txt)
network_ok="no"

echo "===== Network interfaces (ip link) =====" >> "$DETAILS_FILE"
ip link show >> "$DETAILS_FILE" 2>&1

echo "" >> "$DETAILS_FILE"
echo "===== Interface link state (ethtool) =====" >> "$DETAILS_FILE"
if command -v ethtool >/dev/null 2>&1; then
    for iface in $(ip link show 2>/dev/null | awk -F': ' '/^[0-9]+:/{print $2}' | grep -v lo | cut -d@ -f1); do
        echo "--- $iface ---" >> "$DETAILS_FILE"
        ethtool "$iface" 2>&1 | grep -E "Speed|Duplex|Link detected" >> "$DETAILS_FILE" || true
        if ethtool "$iface" 2>/dev/null | grep -q "Link detected: yes"; then
            network_ok="yes"
        fi
    done
else
    echo "ethtool not available — using ip link state fallback" >> "$DETAILS_FILE"
    if ip link show 2>/dev/null | grep -q "state UP"; then
        network_ok="yes"
    fi
fi

echo "" >> "$DETAILS_FILE"
echo "===== IP addresses (ip addr) =====" >> "$DETAILS_FILE"
ip addr show 2>/dev/null | grep -E "^[0-9]+:|inet " >> "$DETAILS_FILE" || true

echo "" >> "$DETAILS_FILE"
echo "===== Loopback ping =====" >> "$DETAILS_FILE"
if ping -c 2 -W 2 127.0.0.1 >> "$DETAILS_FILE" 2>&1; then
    echo "Loopback ping: OK" >> "$DETAILS_FILE"
else
    echo "Loopback ping: FAILED" >> "$DETAILS_FILE"
fi

echo "ATTACHMENT: $DETAILS_FILE"

if [ "$network_ok" = "yes" ]; then
    echo "RESULT: PASS — At least one network interface is up with link"
    exit 0
else
    echo "RESULT: FAIL — No network interface with active link detected"
    exit 1
fi
