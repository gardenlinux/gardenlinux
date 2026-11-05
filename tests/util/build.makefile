#!/usr/bin/env -S make -f

MAKEFLAGS += --no-builtin-rules

.SILENT:
.DELETE_ON_ERROR:

.PHONY: help all dist dist-disk oci \
	dist-amd64 dist-arm64 \
	dist-disk-amd64 dist-disk-arm64 \
	oci-amd64 oci-arm64 \
	runtime-amd64 runtime-arm64 \
	edk2 clean

# Default target: show help when invoked without arguments.
.DEFAULT_GOAL := help

help:
	echo 'Garden Linux test build system'
	echo ''
	echo 'Usage: make -f util/build.makefile <target>'
	echo ''
	echo 'Aggregate targets:'
	echo '  all               build everything (dist-disk + edk2)'
	echo '  dist              build dist tarballs for both arches + edk2'
	echo '  dist-disk         build dist ext2 disk images for both arches (+ dist, edk2)'
	echo '  oci               build multiarch OCI test image (.build/dist.oci)'
	echo '  edk2              download EDK2 firmware for both arches'
	echo '  clean             remove the .build directory'
	echo '  help              show this help'
	echo ''
	echo 'Per-arch targets (amd64 / arm64):'
	echo '  runtime-<arch>    build python runtime tarball (.build/runtime-<arch>.tar.gz)'
	echo '  dist-<arch>       build test dist tarball      (.build/dist-<arch>.tar.gz)'
	echo '  dist-disk-<arch>  build test dist disk image   (.build/dist-<arch>.ext2.raw'
	echo '                    plus .vhd / .qcow2 / .ext2.raw.tar.gz derivatives)'
	echo '  oci-<arch>        build single-arch OCI image  (.build/dist-<arch>.oci)'
	echo ''
	echo 'Examples:'
	echo '  make -f util/build.makefile dist-amd64'
	echo '  make -f util/build.makefile dist-disk-arm64'
	echo '  make -f util/build.makefile oci-amd64'
	echo '  make -f util/build.makefile oci'
	echo '  make -f util/build.makefile all'

all: dist-disk edk2
dist: .build/dist-amd64.tar.gz .build/dist-arm64.tar.gz edk2
dist-disk: dist .build/dist-amd64.ext2.raw .build/dist-arm64.ext2.raw
edk2: .build/edk2-qemu-x86_64-code .build/edk2-qemu-x86_64-vars .build/edk2-qemu-aarch64-code .build/edk2-qemu-aarch64-vars

runtime-amd64:   .build/runtime-amd64.tar.gz
runtime-arm64:   .build/runtime-arm64.tar.gz
dist-amd64:      .build/dist-amd64.tar.gz
dist-arm64:      .build/dist-arm64.tar.gz
dist-disk-amd64: .build/dist-amd64.ext2.raw
dist-disk-arm64: .build/dist-arm64.ext2.raw
oci-amd64:       .build/dist-amd64.oci
oci-arm64:       .build/dist-arm64.oci
oci:             .build/dist.oci

clean:
	rm -rf .build

.build:
	mkdir .build

.build/dist-%.tar.gz: util/build_dist.sh .build/runtime-%.tar.gz conftest.py $(wildcard handlers/*.py) $(shell find integration -name 'test_*.py' 2>/dev/null) $(wildcard plugins/*.py) | .build
	echo '🛠️  building test framework distribution ($*)'
	./$< $(word 2,$^) $@ $*

.build/dist-%.ext2.raw: util/build_dist_image.sh .build/dist-%.tar.gz | .build
	echo '🛠️  bundling test framework as disk image ($*)'
	./$< $(word 2,$^) $@

.build/runtime-%.tar.gz: util/build_runtime.sh util/requirements.txt util/python.env.sh | .build
	echo '🛠️  building python runtime ($*)'
	./$< $(word 2,$^) $(word 3,$^) $@ $*

.build/dist-%.oci: util/build_oci.sh .build/dist-%.tar.gz util/container/Containerfile util/container/enter_host_ns.c | .build
	echo '🛠️  building OCI test image ($*)'
	./$< .build $@ $*

.build/dist.oci: util/build_multiarch_oci.sh .build/dist-amd64.oci .build/dist-arm64.oci | .build
	echo '🛠️  building multiarch OCI test image'
	./$< .build $@

.build/edk2-%: | .build
	echo '⬇️  fetching EDK2 ($*)'
	curl -sSLf "https://github.com/gardenlinux/edk2-build/releases/download/edk2-stable202505/edk2-$*" > $@
