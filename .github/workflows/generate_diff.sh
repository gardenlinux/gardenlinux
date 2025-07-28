#!/usr/bin/env bash

set -euo pipefail

whitelist=()

if [ -z ${2+x} ]; then
    # $2 is unset
    basefile="${1/bare-/}.oci"
else
    # $2 is set
    basefile="$2.tar"
fi

sedcommands=()

for file in "${whitelist[@]}"; do
    sedcommands+=("-e")
    sedcommands+=("\|$file|d")
done

if ! cmp "A/$basefile" "B/$basefile" > /dev/null; then
    # Difference detected

    files=$(diff -qrN ./A/unpacked ./B/unpacked 2> /dev/null \
    | grep differ \
    | perl -0777 -pe "s/(?:[^\/\n]*\/){3}([^\s]*)[^\n]*/\1/g" \
    | sed -E "${sedcommands[@]}" || true)

    echo "$files" > differ_files

    if [[ $files = '' ]]; then
        # All differences are whitelisted
        exit 0
    fi

	exit 1
else
    # Builds are the same
    echo "" > differ_files
	exit 0
fi
