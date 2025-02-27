SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c

ROOT_DIR := $(shell git rev-parse --show-toplevel)

# Generate FLAVORS variable by running the flavor parser
FLAVORS := $(shell $(ROOT_DIR)/bin/flavors_parse.py --exclude "bare-*" --build --test)
FLAVORS_BARE := $(shell $(ROOT_DIR)/bin/flavors_parse.py --include-only "bare-*" --build --test)

# Base commands
CMD_BUILD := $(ROOT_DIR)/build
FLAG_KMS := --kms
CMD_BUILD_BARE := $(ROOT_DIR)/build_bare_flavors
CMD_TEST := $(ROOT_DIR)/test

# Default value for USE_KMS
USE_KMS ?= false

.PHONY: help all

.DEFAULT: help

# help: help					List available tasks of the project
help:
	@echo "Usage: make [target] [USE_KMS=true/false]"
	@echo ""
	@echo "general targets:"
	@grep -E '^# help: ' $(MAKEFILE_LIST) | sed 's/^# help: //g' | awk 'BEGIN {FS = ": "}; {printf "%-60s %s\n", $$1, $$2}'
	@echo ""
	@echo "Available targets for Official Flavors:"
	@echo ""
	@echo "all targets:"
	@printf "%-80s%s\n" "  all" "Run build and Chroot tests for all flavors"
	@printf "%-80s%s\n" "  all-build" "Run build for all flavors"
	@printf "%-80s%s\n" "  all-test" "Run Chroot tests for all flavors"
	@echo ""
	@echo "base build targets:"
	@printf "%-80s%s\n" "  base-amd64-build" "Run bootstrap/base build for amd64"
	@printf "%-80s%s\n" "  base-arm64-build" "Run bootstrap/base build for arm64"
	@printf "%-80s%s\n" "  container-amd64-build" "Run base container build for amd64"
	@printf "%-80s%s\n" "  container-arm64-build" "Run base container build for arm64"
	@echo ""
	@echo "bare container flavor build targets:"
	@$(foreach flavor,$(FLAVORS_BARE), \
		printf "%-80s%s\n" "  $(flavor)-build" "Run build $(flavor)"; \
	)
	@echo ""
	@echo "image flavor build targets:"
	@$(foreach flavor,$(FLAVORS), \
		printf "%-80s%s\n" "  $(flavor)-build" "Run build $(flavor)"; \
	)
	@echo ""
	@echo "base Chroot tests targets:"
	@printf "%-80s%s\n" "  base-amd64-test" "Run bootstrap/base Chroot tests for amd64"
	@printf "%-80s%s\n" "  base-arm64-test" "Run bootstrap/base Chroot tests for arm64"
	@printf "%-80s%s\n" "  container-amd64-test" "Run base container Chroot tests for amd64"
	@printf "%-80s%s\n" "  container-arm64-test" "Run base container Chroot tests for arm64"
	@echo ""
	@echo "bare container flavor Chroot tests targets:"
	@$(foreach flavor,$(FLAVORS_BARE), \
		printf "%-80s%s\n" "  $(flavor)-test" "Run Chroot tests $(flavor)"; \
	)
	@echo ""
	@echo "image flavor Chroot tests targets:"
	@$(foreach flavor,$(FLAVORS), \
		printf "%-80s%s\n" "  $(flavor)-test" "Run Chroot tests $(flavor)"; \
	)

# all: Run build and test for all flavors
all: all-build

# Run build for all flavors
all-build: $(addsuffix -build, $(FLAVORS)) $(addsuffix -build, $(FLAVORS_BARE))

# Run test for all flavors
all-test: $(addsuffix -test, $(FLAVORS)) $(addsuffix -test, $(FLAVORS_BARE))

define build
$(1)-build:
	@echo "Running build for flavor $(1)"
	$(CMD_BUILD) $(1)
endef

define build_kms
$(1)-build:
	@echo "Running build for flavor $(1) with USE_KMS=$(USE_KMS)"
ifeq ($(USE_KMS), true)
	$(CMD_BUILD) $(FLAG_KMS) $(1)
else
	$(CMD_BUILD) $(1)
endif
endef

define build_bare
$(1)-build:
	@echo "Running build_bare_flavors for flavor $(1)"
	$(CMD_BUILD_BARE) $(subst bare-,,$(subst -amd64,,$(subst -arm64,,$(1))))
endef

define test
$(1)-test:
	@echo "Running test for flavor $(1)"
	$(CMD_TEST) $(1)
endef

# # Extract ARCH from the flavor string (e.g., "bare-python-amd64" -> "amd64")
bare_get_arch = $(shell echo $(1) | grep -oE '(amd64|arm64)')
# 
# # Extract CONFIG from the flavor string (e.g., "bare-python-amd64" -> "python")
bare_get_config = $(shell echo $(1) | sed 's/^bare-//' | sed 's/-amd64//' | sed 's/-arm64//')

define test_bare
$(1)-test:
	@echo "Running test for bare_flavor $(1)"
	$(eval ARCH := $(call bare_get_arch,$(1)))
	$(eval CONFIG := $(call bare_get_config,$(1)))
	$(eval IMAGE_PATH := $(ROOT_DIR)/.build/bare_flavors/$(CONFIG)-$(ARCH).oci)
	@ # TODO: properly load this per target
	$(eval IMAGE = $(shell test -f $(IMAGE_PATH) && podman load -qi $(IMAGE_PATH) 2>/dev/null | awk '{ print $$NF }'))
	@if [ -f "$(IMAGE_PATH)" ]; then \
		if [ -z "$(IMAGE)" ]; then \
			echo "Error: Failed to extract image name from podman load output."; \
			exit 1; \
		fi; \
		echo "CONFIG=$(CONFIG)"; \
		echo "ARCH=$(ARCH)"; \
		echo "IMAGE_PATH=$(IMAGE_PATH)"; \
		echo "IMAGE=$(IMAGE)"; \
		cd "$(ROOT_DIR)/bare_flavors/$(CONFIG)/test" && \
		podman build -t test --build-arg image=$(IMAGE) . && \
		podman run --rm test; \
	else \
		echo "Error: OCI file not found: $(IMAGE_PATH)"; \
		exit 1; \
	fi
endef

# Generate rules dynamically for all bare flavors
$(foreach flavor, $(FLAVORS_BARE), $(eval $(call build_bare, $(flavor))))
$(foreach flavor, $(FLAVORS_BARE), $(eval $(call test_bare, $(flavor))))

# Generate rules for base targets only
$(eval $(call build, base-amd64))
$(eval $(call build, base-arm64))
$(eval $(call test, base-amd64))
$(eval $(call test, base-arm64))

# Generate rules dynamically for all flavors
$(foreach flavor, $(FLAVORS), $(eval $(call build_kms, $(flavor))))
$(foreach flavor, $(FLAVORS), $(eval $(call test, $(flavor))))
