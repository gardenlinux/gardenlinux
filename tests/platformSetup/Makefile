SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c

ROOT_DIR := $(shell git rev-parse --show-toplevel)
#GIT_SHA := $(shell git rev-parse HEAD)
#GIT_SHA_SHORT := $(shell git rev-parse --short HEAD)
#GIT_BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
#GIT_BRANCH_SAFE := $(shell git rev-parse --abbrev-ref HEAD | tr -cs 'a-zA-Z0-9._-' '-' | sed 's/-$$//')
UUID_FILE := $(ROOT_DIR)/tests/platformSetup/.uuid
# Check if the .uuid file exists. If it does, read from it, otherwise generate a new uuid/seed
ifeq ($(wildcard $(UUID_FILE)),)
	UUID := $(shell cat /proc/sys/kernel/random/uuid)
    $(shell echo $(UUID) > $(UUID_FILE))
else
    UUID := $(shell cat $(UUID_FILE))
endif
SEED := $(shell cat $(UUID_FILE) | cut -d'-' -f1)
# ifeq ($(or $(strip $(GL_VERSION)), $(GL_VERSION)), latest)
ifeq ($(strip $(GL_VERSION)),)
GL_VERSION := latest
endif
ifeq ($(origin GL_REGISTRY), undefined)
GL_REGISTRY := ghcr.io/gardenlinux
endif

GARDENLINUX_BUILD_CRE ?= podman

# PLATFORMS_LOCAL = firecracker kvm
PLATFORMS_CLOUD = ali aws azure gcp
ARCHS = amd64 arm64
FLAVORS = default trustedboot trustedboot_tpm2

# Exclusions as a list of "platform-arch-flavor"
EXCLUDES := ali-amd64-trustedboot \
			ali-amd64-trustedboot_tpm2 \
			ali-arm64-default \
            ali-arm64-trustedboot \
            ali-arm64-trustedboot_tpm2 \
            azure-arm64-trustedboot \
            azure-arm64-trustedboot_tpm2

CRE_CMD_BASE = $(GARDENLINUX_BUILD_CRE) run -it --rm -v $(ROOT_DIR):/gardenlinux -e TF_* -v ~/.aliyun:/root/.aliyun -e ALIBABA_* -v ~/.aws:/root/.aws -e AWS_* -v ~/.azure:/root/.azure -e azure_* -e ARM_* -e ACTIONS_* -v ~/.config/gcloud:/root/.config/gcloud -e GOOGLE_* -e CLOUDSDK_* 
CRE_CMD_security = --cap-add SYS_ADMIN,MKNOD,AUDIT_WRITE,NET_RAW --security-opt apparmor=unconfined
#CRE_CMD_priviliged = --privileged
CRE_CMD_tofu = $(CRE_CMD_BASE) -v ~/.ssh:/root/.ssh:ro $(GL_REGISTRY)/gardenlinux/platform-test-tofu:$(GL_VERSION)
MKDIRS = ~/.aliyun ~/.aws ~/.azure ~/.config/gcloud

.PHONY: all
.DEFAULT: help

is_excluded = $(filter $(1),$(EXCLUDES))

# help: help					List available tasks of the project
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "general targets:"
	@grep -E '^# help: ' $(MAKEFILE_LIST) | sed 's/^# help: //g' | awk 'BEGIN {FS = ": "}; {printf "%-40s %s\n", $$1, $$2}'
	@echo ""
	@echo "platform-specific targets:"
	@$(foreach platform,$(PLATFORMS_CLOUD), \
		$(foreach arch,$(ARCHS), \
			$(foreach flavor,$(FLAVORS), \
				$(if $(call is_excluded,$(platform)-$(arch)-$(flavor)),, \
					echo "$(platform)-$(arch)-$(flavor)-plan        Run tofu plan for $(platform) $(arch) $(flavor)"; \
					echo "$(platform)-$(arch)-$(flavor)-apply       Run tofu apply for $(platform) $(arch) $(flavor)"; \
					echo "$(platform)-$(arch)-$(flavor)-show        Run tofu show for $(platform) $(arch) $(flavor)"; \
					echo "$(platform)-$(arch)-$(flavor)-login       Run tofu login for $(platform) $(arch) $(flavor)"; \
					echo "$(platform)-$(arch)-$(flavor)-destroy     Run tofu destroy for $(platform) $(arch) $(flavor)"; \
				) \
			) \
		) \
	)

### help: all					Run all platform tests
### all: apply-platforms

# Platform-specific targets for PLATFORMS_CLOUD
$(foreach platform,$(PLATFORMS_CLOUD), \
	$(foreach arch,$(ARCHS), \
		$(foreach flavor,$(FLAVORS), \
			$(if $(call is_excluded,$(platform)-$(arch)-$(flavor)),, \
    			$(eval \
    				$(platform)-$(arch)-$(flavor)-plan: ; \
					mkdir -p $(MKDIRS) && \
    				$(CRE_CMD_tofu) bash -c "\
    					cd platformSetup/tofu && \
    					tofu init && \
    					tofu workspace select -or-create $(platform)-$(arch)-$(flavor)-$(SEED) && \
    					tofu plan -var-file variables.$(platform).$(arch).$(flavor).tfvars && \
    					tofu workspace select default" \
    			) \
    			$(eval \
    				$(platform)-$(arch)-$(flavor)-apply: ; \
					mkdir -p $(MKDIRS) && \
    				$(CRE_CMD_tofu) bash -c "\
    					cd platformSetup/tofu && \
    					tofu init && \
    					tofu workspace select -or-create $(platform)-$(arch)-$(flavor)-$(SEED) && \
    					tofu apply --auto-approve -var-file variables.$(platform).$(arch).$(flavor).tfvars && \
    					./env_create.sh $(platform) $(arch) $(flavor) && \
    					./pytest_config_create.sh $(platform) $(arch) $(flavor) && \
    					tofu workspace select default" \
    			) \
    			$(eval \
    				$(platform)-$(arch)-$(flavor)-show: ; \
					mkdir -p $(MKDIRS) && \
    				$(CRE_CMD_tofu) bash -c "\
    					cd platformSetup/tofu && \
    					tofu init && \
    					tofu workspace select -or-create $(platform)-$(arch)-$(flavor)-$(SEED) && \
    					tofu show && \
    					tofu workspace select default" \
    			) \
    			$(eval \
    				$(platform)-$(arch)-$(flavor)-login: ; \
					mkdir -p $(MKDIRS) && \
    				$(CRE_CMD_tofu) bash -c "\
    					cd platformSetup/tofu && \
    					tofu init && \
    					tofu workspace select -or-create $(platform)-$(arch)-$(flavor)-$(SEED) && \
    					./env_create.sh $(platform) $(arch) $(flavor) && \
    					tofu workspace select default && \
    					./login.$(platform).$(arch).$(flavor).sh" \
    			) \
    			$(eval \
    				$(platform)-$(arch)-$(flavor)-destroy: ; \
					mkdir -p $(MKDIRS) && \
    				$(CRE_CMD_tofu) bash -c "\
    					cd platformSetup/tofu && \
    					tofu init && \
    					tofu workspace select $(platform)-$(arch)-$(flavor)-$(SEED) && \
    					tofu destroy --auto-approve -var-file variables.$(platform).$(arch).$(flavor).tfvars && \
    					tofu workspace select default && \
    					tofu workspace delete $(platform)-$(arch)-$(flavor)-$(SEED)" \
    			) \
    		) \
    	) \
	) \
)
