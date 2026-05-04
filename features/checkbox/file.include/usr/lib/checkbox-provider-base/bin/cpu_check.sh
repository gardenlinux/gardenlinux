#!/usr/bin/env bash

DETAILS_FILE=$(mktemp /tmp/cpu_check_XXXX.txt)
cpu_ok="yes"

echo "===== CPU model and cores =====" >> "$DETAILS_FILE"
grep -E "^(processor|model name|cpu MHz|cpu cores|siblings)" /proc/cpuinfo | head -40 >> "$DETAILS_FILE"

core_count=$(grep -c "^processor" /proc/cpuinfo 2>/dev/null || echo 0)
echo "" >> "$DETAILS_FILE"
echo "Logical CPU count: $core_count" >> "$DETAILS_FILE"

phys_cores=$(grep "^cpu cores" /proc/cpuinfo 2>/dev/null | head -1 | awk '{print $4}')
sockets=$(grep -c "^physical id" /proc/cpuinfo 2>/dev/null | awk '{print $1}')
[ -n "$phys_cores" ] && echo "Physical cores per socket: $phys_cores" >> "$DETAILS_FILE"
[ -n "$sockets" ] && echo "Socket count: $sockets" >> "$DETAILS_FILE"

echo "" >> "$DETAILS_FILE"
echo "===== CPU flags (first processor) =====" >> "$DETAILS_FILE"
grep -m1 "^flags" /proc/cpuinfo 2>/dev/null | cut -d: -f2 | tr ' ' '\n' | sort >> "$DETAILS_FILE" || true

echo "" >> "$DETAILS_FILE"
echo "===== lscpu =====" >> "$DETAILS_FILE"
if command -v lscpu >/dev/null 2>&1; then
    lscpu >> "$DETAILS_FILE" 2>&1
fi

if [ "$core_count" -lt 1 ]; then
    cpu_ok="no"
fi

echo "ATTACHMENT: $DETAILS_FILE"

if [ "$cpu_ok" = "yes" ]; then
    echo "RESULT: PASS — CPU detected with $core_count logical core(s)"
    exit 0
else
    echo "RESULT: FAIL — Unable to detect CPU cores from /proc/cpuinfo"
    exit 1
fi
