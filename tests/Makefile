SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c

ROOT_DIR := $(shell git rev-parse --show-toplevel)
#GIT_SHA := $(shell git rev-parse HEAD)
#GIT_SHA_SHORT := $(shell git rev-parse --short HEAD)
#ifeq ($(origin GL_VERSION), undefined)
#GL_VERSION := $(shell $(ROOT_DIR)/bin/glrd --no-header --type patch --latest --fields Version)
ifeq ($(strip $(GL_VERSION)),)
GL_VERSION := latest
endif
ifeq ($(origin GL_REGISTRY), undefined)
GL_REGISTRY := ghcr.io/gardenlinux
endif
GL_IMAGE := $(GL_REGISTRY)/gardenlinux/platform-test-kvm:$(GL_VERSION)

GARDENLINUX_BUILD_CRE ?= podman

PLATFORMS_LOCAL = chroot kvm firecracker
PLATFORMS_CLOUD = ali aws azure gcp
ARCHS = amd64 arm64
FLAVORS = default trustedboot trustedboot_tpm2

# Exclusions as a list of "platform-arch-flavor"
EXCLUDES := chroot-amd64-trustedboot \
			chroot-amd64-trustedboot_tpm2 \
			chroot-arm64-trustedboot \
			chroot-arm64-trustedboot_tpm2 \
			firecracker-amd64-trustedboot \
			firecracker-amd64-trustedboot_tpm2 \
			firecracker-arm64-trustedboot \
			firecracker-arm64-trustedboot_tpm2 \
			ali-amd64-trustedboot \
			ali-amd64-trustedboot_tpm2 \
			ali-arm64-default \
            ali-arm64-trustedboot \
            ali-arm64-trustedboot_tpm2 \
            azure-arm64-trustedboot \
            azure-arm64-trustedboot_tpm2

CRE_CMD_BASE = $(GARDENLINUX_BUILD_CRE) run -it --rm -v $(ROOT_DIR):/gardenlinux
CRE_CMD_security = --cap-add SYS_ADMIN,MKNOD,AUDIT_WRITE,NET_RAW --security-opt apparmor=unconfined
CRE_CMD_priviliged = --privileged
CRE_CMD_tofu = $(CRE_CMD_BASE) -v ~/.ssh:/root/.ssh:ro $(GL_REGISTRY)/gardenlinux/platform-test-tofu:$(GL_VERSION)
CRE_CMD_chroot = $(CRE_CMD_BASE) $(CRE_CMD_security) $(GL_REGISTRY)/gardenlinux/platform-test-kvm:$(GL_VERSION)
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
	@$(foreach platform,$(PLATFORMS_LOCAL), \
  		$(foreach arch,$(ARCHS), \
			$(foreach flavor,$(FLAVORS), \
				$(if $(call is_excluded,$(platform)-$(arch)-$(flavor)),, \
					printf "%-60s%s\n" "$(platform)-$(arch)-$(flavor)-test-platform" "Run platform tests via opentofu for $(platform) on $(arch) $(flavor)"; \
				) \
			) \
		) \
	)
	@$(foreach platform,$(PLATFORMS_CLOUD), \
  		$(foreach arch,$(ARCHS),\
			$(foreach flavor,$(FLAVORS), \
				$(if $(call is_excluded,$(platform)-$(arch)-$(flavor)),, \
					printf "%-60s%s\n" "$(platform)-$(arch)-$(flavor)-test-platform" "Run platform tests via opentofu for $(platform) on $(arch) $(flavor)"; \
				) \
			) \
		) \
	)

# help: all					Run all platform tests
all: test-platforms

### platform-specific targets
$(foreach platform,$(PLATFORMS_LOCAL),\
  $(foreach arch,$(ARCHS), \
	$(foreach flavor,$(FLAVORS), \
		$(if $(call is_excluded,$(platform)-$(arch)-$(flavor)),, \
  			$(eval \
  			  $(platform)-$(arch)-$(flavor)-test-platform: ; \
				  test -f $(ROOT_DIR)/tests/config/$(platform).$(arch).$(flavor).yaml || cp $(ROOT_DIR)/tests/config/$(platform).$(arch).$(flavor).yaml.example $(ROOT_DIR)/tests/config/$(platform).$(arch).$(flavor).yaml ; \
			      $(CRE_CMD_$(platform)) bash -c "pytest --iaas=$(platform) --configfile=/gardenlinux/tests/config/$(platform).$(arch).$(flavor).yaml --junit-xml=/gardenlinux/tests/$(platform).$(arch).$(flavor).platform.test.xml" ; \
  			) \
  		) \
  	) \
  ) \
)

$(foreach platform,$(PLATFORMS_CLOUD),\
  $(foreach arch,$(ARCHS),\
	$(foreach flavor,$(FLAVORS), \
		$(if $(call is_excluded,$(platform)-$(arch)-$(flavor)),, \
			$(eval \
			  $(platform)-$(arch)-$(flavor)-test-platform: ; \
			  	$(CRE_CMD_tofu) pytest --iaas=manual --configfile=/gardenlinux/tests/config/manual_$(platform).$(arch).$(flavor).yaml --junit-xml=/gardenlinux/tests/$(platform).$(arch).$(flavor).platform.test.xml ; \
			) \
		) \
	) \
  ) \
)

