SHELL := /usr/bin/env bash
.DEFAULT_GOAL := all

MAKEFLAGS += --no-builtin-rules

.DELETE_ON_ERROR:

# Architecture and platform definitions
ARCHES := amd64 arm64
PLATFORMS := ali azure aws openstack gcp
FORMATS := raw vhd qcow2

# Architecture to runtime mapping
ARCH_RUNTIME_amd64 := x86_64
ARCH_RUNTIME_arm64 := aarch64

# Platform to format mapping
PLATFORM_FORMAT_ali := raw
PLATFORM_FORMAT_azure := vhd
PLATFORM_FORMAT_aws := raw
PLATFORM_FORMAT_openstack := qcow2
PLATFORM_FORMAT_gcp := raw

# Generate arch-platform combinations
ARCH_PLATFORM_COMBINATIONS := $(foreach arch,$(ARCHES),$(foreach platform,$(PLATFORMS),$(arch)-$(platform)))

.PHONY: all dist clean help $(addprefix dist-,$(ARCHES)) $(addprefix dist-,$(FORMATS)) $(addprefix dist-,$(PLATFORMS)) $(addprefix dist-,$(ARCH_PLATFORM_COMBINATIONS))

# Calculate checksum of all files under git control (tracked + untracked, excluding gitignored)
.build/checksum: | .build
	( git ls-files && git ls-files --others --exclude-standard ) \
		| sort -u \
		| xargs sha256sum \
		| sha256sum \
		| cut -d' ' -f1 > $@

all: .build/dist.tar.gz

dist: .build/dist.tar.gz

# Architecture-specific targets
$(addprefix dist-,$(ARCHES)): dist-%: | .build
	@$(MAKE) .build/dist-$*.tar.gz

# Format-specific targets
$(addprefix dist-,$(FORMATS)): dist-%: | .build
	@$(MAKE) .build/dist-$*.tar.gz

# Platform-specific targets
define PLATFORM_TARGET_template
dist-$(1): dist-$(PLATFORM_FORMAT_$(1))
endef
$(foreach platform,$(PLATFORMS),$(eval $(call PLATFORM_TARGET_template,$(platform))))

# Architecture + Platform combination targets
$(addprefix dist-,$(ARCH_PLATFORM_COMBINATIONS)): dist-%: | .build
	@$(MAKE) .build/dist-$*.tar.gz

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

