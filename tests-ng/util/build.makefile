#!/usr/bin/env -S make -f

MAKEFLAGS += --no-builtin-rules

.SILENT:
.DELETE_ON_ERROR:

.PHONY: dist clean

all: dist edk2
dist: .build/dist.tar.gz .build/dist.ext2.raw
edk2: .build/edk2-qemu-x86_64-code .build/edk2-qemu-x86_64-vars .build/edk2-qemu-aarch64-code .build/edk2-qemu-aarch64-vars

clean:
	rm -rf .build

.build:
	mkdir .build

.build/dist.tar.gz: util/build_dist.sh .build/runtime.tar.gz conftest.py $(wildcard plugins/*.py) $(wildcard test_*.py) $(wildcard */test_*.py) | .build
	echo '🛠️  building test framework distribution'
	./$< $(word 2,$^) $@

.build/dist.ext2.raw: util/build_dist_image.sh .build/dist.tar.gz | .build
	echo '🛠️  bundling test framework as disk image'
	./$^ $@

.build/runtime.tar.gz: util/build_runtime.sh util/requirements.txt util/python.env.sh | .build
	echo '🛠️  building python runtime'
	./$^ $@

.build/edk2-%: | .build
	echo '⬇️  fetching EDK2 ($*)'
	retry -d "1,2,5,10,30" curl -sSLf "https://github.com/gardenlinux/edk2-build/releases/download/edk2-stable202505/edk2-$*" > $@
