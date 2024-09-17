SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c

ROOT_DIR := $(shell git rev-parse --show-toplevel)
GIT_SHA:= $(shell git rev-parse HEAD)
GIT_SHA_SHORT := $(shell git rev-parse --short HEAD)
ifeq ($(strip $(GL_VERSION)),)
GL_VERSION := $(shell $(ROOT_DIR)/bin/garden-version-resolver --latest)
endif
ifeq ($(strip $(GL_REGISTRY)),)
GL_REGISTRY := ghcr.io/gardenlinux
endif

GARDENLINUX_BUILD_CRE ?= sudo podman

PLATFORMS = ali aws azure firecracker gcp kvm openstack

.PHONY: all
.DEFAULT: help

# Define reusable functions
define copy_files
	cp $(ROOT_DIR)/tests/Pipfile $1/
	cp $(ROOT_DIR)/tests/Pipfile.lock $1/
endef

define pull_image
	$(GARDENLINUX_BUILD_CRE) pull $(GL_REGISTRY)/$(strip $1):$(GL_VERSION)
endef

define build_image
	$(GARDENLINUX_BUILD_CRE) build --build-arg GL_VERSION=$(GL_VERSION) -t $1:$(GL_VERSION) -t $1:$(GIT_SHA) -t $1:$(GIT_SHA_SHORT) $2
endef

define push_image
	$(GARDENLINUX_BUILD_CRE) push $(strip $1):$(GL_VERSION) $(GL_REGISTRY)/$(strip $1):$(GIT_SHA)
	$(GARDENLINUX_BUILD_CRE) push $(strip $1):$(GL_VERSION) $(GL_REGISTRY)/$(strip $1):$(GIT_SHA_SHORT)
endef

define push_image_release
	$(GARDENLINUX_BUILD_CRE) push $(strip $1):$(GL_VERSION) $(GL_REGISTRY)/$(strip $1):$(GL_VERSION)
endef

define clean_files
	rm $1/Pipfile
	rm $1/Pipfile.lock
endef

# help: help					List available tasks of the project
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "general targets:"
	@grep -E '^# help: ' $(MAKEFILE_LIST) | sed 's/^# help: //g' | awk 'BEGIN {FS = ": "}; {printf "%-40s %s\n", $$1, $$2}'
	@echo ""
	@echo "platform-specific targets:"
	@$(foreach platform,$(PLATFORMS), \
		printf "%-40s%s\n" "pull-platform-test-$(platform)" "Pull the platform test image for $(platform)"; \
	)
	@$(foreach platform,$(PLATFORMS), \
		printf "%-40s%s\n" "build-platform-test-$(platform)" "Build the platform test image for $(platform)"; \
	)
	@$(foreach platform,$(PLATFORMS), \
		printf "%-40s%s\n" "push-platform-test-$(platform)" "Push the platform test image for $(platform)"; \
	)
	@$(foreach platform,$(PLATFORMS), \
		printf "%-40s%s\n" "push-release-platform-test-$(platform)" "Push the platform test image for $(platform) with release tag"; \
	)

# help: all					Build all platform test images
all: build-platform-test

# help: all-push				Build and push all platform test images
all-push: build-platform-test push-platform-test

# help: pull-platform-test-base			Pull the platform test base image
pull-platform-test-base:
	$(call pull_image, gardenlinux/platform-test-base)

# help: pull-platform-test			Pull all platform test images
pull-platform-test: pull-platform-test-base $(addprefix pull-platform-test-,$(PLATFORMS))

# help: build-platform-test-base		Build the platform test base image
build-platform-test-base: pull-platform-test-base
	$(call copy_files, platform-test-base)
	$(call build_image, gardenlinux/platform-test-base, platform-test-base)
	$(call build_image, $(GL_REGISTRY)/gardenlinux/platform-test-base, platform-test-base)
	$(call clean_files, platform-test-base)

# help: build-platform-test			Build all platform test images
build-platform-test: $(addprefix build-platform-test-,$(PLATFORMS))

# platform-specific targets
$(foreach platform,$(PLATFORMS),\
  $(eval \
    pull-platform-test-$(platform): ; \
		$(call pull_image, gardenlinux/platform-test-$(platform)) ; \
  ) \
)
$(foreach platform,$(PLATFORMS),\
  $(eval \
    build-platform-test-$(platform): build-platform-test-base pull-platform-test-$(platform); \
		$(call copy_files, platform-test/$(platform)) ; \
		$(call build_image, gardenlinux/platform-test-$(platform), platform-test/$(platform)) ; \
		$(call build_image, $(GL_REGISTRY)/gardenlinux/platform-test-$(platform), platform-test/$(platform)) ; \
		$(call clean_files, platform-test/$(platform)) \
  ) \
)
$(foreach platform,$(PLATFORMS),\
  $(eval \
    push-platform-test-$(platform): ; \
		$(call push_image, gardenlinux/platform-test-$(platform)) ; \
  ) \
)
$(foreach platform,$(PLATFORMS),\
  $(eval \
    push-release-platform-test-$(platform): ; \
		$(call push_image_release, gardenlinux/platform-test-$(platform)) ; \
  ) \
)

# help: push-platform-test-base			Push the platform test base image
push-platform-test-base:
	$(call push_image, gardenlinux/platform-test-base)

# help: push-release-platform-test-base		Push the platform test base image with release tag
push-release-platform-test-base:
	$(call push_image_release, gardenlinux/platform-test-base)

# help: push-platform-test			Push all platform test images
push-platform-test: push-platform-test-base $(addprefix push-platform-test-,$(PLATFORMS))

# help: push-release-platform-test		Push all platform test images with release tag
push-release-platform-test: push-release-platform-test-base $(addprefix push-release-platform-test-,$(PLATFORMS))
