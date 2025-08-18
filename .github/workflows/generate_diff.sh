#!/usr/bin/env bash

set -euo pipefail

whitelist=()

if [ "$1" = "-oci" ]; then
    basefile_a="${2/bare-/}.oci"
    basefile_b="${2/bare-/}.oci"
    unpacked_a="$3"
    unpacked_b="$4"
    depth=$5
    result="$2-diff"
else
    basefile_a="$2.tar"
    basefile_b="$3.tar"
    unpacked_a="./A/unpacked"
    unpacked_b="./B/unpacked"
    depth="3"
    result="$1-diff"
fi

sedcommands=()

if [ ! ${#whitelist[@]} -eq 0 ]; then
    sedcommands+=("sed -E")
else 
    sedcommands+=("cat")
fi

for file in "${whitelist[@]}"; do
    sedcommands+=("-e")
    sedcommands+=("\|$file|d")
done

if ! cmp "A/$basefile_a" "B/$basefile_b" > /dev/null; then
    # Difference detected

    files=$(diff -qrN "$unpacked_a" "$unpacked_b" 2> /dev/null \
    | grep differ \
    | perl -0777 -pe "s/(?:[^\/\n]*\/){$depth}([^\s]*)[^\n]*/\1/g" \
    | "${sedcommands[@]}" || true)

    echo "$files" > "$result"

    if [[ $files = '' ]]; then
         # All differences are whitelisted
         exit 0
     fi

 	exit 1
else
    # Builds are the same
    echo "" > "$result"

    exit 0
fi
