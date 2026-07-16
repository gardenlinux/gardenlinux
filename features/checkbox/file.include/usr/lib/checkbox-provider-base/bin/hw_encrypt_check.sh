#!/usr/bin/env bash

DETAILS_FILE=$(mktemp /tmp/fips_hw_crypto_XXXX.txt)

cpu_flags=$(grep -m1 -i "flags" /proc/cpuinfo)
arch=$(uname -m)

hw_accel="no"

if [[ "$arch" == "x86_64" || "$arch" == "i686" ]]; then
    if echo "$cpu_flags" | grep -qw "aes"; then
        hw_accel="yes"
        echo "AES-NI hardware acceleration detected." >> "$DETAILS_FILE"
    else
        echo "AES-NI hardware acceleration NOT detected." >> "$DETAILS_FILE"
    fi
elif [[ "$arch" == "aarch64" ]]; then
    if echo "$cpu_flags" | grep -Eqw "aes|sha1|sha2|pmull"; then
        hw_accel="yes"
        echo "ARMv8 Crypto Extensions detected." >> "$DETAILS_FILE"
    else
        echo "ARMv8 Crypto Extensions NOT detected." >> "$DETAILS_FILE"
    fi
else
    echo "Unsupported architecture: $arch" >> "$DETAILS_FILE"
fi

if lsmod | grep -q "aesni_intel"; then
    echo "Kernel module aesni_intel is loaded." >> "$DETAILS_FILE"
fi
if grep -q "aes" /proc/crypto; then
    echo "AES crypto driver available in kernel." >> "$DETAILS_FILE"
fi

echo "ATTACHMENT: $DETAILS_FILE"

if [[ "$hw_accel" == "yes" ]]; then
    echo -e "RESULT: PASS — Hardware encryption is enabled"
    exit 0
else
    echo -e "RESULT: FAIL — Hardware encryption not detected (FIPS requirement)"
    exit 1
fi
