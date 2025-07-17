SHELL := /usr/bin/env bash
.DEFAULT_GOAL := all

MAKEFLAGS += --no-builtin-rules

.SILENT:
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
	ln -sf "tests-ng-dist-$$checksum.tar.gz" .build/tests-ng-dist.tar.gz

.build/runtime-%.tar.gz: util/build_runtime.sh util/requirements.txt | .build
	./$< $* $(word 2,$^) $@

clean:
	@echo "Cleaning build artifacts..."
	rm -rf .build

