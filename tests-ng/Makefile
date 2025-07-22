SHELL := /usr/bin/env bash
.DEFAULT_GOAL := all

MAKEFLAGS += --no-builtin-rules

.DELETE_ON_ERROR:

.PHONY: all dist clean help

# Calculate checksum of all files under git control (tracked + untracked, excluding gitignored)
.build/checksum: | .build
	( git ls-files && git ls-files --others --exclude-standard ) \
		| sort -u \
		| xargs sha256sum \
		| sha256sum \
		| cut -d' ' -f1 > $@

all: .build/dist.tar.gz

dist: .build/dist.tar.gz

.build:
	mkdir -p .build

.build/dist.tar.gz: .build/checksum util/build_dist.sh .build/runtime-x86_64.tar.gz .build/runtime-aarch64.tar.gz conftest.py $(wildcard plugins/*.py) $(wildcard test_*.py) | .build
	@checksum=$$(cat .build/checksum); \
	checksummed_file=".build/tests-ng-dist-$$checksum.tar.gz"; \
	util/build_dist.sh "$$checksummed_file" x86_64:.build/runtime-x86_64.tar.gz aarch64:.build/runtime-aarch64.tar.gz; \
	ln -sf "tests-ng-dist-$$checksum.tar.gz" .build/tests-ng-dist.tar.gz; \
	ln -sf "tests-ng-dist-$$checksum.disk.raw" .build/tests-ng-dist.disk.raw; \
	ln -sf "tests-ng-dist-$$checksum.disk.raw.tar.gz" .build/tests-ng-dist.disk.raw.tar.gz; \
	ln -sf "tests-ng-dist-$$checksum.disk.vhd" .build/tests-ng-dist.disk.vhd; \
	ln -sf "tests-ng-dist-$$checksum.disk.vhd.tar.gz" .build/tests-ng-dist.disk.vhd.tar.gz; \
	ln -sf "tests-ng-dist-$$checksum.disk.qcow2" .build/tests-ng-dist.disk.qcow2; \
	ln -sf "tests-ng-dist-$$checksum.disk.qcow2.tar.gz" .build/tests-ng-dist.disk.qcow2.tar.gz

.build/runtime-%.tar.gz: util/build_runtime.sh util/requirements.txt | .build
	./$< $* $(word 2,$^) $@

clean:
	@echo "Cleaning build artifacts..."
	rm -rf .build
