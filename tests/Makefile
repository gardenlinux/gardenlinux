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
FLAVORS_PUBLIC_CLOUD := $(shell $(ROOT_DIR)/bin/flavors_parse.py --category "public-cloud" --test-platform)
FLAVORS_LOCAL := $(shell $(ROOT_DIR)/bin/flavors_parse.py --include-only "kvm-*" --include-only "firecracker-*")

CRE_CMD_BASE = $(GARDENLINUX_BUILD_CRE) run -it --rm -v $(ROOT_DIR):/gardenlinux
CRE_CMD_security = --cap-add SYS_ADMIN,MKNOD,AUDIT_WRITE,NET_RAW --security-opt apparmor=unconfined
CRE_CMD_priviliged = --privileged
CRE_CMD_tofu = $(CRE_CMD_BASE) -v ~/.ssh:/root/.ssh:ro $(GL_REGISTRY)/gardenlinux/platform-test-tofu:$(GL_VERSION)
CRE_CMD_firecracker = sudo $(CRE_CMD_BASE) $(CRE_CMD_security) $(CRE_CMD_priviliged) --device=/dev/kvm $(GL_REGISTRY)/gardenlinux/platform-test-firecracker:$(GL_VERSION)
CRE_CMD_kvm = $(CRE_CMD_BASE) $(CRE_CMD_security) -v ~/.ssh:/root/.ssh:ro --device=/dev/kvm $(GL_REGISTRY)/gardenlinux/platform-test-kvm:$(GL_VERSION)

.PHONY: all
.DEFAULT: help

is_excluded = $(filter $(1),$(EXCLUDES))

# help: help					List available tasks of the project
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "general targets:"
	@grep -E '^# help: ' $(MAKEFILE_LIST) | sed 's/^# help: //g' | awk 'BEGIN {FS = ": "}; {printf "%-80s %s\n", $$1, $$2}'
	@echo ""
	@echo "Available Platform Test targets for Official Flavors:"
	@echo ""
	@echo "Qemu Provisioner Platform Tests targets:"
	@$(foreach flavor,$(FLAVORS_PUBLIC_CLOUD) $(FLAVORS_LOCAL), \
		printf "%-80s%s\n" "  $(flavor)-qemu-test-platform" "Run platform tests build with Qemu for $(flavor)"; \
	)
	@echo ""
	@echo "Tofu Provisioner Platform Tests targets:"
	@$(foreach flavor,$(FLAVORS_PUBLIC_CLOUD), \
		printf "%-80s%s\n" "  $(flavor)-tofu-test-platform" "Run platform tests build with OpenTofu for $(flavor)"; \
	)

# help: all					Run all platform tests
all: test-platforms

### platform-specific targets
$(foreach flavor,$(FLAVORS_PUBLIC_CLOUD) $(FLAVORS_LOCAL), \
	$(eval \
	  $(flavor)-qemu-test-platform: ; \
		$(GARDENLINUX_BUILD_CRE) exec -it qemu-$(flavor) bash -c "\
			until test -f /tmp/qemu.pid; do echo 'Waiting for qemu to start...'; sleep 1; done && \
			./pytest.qemu.$(flavor).test.sh \
		" \
	) \
)

$(foreach flavor,$(FLAVORS_PUBLIC_CLOUD), \
	$(eval \
	  $(flavor)-tofu-test-platform: ; \
	  	$(CRE_CMD_tofu) pytest --iaas=manual --configfile=tests/config/pytest.manual.$(flavor).yaml --junit-xml=tests/$(flavor).platform.test.xml ; \
	) \
)
