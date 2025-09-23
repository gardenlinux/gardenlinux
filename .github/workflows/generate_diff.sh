#!/usr/bin/env bash

set -euo pipefail

whitelist=()

nightly_whitelist=("etc/apt/sources\.list\.d/gardenlinux\.sources"
                   "etc/os-release"
                   "etc/shadow"
                   "etc/update-motd\.d/05-logo"
                   "var/lib/apt/lists/packages\.gardenlinux\.io_gardenlinux_dists_[0-9]*\.[0-9]*_.*"
                   "var/lib/apt/lists/packages\.gardenlinux\.io_gardenlinux_dists_[0-9]*\.[0-9]*_main_binary-(arm64|amd64)_Packages"
                   "efi/loader/entries/Default-[0-9]*\.[0-9]*\.[0-9]*-(cloud-)?(arm64|amd64)\.conf"
                   "efi/Default/[0-9]*\.[0-9]*\.[0-9]*-(cloud-)?(arm64|amd64)/initrd"
                   "boot/initrd\.img-[0-9]*\.[0-9]*\.[0-9]*-(cloud-)?(arm64|amd64)")

nightly=false
oci=false

while [ $# -gt 0 ]; do
	case "$1" in
		--oci)
			oci=true
			shift
			;;
		--nightly)
			nightly=true
			shift
			;;
		*)
			break
			;;
	esac
done

if $oci; then
    basefile_a="${1/bare-/}.oci"
    basefile_b="${1/bare-/}.oci"
    unpacked_a="$2"
    unpacked_b="$3"
    depth=$4
else
    basefile_a="$2.tar"
    basefile_b="$3.tar"
    unpacked_a="./A/unpacked"
    unpacked_b="./B/unpacked"
    depth="3"
fi

if $nightly; then
        whitelist=("${whitelist[@]}" "${nightly_whitelist[@]}")
fi

sedcommands=()

if [ ! ${#whitelist[@]} -eq 0 ]; then
    sedcommands+=("sed")
    sedcommands+=("-E")
else 
    sedcommands+=("cat")
fi

for file in "${whitelist[@]}"; do
    sedcommands+=("-e")
    sedcommands+=("\;$file;d")
done

if ! cmp "A/$basefile_a" "B/$basefile_b" > /dev/null; then
    # Difference detected

    files=$(diff -qrN "$unpacked_a" "$unpacked_b" 2> /dev/null \
    | grep differ \
    | perl -0777 -pe "s/(?:[^\/\n]*\/){$depth}([^\s]*)[^\n]*/\/\1/g" || true)

    filtered_files=$(echo "$files" | "${sedcommands[@]}")

    if [[ $files != '' && $filtered_files = '' ]]; then
         # All differences are whitelisted
         echo "whitelist" > "$1-diff"

         exit 0
    fi

    echo "$filtered_files" > "$1-diff"

 	exit 1
else
    # Builds are the same
    echo "" > "$1-diff"

    exit 0
fi
