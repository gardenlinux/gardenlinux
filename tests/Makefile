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

GARDENLINUX_BUILD_CRE ?= sudo podman

# PLATFORMS = ali aws azure firecracker gcp kvm openstack
PLATFORMS = chroot kvm aws azure gcp firecracker

CRE_CMD_BASE = $(GARDENLINUX_BUILD_CRE) run -it --rm -v $(ROOT_DIR):/gardenlinux
#CRE_CMD_BASE = $(GARDENLINUX_BUILD_CRE) run -it -p 2223:2223 -v $(ROOT_DIR):/gardenlinux
CRE_CMD_security = --cap-add SYS_ADMIN,MKNOD,AUDIT_WRITE,NET_RAW --security-opt apparmor=unconfined
CRE_CMD_priviliged = --privileged
CRE_CMD_chroot = $(CRE_CMD_BASE) $(CRE_CMD_security) $(GL_REGISTRY)/gardenlinux/platform-test-kvm:$(GL_VERSION)
CRE_CMD_kvm = $(CRE_CMD_BASE) --device=/dev/kvm $(GL_REGISTRY)/gardenlinux/platform-test-kvm:$(GL_VERSION)
CRE_CMD_aws = $(CRE_CMD_BASE) -v ~/.aws:/root/.aws -e AWS_PROFILE $(GL_REGISTRY)/gardenlinux/platform-test-aws:$(GL_VERSION)
CRE_CMD_azure = $(CRE_CMD_BASE) -v ~/.azure:/root/.azure $(GL_REGISTRY)/gardenlinux/platform-test-azure:$(GL_VERSION)
CRE_CMD_gcp = $(CRE_CMD_BASE) -v ~/.config/gcloud:/root/.config/gcloud $(GL_REGISTRY)/gardenlinux/platform-test-gcp:$(GL_VERSION)
CRE_CMD_firecracker = $(CRE_CMD_BASE) $(CRE_CMD_priviliged) $(GL_REGISTRY)/gardenlinux/platform-test-firecracker:$(GL_VERSION)

.PHONY: all
.DEFAULT: help

# Define reusable functions
define check_image_file
	$(CRE_CMD_$(1)) test -f $(shell yq -r ".$(1).image" $(ROOT_DIR)/tests/config/kvm.yaml)
	if [ $$? -ne 0 ] ; then
		$(error "Image for $(1) not found\n")
	fi
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
		printf "%-40s%s\n" "test-platform-$(platform)" "Run platform tests for $(platform)"; \
	)

# help: all					Run all platform tests
all: test-platforms

### platform-specific targets
$(foreach platform,$(PLATFORMS),\
  $(eval \
    test-platform-$(platform): ; \
		$(CRE_CMD_$(platform)) pytest --iaas=$(platform) --configfile=/gardenlinux/tests/config/$(platform).yaml ; \
  ) \
)
