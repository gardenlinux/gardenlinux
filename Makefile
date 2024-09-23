SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c

ROOT_DIR := $(shell git rev-parse --show-toplevel)
GIT_SHA := $(shell git rev-parse HEAD)
GIT_SHA_SHORT := $(shell git rev-parse --short HEAD)
ifeq ($(origin GL_VERSION), undefined)
GL_VERSION := $(shell $(ROOT_DIR)/bin/garden-version-latest)
endif
ifeq ($(origin GL_DATE), undefined)
GL_DATE := $(shell $(ROOT_DIR)/bin/garden-version --date $(GL_VERSION))
endif
ifeq ($(origin GL_REGISTRY), undefined)
GL_REGISTRY := ghcr.io/gardenlinux
endif
GL_IMAGE := $(GL_REGISTRY)/gardenlinux/platform-test-kvm:$(GL_VERSION)

ARCH := $(shell uname -m)
ifeq ($(ARCH), x86_64)
    ARCH := amd64
endif
ifeq ($(ARCH), aarch64)
    ARCH := arm64
endif

GARDENLINUX_BUILD_CRE ?= sudo podman

PLATFORMS := chroot kvm
TARGETS := kvm_dev kvm_dev_trustedboot kvm_dev_trustedboot_tpm2 kvm kvm_trustedboot kvm_trustedboot_tpm2 metal metal_trustedboot metal_trustedboot_tpm2 gcp gdch aws aws_trustedboot aws_trustedboot_tpm2 azure ali openstack openstackbaremetal vmware metal_pxe firecracker metal-vhost
MODIFIERS := gardener_prod

.PHONY: all
.DEFAULT: help

# help: help					List available tasks of the project
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "general targets:"
	@grep -E '^# help: ' $(MAKEFILE_LIST) | sed 's/^# help: //g' | awk 'BEGIN {FS = ": "}; {printf "%-60s %s\n", $$1, $$2}'
	@echo ""
	@echo "specific targets:"
	@$(foreach target,$(TARGETS), \
    	$(foreach modifier,$(MODIFIERS),\
    		printf "%-60s%s\n" "build-$(target)" "Build target $(target)"; \
    	) \
	)	
	@echo ""
	@echo "specific targets with modifiers:"
	@$(foreach target,$(TARGETS), \
    	$(foreach modifier,$(MODIFIERS),\
    		printf "%-60s%s\n" "build-$(target)-$(modifier)-$(ARCH)" "Build target $(target) with modfier $(modifier) on $(ARCH)"; \
    	) \
	)	

# help: all					Run all platform tests
all: test-platforms

### specific targets
$(foreach target,$(TARGETS), \
  $(foreach modifier,$(MODIFIERS), \
    $(eval \
      build-$(target): ; \
      ./build $(target); \
    ) \
    $(eval \
      build-$(target)-$(modifier)-$(ARCH): ; \
      ./build $(target)-$(modifier)-$(ARCH); \
    ) \
  ) \
)	