# Template for architecture-specific builds
define ARCH_BUILD_template
.build/dist-$(1).tar.gz: .build/checksum util/build_dist.sh .build/runtime-$(ARCH_RUNTIME_$(1)).tar.gz conftest.py $$(wildcard plugins/*.py) $$(wildcard test_*.py) | .build
	@checksum=$$$$(cat .build/checksum); \
	checksummed_file=".build/tests-ng-dist-$(1)-$$$$checksum.tar.gz"; \
	util/build_dist.sh "$$$$checksummed_file" $(ARCH_RUNTIME_$(1)):.build/runtime-$(ARCH_RUNTIME_$(1)).tar.gz; \
	ln -sf "tests-ng-dist-$(1)-$$$$checksum.tar.gz" .build/tests-ng-dist-$(1).tar.gz; \
	ln -sf "tests-ng-dist-$(1)-$$$$checksum.tar.gz" .build/tests-ng-dist.tar.gz
endef
$(foreach arch,$(ARCHES),$(eval $(call ARCH_BUILD_template,$(arch))))

# Template for format-specific builds
define FORMAT_BUILD_template
.build/dist-$(1).tar.gz: .build/checksum util/build_dist.sh .build/runtime-x86_64.tar.gz .build/runtime-aarch64.tar.gz conftest.py $$(wildcard plugins/*.py) $$(wildcard test_*.py) | .build
	@checksum=$$$$(cat .build/checksum); \
	checksummed_file=".build/tests-ng-dist-$(1)-$$$$checksum.tar.gz"; \
	util/build_dist.sh "$$$$checksummed_file" --formats $(1) x86_64:.build/runtime-x86_64.tar.gz aarch64:.build/runtime-aarch64.tar.gz; \
	ln -sf "tests-ng-dist-$(1)-$$$$checksum.tar.gz" .build/tests-ng-dist-$(1).tar.gz; \
	ln -sf "tests-ng-dist-$(1)-$$$$checksum.tar.gz" .build/tests-ng-dist.tar.gz; \
	ln -sf "tests-ng-dist-$(1)-$$$$checksum.disk.$(1)" .build/tests-ng-dist.disk.$(1); \
	ln -sf "tests-ng-dist-$(1)-$$$$checksum.disk.$(1).tar.gz" .build/tests-ng-dist.disk.$(1).tar.gz
endef
$(foreach format,$(FORMATS),$(eval $(call FORMAT_BUILD_template,$(format))))

# Template for architecture + platform combination builds
define ARCH_PLATFORM_BUILD_template
.build/dist-$(1)-$(2).tar.gz: .build/checksum util/build_dist.sh .build/runtime-$(ARCH_RUNTIME_$(1)).tar.gz conftest.py $$(wildcard plugins/*.py) $$(wildcard test_*.py) | .build
	@checksum=$$$$(cat .build/checksum); \
	checksummed_file=".build/tests-ng-dist-$(1)-$(2)-$$$$checksum.tar.gz"; \
	util/build_dist.sh "$$$$checksummed_file" --formats $(PLATFORM_FORMAT_$(2)) $(ARCH_RUNTIME_$(1)):.build/runtime-$(ARCH_RUNTIME_$(1)).tar.gz; \
	ln -sf "tests-ng-dist-$(1)-$(2)-$$$$checksum.tar.gz" .build/tests-ng-dist-$(1)-$(2).tar.gz; \
	ln -sf "tests-ng-dist-$(1)-$(2)-$$$$checksum.tar.gz" .build/tests-ng-dist.tar.gz; \
	ln -sf "tests-ng-dist-$(1)-$(2)-$$$$checksum.disk.$(PLATFORM_FORMAT_$(2))" .build/tests-ng-dist.disk.$(PLATFORM_FORMAT_$(2)); \
	ln -sf "tests-ng-dist-$(1)-$(2)-$$$$checksum.disk.$(PLATFORM_FORMAT_$(2)).tar.gz" .build/tests-ng-dist.disk.$(PLATFORM_FORMAT_$(2)).tar.gz
endef
$(foreach arch,$(ARCHES),$(foreach platform,$(PLATFORMS),$(eval $(call ARCH_PLATFORM_BUILD_template,$(arch),$(platform)))))

.build/runtime-%.tar.gz: util/build_runtime.sh util/requirements.txt | .build
	./$< $* $(word 2,$^) $@

clean:
	@echo "Cleaning build artifacts..."
	rm -rf .build

help:
	@echo "Available targets:"
	@echo "  all, dist          - Build distribution for all architectures and formats"
	@echo ""
	@echo "Architecture-specific builds:"
	@echo "  dist-amd64        - Build distribution for amd64 only"
	@echo "  dist-arm64        - Build distribution for arm64 only"
	@echo ""
	@echo "Format-specific builds:"
	@echo "  dist-raw           - Build raw disk format (for GCP, AWS, ALI)"
	@echo "  dist-vhd           - Build VHD disk format (for Azure)"
	@echo "  dist-qcow2         - Build QCOW2 disk format (for OpenStack)"
	@echo ""
	@echo "Platform-specific builds:"
	@echo "  dist-ali           - Build for Alibaba Cloud (qcow2 format)"
	@echo "  dist-azure         - Build for Microsoft Azure (vhd format)"
	@echo "  dist-aws           - Build for Amazon Web Services (raw format)"
	@echo "  dist-openstack     - Build for OpenStack (qcow2 format)"
	@echo "  dist-gcp           - Build for Google Cloud Platform (raw format)"
	@echo ""
	@echo "Architecture + Platform combinations:"
	@echo "  dist-amd64-ali     - Build amd64 for Alibaba Cloud"
	@echo "  dist-amd64-azure   - Build amd64 for Microsoft Azure"
	@echo "  dist-amd64-aws     - Build amd64 for Amazon Web Services"
	@echo "  dist-amd64-openstack - Build amd64 for OpenStack"
	@echo "  dist-amd64-gcp     - Build amd64 for Google Cloud Platform"
	@echo "  dist-arm64-ali     - Build arm64 for Alibaba Cloud"
	@echo "  dist-arm64-azure   - Build arm64 for Microsoft Azure"
	@echo "  dist-arm64-aws     - Build arm64 for Amazon Web Services"
	@echo "  dist-arm64-openstack - Build arm64 for OpenStack"
	@echo "  dist-arm64-gcp     - Build arm64 for Google Cloud Platform"
	@echo ""
	@echo "  clean              - Remove all build artifacts"
	@echo "  help               - Show this help message"
