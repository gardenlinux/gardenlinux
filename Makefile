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

# Default value for USE_KMS
USE_KMS ?= false

.PHONY: help all

.DEFAULT: help

# help: help					List available tasks of the project
help:
	@echo "Usage: make [target] [USE_KMS=true/false]"
	@echo ""
	@echo "general targets:"
	@grep -E '^# help: ' $(MAKEFILE_LIST) | sed 's/^# help: //g' | awk 'BEGIN {FS = ": "}; {printf "%-80s %s\n", $$1, $$2}'
	@echo ""
	@echo "Available targets for Official Flavors:"
	@echo ""
	@echo "all targets:"
	@printf "%-80s%s\n" "  all" "Run build for all flavors"
	@printf "%-80s%s\n" "  all-build" "Run build for all flavors"
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

# all: Run build for all flavors
all: all-build

# Run build for all flavors
all-build: $(addsuffix -build, $(FLAVORS)) $(addsuffix -build, $(FLAVORS_BARE))

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

# Generate rules dynamically for all bare flavors
$(foreach flavor, $(FLAVORS_BARE), $(eval $(call build_bare, $(flavor))))

# Generate rules for base targets only
$(eval $(call build, base-amd64))
$(eval $(call build, base-arm64))

# Generate rules dynamically for all flavors
$(foreach flavor, $(FLAVORS), $(eval $(call build_kms, $(flavor))))