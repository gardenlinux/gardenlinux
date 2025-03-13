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
KVM_DEVICE := $(shell if [ -e /dev/kvm ] && [ -w /dev/kvm ]; then echo "--device=/dev/kvm"; else echo ""; fi)

# Generate FLAVORS variable by running the flavor parser
FLAVORS_BARE := $(shell $(ROOT_DIR)/bin/flavors_parse.py --include-only "bare-*" --build --test)
FLAVORS_IMAGE := $(shell $(ROOT_DIR)/bin/flavors_parse.py --exclude "bare-*" --build --test)
FLAVORS_PUBLIC_CLOUD := $(shell $(ROOT_DIR)/bin/flavors_parse.py --category "public-cloud" --test)


CRE_CMD_BASE = $(GARDENLINUX_BUILD_CRE) run -it --rm -v $(ROOT_DIR):/gardenlinux
CRE_CMD_security = --cap-add SYS_ADMIN,MKNOD,AUDIT_WRITE,NET_RAW --security-opt apparmor=unconfined
CRE_CMD_privileged = --privileged
CRE_CMD_tofu = $(CRE_CMD_BASE) -v ~/.ssh:/root/.ssh:ro $(GL_REGISTRY)/gardenlinux/platform-test-tofu:$(GL_VERSION)

.PHONY: all
.DEFAULT: help

define chroot_test
$(1)-chroot-test:
	@echo "Running Chroot Test for flavor $(1)"
	cd $(ROOT_DIR) && ./test $(1)
endef

# # Extract ARCH from the flavor string (e.g., "bare-python-amd64" -> "amd64")
bare_get_arch = $(shell echo $(1) | grep -oE '(amd64|arm64)')
# 
# # Extract CONFIG from the flavor string (e.g., "bare-python-amd64" -> "python")
bare_get_config = $(shell echo $(1) | sed 's/^bare-//' | sed 's/-amd64//' | sed 's/-arm64//')

define container_test
$(1)-container-test:
	@echo "Running Container Test for bare flavor $(1)"
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

# help: help					List available tasks of the project
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "general targets:"
	@grep -E '^# help: ' $(MAKEFILE_LIST) | sed 's/^# help: //g' | awk 'BEGIN {FS = ": "}; {printf "%-80s %s\n", $$1, $$2}'
	@echo ""
	@echo "Available Chroot Test targets for Official Flavors:"
	@echo ""
	@echo "base Chroot tests targets:"
	@printf "%-80s%s\n" "  base-amd64-chroot-test" "Run bootstrap/base Chroot tests for amd64"
	@printf "%-80s%s\n" "  base-arm64-chroot-test" "Run bootstrap/base Chroot tests for arm64"
	@printf "%-80s%s\n" "  container-amd64-chroot-test" "Run base container Chroot tests for amd64"
	@printf "%-80s%s\n" "  container-arm64-chroot-test" "Run base container Chroot tests for arm64"
	@echo ""
	@echo "bare flavor Container tests targets:"
	@$(foreach flavor,$(FLAVORS_BARE), \
		printf "%-80s%s\n" "  $(flavor)-container-test" "Run Container tests $(flavor)"; \
	)
	@echo ""
	@echo "image flavor Chroot tests targets:"
	@$(foreach flavor,$(FLAVORS_IMAGE), \
		printf "%-80s%s\n" "  $(flavor)-chroot-test" "Run Chroot tests $(flavor)"; \
	)
	@echo ""
	@echo "Available Platform Test targets for Official Flavors:"
	@echo ""
	@echo "Qemu Provisioner Platform Tests targets:"
	@$(foreach flavor,$(FLAVORS_IMAGE), \
		printf "%-80s%s\n" "  $(flavor)-qemu-test-platform" "Run platform tests build with Qemu for $(flavor)"; \
	)
	@echo ""
	@echo "Tofu Provisioner Platform Tests targets:"
	@$(foreach flavor,$(FLAVORS_PUBLIC_CLOUD), \
		printf "%-80s%s\n" "  $(flavor)-tofu-test-platform" "Run platform tests build with OpenTofu for $(flavor)"; \
	)

# help: all					Run all platform tests
all: test-platforms

# Run Chroot tests for all flavors
all-chroot-test: $(addsuffix -chroot-test, $(FLAVORS_IMAGE))

# Run Container tests for all flavors
all-container-test: $(addsuffix -container-test, $(FLAVORS_BARE))

# Run Platform tests for all flavors with Qemu provisioner
all-qemu-test-platform: $(addsuffix -qemu-test-platform, $(FLAVORS_IMAGE))

# Run Platform tests for all flavors with OpenTofu provisioner
all-tofu-test-platform: $(addsuffix -tofu-test-platform, $(FLAVORS_PUBLIC_CLOUD))

# Generate rules dynamically for all bare flavors
$(foreach flavor, $(FLAVORS_BARE), $(eval $(call container_test, $(flavor))))

# Generate rules for base targets only
$(eval $(call chroot_test, base-amd64))
$(eval $(call chroot_test, base-arm64))

# Generate rules dynamically for all flavors
$(foreach flavor, $(FLAVORS_IMAGE), $(eval $(call chroot_test, $(flavor))))

### platform-specific targets
$(foreach flavor,$(FLAVORS_IMAGE), \
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
	  	$(CRE_CMD_tofu) pytest --provisioner=manual --configfile=/gardenlinux/tests/config/pytest.manual.$(flavor).yaml --junit-xml=/gardenlinux/tests/$(flavor).platform.test.xml ; \
	) \
)
