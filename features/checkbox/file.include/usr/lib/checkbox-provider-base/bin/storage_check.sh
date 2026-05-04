#!/usr/bin/env bash

DETAILS_FILE=$(mktemp /tmp/storage_check_XXXX.txt)
storage_ok="yes"

echo "===== Block devices (lsblk) =====" >> "$DETAILS_FILE"
if command -v lsblk >/dev/null 2>&1; then
    lsblk -o NAME,SIZE,TYPE,TRAN,MODEL >> "$DETAILS_FILE" 2>&1
    disk_count=$(lsblk -dn -o TYPE 2>/dev/null | grep -c "^disk" || true)
    echo "Detected $disk_count disk(s)" >> "$DETAILS_FILE"
    if [ "$disk_count" -eq 0 ]; then
        echo "WARNING: No physical disks detected via lsblk" >> "$DETAILS_FILE"
        storage_ok="no"
    fi
else
    echo "lsblk not available" >> "$DETAILS_FILE"
    storage_ok="no"
fi

echo "" >> "$DETAILS_FILE"
echo "===== SMART health (smartctl) =====" >> "$DETAILS_FILE"
if command -v smartctl >/dev/null 2>&1; then
    for dev in $(lsblk -dn -o NAME 2>/dev/null | sed 's|^|/dev/|'); do
        echo "--- $dev ---" >> "$DETAILS_FILE"
        smartctl -H "$dev" >> "$DETAILS_FILE" 2>&1 || true
    done
else
    echo "smartctl not available (smartmontools not installed)" >> "$DETAILS_FILE"
fi

echo "" >> "$DETAILS_FILE"
echo "===== Disk read throughput (hdparm) =====" >> "$DETAILS_FILE"
if command -v hdparm >/dev/null 2>&1 && [ "$storage_ok" = "yes" ]; then
    first_disk=$(lsblk -dn -o NAME,TYPE 2>/dev/null | awk '$2=="disk"{print $1; exit}' | sed 's|^|/dev/|')
    tran=$(lsblk -dn -o NAME,TRAN 2>/dev/null | awk '$1==substr("'"$first_disk"'",6){print $2; exit}')
    if [ -n "$first_disk" ] && [ -b "$first_disk" ]; then
        echo "Testing $first_disk (transport: ${tran:-unknown})" >> "$DETAILS_FILE"
        # Run 3 iterations, collect results
        total_mbps=0
        for i in 1 2 3; do
            result=$(hdparm -t --direct "$first_disk" 2>/dev/null | grep "Timing" | grep -oE '[0-9]+\.[0-9]+ MB/sec' | grep -oE '[0-9]+\.[0-9]+' || echo "0")
            echo "  Run $i: ${result} MB/s" >> "$DETAILS_FILE"
            total_mbps=$(awk "BEGIN{print $total_mbps + $result}")
        done
        avg_mbps=$(awk "BEGIN{printf \"%.1f\", $total_mbps / 3}")
        echo "  Average: ${avg_mbps} MB/s" >> "$DETAILS_FILE"

        # Thresholds by transport type (matching Checkbox disk_read_performance_test.sh)
        case "$tran" in
            nvme)    threshold=200 ;;
            sas)     threshold=100 ;;
            sata)    threshold=80  ;;
            usb)     threshold=25  ;;
            *)       threshold=80  ;;
        esac
        echo "  Minimum threshold for ${tran:-unknown}: ${threshold} MB/s" >> "$DETAILS_FILE"
        if awk "BEGIN{exit ($avg_mbps >= $threshold) ? 0 : 1}"; then
            echo "  Throughput check: PASS" >> "$DETAILS_FILE"
        else
            echo "  Throughput check: FAIL (${avg_mbps} MB/s < ${threshold} MB/s)" >> "$DETAILS_FILE"
            storage_ok="no"
        fi
    fi
else
    echo "hdparm not available or no disk found" >> "$DETAILS_FILE"
fi

echo "ATTACHMENT: $DETAILS_FILE"

if [ "$storage_ok" = "yes" ]; then
    echo "RESULT: PASS — Storage devices detected and accessible"
    exit 0
else
    echo "RESULT: FAIL — Storage check failed (no disk detected or throughput below threshold)"
    exit 1
fi
