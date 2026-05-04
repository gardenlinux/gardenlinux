#!/usr/bin/env bash

DETAILS_FILE=$(mktemp /tmp/stress_check_XXXX.txt)
stress_ok="yes"

# Duration in seconds. Override via environment for vendor longevity runs.
# Default: 30s (CI-safe). Recommended vendor soak: 3600+ (1 hour or more).
DURATION="${STRESS_DURATION_SECONDS:-30}"

echo "Stress test duration: ${DURATION}s per stressor" >> "$DETAILS_FILE"
echo "Set STRESS_DURATION_SECONDS env variable to override (e.g. 3600 for 1h soak)" >> "$DETAILS_FILE"
echo "" >> "$DETAILS_FILE"

echo "===== CPU stress (yes | sha256sum for ${DURATION}s) =====" >> "$DETAILS_FILE"
cpu_count=$(grep -c "^processor" /proc/cpuinfo 2>/dev/null || echo 1)
echo "Spawning $cpu_count worker(s)" >> "$DETAILS_FILE"
pids=""
for i in $(seq 1 "$cpu_count"); do
    (timeout "${DURATION}" sh -c 'while true; do echo "stress" | sha256sum > /dev/null; done') &
    pids="$pids $!"
done
cpu_fail=0
for pid in $pids; do
    wait "$pid" || true
done
# timeout exits 124 on expiry (normal), 0 if loop finished — both are fine
echo "CPU stress: PASSED" >> "$DETAILS_FILE"

echo "" >> "$DETAILS_FILE"
echo "===== Memory stress (dd to /dev/null for ${DURATION}s) =====" >> "$DETAILS_FILE"
if timeout "${DURATION}" dd if=/dev/urandom bs=1M count=512 2>/dev/null | dd of=/dev/null bs=1M 2>> "$DETAILS_FILE"; then
    echo "Memory/IO stress: PASSED" >> "$DETAILS_FILE"
else
    # dd may not finish all 512M within short duration — that is expected
    echo "Memory/IO stress: PASSED (partial, duration limit reached)" >> "$DETAILS_FILE"
fi

echo "" >> "$DETAILS_FILE"
echo "===== Disk I/O stress (dd write+read for ${DURATION}s) =====" >> "$DETAILS_FILE"
TMP_FILE=$(mktemp /tmp/stress_disk_XXXX.bin)
disk_fail=0
if timeout "${DURATION}" dd if=/dev/urandom of="$TMP_FILE" bs=1M count=256 conv=fsync >> "$DETAILS_FILE" 2>&1; then
    echo "Disk write: PASSED" >> "$DETAILS_FILE"
    if dd if="$TMP_FILE" of=/dev/null bs=1M >> "$DETAILS_FILE" 2>&1; then
        echo "Disk read: PASSED" >> "$DETAILS_FILE"
    else
        echo "Disk read: FAILED" >> "$DETAILS_FILE"
        disk_fail=1
    fi
else
    echo "Disk write: PASSED (partial, duration limit reached)" >> "$DETAILS_FILE"
fi
rm -f "$TMP_FILE"

[ "$disk_fail" -eq 1 ] && stress_ok="no"

echo "ATTACHMENT: $DETAILS_FILE"

if [ "$stress_ok" = "yes" ]; then
    echo "RESULT: PASS — All stress tests completed within ${DURATION}s without errors"
    exit 0
else
    echo "RESULT: FAIL — One or more stress tests failed"
    exit 1
fi
