#!/usr/bin/env -S make -f

MAKEFLAGS += --no-builtin-rules

.SILENT:
.DELETE_ON_ERROR:

.PHONY: dist clean

all: dist edk2
dist: .build/dist.tar.gz .build/dist.ext2
edk2: .build/edk2-qemu-x86_64-code .build/edk2-qemu-x86_64-vars .build/edk2-qemu-aarch64-code .build/edk2-qemu-aarch64-vars

clean:
	rm -rf .build

.build:
	mkdir .build

.build/dist.tar.gz: util/build_dist.sh .build/runtime-x86_64.tar.gz .build/runtime-aarch64.tar.gz conftest.py $(wildcard plugins/*.py) $(wildcard test_*.py) | .build
	echo '🛠️  building test framework distribution'
	./$< $@ x86_64:$(word 2,$^) aarch64:$(word 3,$^)

.build/dist.ext2: util/build_ext2.sh .build/dist.tar.gz | .build
	echo '🛠️  bundling test framework as disk image'
	./$^ $@

.build/runtime-%.tar.gz: util/build_runtime.sh util/requirements.txt | .build
	echo '🛠️  building python runtime for $*'
	./$< $* $(word 2,$^) $@

.build/edk2-%: | .build
	echo '⬇️  fetching EDK2 ($*)'
	curl -sSLf "https://github.com/gardenlinux/edk2-build/releases/download/edk2-stable202505/edk2-$*" > $@
