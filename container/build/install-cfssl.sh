#!usr/bin/env bash

# This script downloads cfssl binaries and moves them to /usr/bin/ (in PATH).
# With cfssl installed, our central build can just refer to the existing
# binaries instead of performing a fresh build every time.

cfssl_version="1.5.0"

cfssl_files=( \
    cfssl-bundle \
    cfssl-certinfo \
    cfssl-newkey \
    cfssl-scan \
    cfssljson \
    cfssl \
    mkbundle \
    multirootca \
)

for file in "${cfssl_files[@]}"; do
    outname="/usr/bin/${file}"
    url="https://github.com/cloudflare/cfssl/releases/download/v${cfssl_version}/${file}_${cfssl_version}_linux_amd64"
    wget --no-verbose -O "${outname}" "${url}"
    chmod +x "${outname}"
done