#!/usr/bin/env bash

set -euo pipefail

whitelist=("dummypath_abcd...")

if [ -z ${2+x} ]; then
    # $2 is unset
    basefile_a="${1/bare-/}.oci"
    basefile_b="${1/bare-/}.oci"
else
    # $2 is set
    basefile_a="$2.tar"
    basefile_b="$3.tar"
fi

sedcommands=()

for file in "${whitelist[@]}"; do
    sedcommands+=("-e")
    sedcommands+=("\|$file|d")
done

if ! cmp "A/$basefile_a" "B/$basefile_b" > /dev/null; then
    # Difference detected

    files=$(diff -qrN ./A/unpacked ./B/unpacked 2> /dev/null \
    | grep differ \
    | perl -0777 -pe "s/(?:[^\/\n]*\/){3}([^\s]*)[^\n]*/\1/g" \
    | sed -E "${sedcommands[@]}" || true)

    echo "$files" > "$1-diff"

    if [[ $files = '' ]]; then
         # All differences are whitelisted
         exit 0
     fi

 	exit 1
else
    # Builds are the same
    echo "" > "$1-diff"

    exit 0
fi
