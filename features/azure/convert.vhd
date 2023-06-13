#!/usr/bin/env bash

set -eufo pipefail

input="$1"
output="$2"

if [[ "$(wc -c "$input" | cut -d " " -f 1)" -gt 4294967296 ]]; then
	echo "image too large"
	exit 1
fi

tmp="$(mktemp)"
cp --sparse=always "$input" "$tmp"
truncate -s 4GiB "$tmp"

# fix GPT and image size mismatch
echo | sfdisk "$tmp"

qemu-img convert -f raw -O vpc -o subformat=fixed,force_size "$tmp" "$output"

rm "$tmp"
