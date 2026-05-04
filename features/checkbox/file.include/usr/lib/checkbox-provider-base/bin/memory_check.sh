#!/usr/bin/env bash

DETAILS_FILE=$(mktemp /tmp/memory_check_XXXX.txt)
memory_ok="yes"

echo "===== Memory info (/proc/meminfo) =====" >> "$DETAILS_FILE"
head -5 /proc/meminfo >> "$DETAILS_FILE"

total_kb=$(grep "^MemTotal:" /proc/meminfo 2>/dev/null | awk '{print $2}')
total_gb=$(awk "BEGIN{printf \"%.1f\", ${total_kb:-0} / 1048576}")
echo "" >> "$DETAILS_FILE"
echo "Total RAM: ${total_kb} kB (${total_gb} GiB)" >> "$DETAILS_FILE"

echo "" >> "$DETAILS_FILE"
echo "===== Memory modules and ECC (dmidecode) =====" >> "$DETAILS_FILE"
if command -v dmidecode >/dev/null 2>&1; then
    dmidecode -t memory 2>/dev/null | grep -iE "(ECC|Error Correction|Size|Speed|Type:|Manufacturer|Part Number)" >> "$DETAILS_FILE" || true
else
    echo "dmidecode not available" >> "$DETAILS_FILE"
fi

echo "" >> "$DETAILS_FILE"
echo "===== Quick memory test (dd write/read 64M to tmpfs) =====" >> "$DETAILS_FILE"
MEM_TMP=$(mktemp /tmp/memtest_XXXX.bin)
if dd if=/dev/urandom of="$MEM_TMP" bs=1M count=64 2>/dev/null && \
   dd if="$MEM_TMP" of=/dev/null bs=1M 2>/dev/null; then
    echo "Memory read/write test: PASSED" >> "$DETAILS_FILE"
else
    echo "Memory read/write test: FAILED" >> "$DETAILS_FILE"
    memory_ok="no"
fi
rm -f "$MEM_TMP"

if [ -z "$total_kb" ] || [ "$total_kb" -eq 0 ]; then
    memory_ok="no"
fi

echo "ATTACHMENT: $DETAILS_FILE"

if [ "$memory_ok" = "yes" ]; then
    echo "RESULT: PASS — Memory detected (${total_kb} kB / ${total_gb} GiB) and basic test passed"
    exit 0
else
    echo "RESULT: FAIL — Memory check failed (total=${total_kb} kB)"
    exit 1
fi
