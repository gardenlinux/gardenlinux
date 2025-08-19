SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c

ROOT_DIR := $(shell git rev-parse --show-toplevel)

GIT_SHA:= $(shell git rev-parse HEAD)
GIT_SHA_SHORT := $(shell git rev-parse --short HEAD)

ifeq ($(origin GL_REGISTRY), undefined)
GL_REGISTRY := ghcr.io/gardenlinux
endif
ifeq ($(strip $(TARGETARCH)),)
ifeq ($(shell uname -m), aarch64)
TARGETARCH := arm64
else ifeq ($(shell uname -m), arm64)
TARGETARCH := arm64
else ifeq ($(shell uname -m), x86_64)
TARGETARCH := amd64
endif
endif

GARDENLINUX_BUILD_CRE ?= podman

PLATFORMS = kvm openstack tofu

.PHONY: all
.DEFAULT: help

# Define reusable functions
define copy_files
	cp $(ROOT_DIR)/tests/Pipfile $1/
	cp $(ROOT_DIR)/tests/Pipfile.lock $1/
	cp $(ROOT_DIR)/tests/platformSetup/tofu/providers.tf $1/
	cp $(ROOT_DIR)/tests/platformSetup/tofu/.terraform.lock.hcl $1/
endef

define pull_image
	$(GARDENLINUX_BUILD_CRE) pull $(GL_REGISTRY)/$(strip $1):$(strip $2) || true
endef

# build an image:
# $1 to_registry
# $2 to_image
# $3 to_tag
# $4 directory with Containerfile
# $5 additional options (optional)
define build_image
	$(GARDENLINUX_BUILD_CRE) build --build-arg TARGETARCH=$(TARGETARCH) --platform linux/$(TARGETARCH) $(strip $5) -t $(strip $1)/$(strip $2):$(strip $3) -t $(strip $1)/$(strip $2):$(GIT_SHA) -t $(strip $1)/$(strip $2):$(GIT_SHA_SHORT) $(strip $4)
endef

define clean_files
	rm $1/Pipfile
	rm $1/Pipfile.lock
	rm $1/providers.tf
	rm $1/.terraform.lock.hcl
endef

# help: help					List available tasks of the project
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "general targets:"
	@grep -E '^# help: ' $(MAKEFILE_LIST) | sed 's/^# help: //g' | awk 'BEGIN {FS = ": "}; {printf "%-80s %s\n", $$1, $$2}'
	@echo ""
	@echo "Available targets for Platform Test Images:"
	@echo ""
	@echo "all targets:"
	@printf "%-80s%s\n" "  pull-platform-test" "Pull all platform test images"
	@printf "%-80s%s\n" "  build-platform-test" "Build all platform test images"
	@echo ""
	@echo "base targets:"
	@printf "%-80s%s\n" "  pull-platform-test-base" "Pull the platform test base image"
	@printf "%-80s%s\n" "  build-platform-test-base" "Build the platform test base image"
	@echo ""
	@echo "platform-specific targets:"
	@$(foreach platform,$(PLATFORMS), \
		printf "%-80s%s\n" "  pull-platform-test-$(platform)" "Pull the platform test image for $(platform)"; \
	)
	@$(foreach platform,$(PLATFORMS), \
		printf "%-80s%s\n" "  build-platform-test-$(platform)" "Build the platform test image for $(platform)"; \
	)

# all					Build all platform test images
all: build-platform-test

# pull-platform-test-base			Pull the platform test base image
pull-platform-test-base:
	$(call pull_image, gardenlinux/platform-test-base, latest)

# pull-platform-test			Pull all platform test images
pull-platform-test: pull-platform-test-base $(addprefix pull-platform-test-,$(PLATFORMS))

# build-platform-test-base		Build the platform test base image
build-platform-test-base:
	$(call copy_files, platform-test-base)
	$(call build_image, $(GL_REGISTRY), gardenlinux/platform-test-base, latest, platform-test-base, --build-arg GITHUB_TOKEN=$(GITHUB_TOKEN) --build-arg GL_VERSION=nightly --pull=missing )
	$(call clean_files, platform-test-base)

# build-platform-test			Build all platform test images
build-platform-test: $(addprefix build-platform-test-,$(PLATFORMS))

# platform-specific targets
$(foreach platform,$(PLATFORMS),\
  $(eval \
    pull-platform-test-$(platform): ; \
		$(call pull_image, gardenlinux/platform-test-$(platform), latest) ; \
  ) \
  $(eval \
    build-platform-test-$(platform): ; \
		$(call copy_files, platform-test/$(platform)) ; \
		$(call pull_image, nightly, nightly) ; \
		$(call build_image, $(GL_REGISTRY), gardenlinux/platform-test-$(platform), latest, platform-test/$(platform), --build-arg GITHUB_TOKEN=$(GITHUB_TOKEN) --build-arg GL_VERSION=latest --pull=never ) ; \
		$(call clean_files, platform-test/$(platform)) \
  ) \
)
