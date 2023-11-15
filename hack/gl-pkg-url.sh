#!/bin/bash

# Parameter 1: garden linux version
# Parameter 2: ARCH (arm64, amd64, all)
# Parameter 3: package name (wildcard allowed, but then you must enclouse parameter with quotes)
# Outputs a list of kernel packages
#
# Example: ./gl-pkg-url.sh 934.10 amd64 linux-headers

GL_VERSION=${1:-today}
GL_ARCH=${2:-"amd64"}
GL_PKG_NAME=${3:-"linux*"}

packages_url="http://repo.gardenlinux.io/gardenlinux/dists/${GL_VERSION}/main/binary-${GL_ARCH}/Packages"

packages=$(curl -s "$packages_url" | grep "Filename: pool/main/.*/$GL_PKG_NAME" | cut -d':' -f 2)

for p in $packages; do
    echo "http://repo.gardenlinux.io/gardenlinux/$p"
done
