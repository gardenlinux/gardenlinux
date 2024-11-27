SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c

ROOT_DIR := $(shell git rev-parse --show-toplevel)

ifeq ($(origin GL_VERSION), undefined)
GL_VERSION := latest
endif
ifeq ($(origin GL_REGISTRY), undefined)
GL_REGISTRY := ghcr.io/gardenlinux
endif
GL_IMAGE := $(GL_REGISTRY)/gardenlinux/platform-test-kvm:$(GL_VERSION)

GARDENLINUX_BUILD_CRE ?= podman

# Generate FLAVORS variable by running the flavor parser
FLAVORS_HYPERVISOR := $(shell $(ROOT_DIR)/bin/flavors_parse.py --category "hypervisor" --test-platform)
FLAVORS_PUBLIC_CLOUD := $(shell $(ROOT_DIR)/bin/flavors_parse.py --category "public-cloud" --test-platform)

CRE_CMD_BASE = $(GARDENLINUX_BUILD_CRE) run -it --rm -v $(ROOT_DIR):/gardenlinux
CRE_CMD_security = --cap-add SYS_ADMIN,MKNOD,AUDIT_WRITE,NET_RAW --security-opt apparmor=unconfined
CRE_CMD_priviliged = --privileged
CRE_CMD_tofu = $(CRE_CMD_BASE) -v ~/.ssh:/root/.ssh:ro $(GL_REGISTRY)/gardenlinux/platform-test-tofu:$(GL_VERSION)
CRE_CMD_firecracker = sudo $(CRE_CMD_BASE) $(CRE_CMD_security) $(CRE_CMD_priviliged) --device=/dev/kvm $(GL_REGISTRY)/gardenlinux/platform-test-firecracker:$(GL_VERSION)
CRE_CMD_kvm = $(CRE_CMD_BASE) $(CRE_CMD_security) --device=/dev/kvm -v /var/run/libvirt/libvirt-sock:/var/run/libvirt/libvirt-sock $(GL_REGISTRY)/gardenlinux/platform-test-kvm:$(GL_VERSION)

.PHONY: all
.DEFAULT: help

is_excluded = $(filter $(1),$(EXCLUDES))

# help: help					List available tasks of the project
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "general targets:"
	@grep -E '^# help: ' $(MAKEFILE_LIST) | sed 's/^# help: //g' | awk 'BEGIN {FS = ": "}; {printf "%-60s %s\n", $$1, $$2}'
	@echo ""
	@echo "platform-specific targets:"
	@$(foreach flavor,$(FLAVORS_HYPERVISOR), \
		printf "%-60s%s\n" "$(flavor)-test-platform" "Run platform tests via pytest --iaas for $(flavor)"; \
	)
	@$(foreach flavor,$(FLAVORS_PUBLIC_CLOUD), \
		printf "%-60s%s\n" "$(flavor)-test-platform" "Run platform tests via opentofu for $(flavor)"; \
	)

# help: all					Run all platform tests
all: test-platforms

### platform-specific targets
$(foreach flavor,$(FLAVORS_HYPERVISOR), \
	$(eval \
	  $(platform)-$(arch)-$(flavor)-test-platform: ; \
		  test -f $(ROOT_DIR)/tests/config/$(platform).$(arch).$(flavor).yaml || cp $(ROOT_DIR)/tests/config/$(platform).$(arch).$(flavor).yaml.example $(ROOT_DIR)/tests/config/$(platform).$(arch).$(flavor).yaml ; \
	      $(CRE_CMD_$(platform)) bash -c "pytest --iaas=$(platform) --configfile=/gardenlinux/tests/config/$(platform).$(arch).$(flavor).yaml --junit-xml=/gardenlinux/tests/$(platform).$(arch).$(flavor).platform.test.xml" ; \
	) \
)

$(foreach flavor,$(FLAVORS_PUBLIC_CLOUD), \
	$(eval \
	  $(flavor)-test-platform: ; \
	  	$(CRE_CMD_tofu) pytest --iaas=manual --configfile=/gardenlinux/tests/config/manual_$(flavor).yaml --junit-xml=/gardenlinux/tests/$(flavor).platform.test.xml ; \
	) \
)
