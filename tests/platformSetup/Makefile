SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c

ROOT_DIR := $(shell git rev-parse --show-toplevel)
UUID_FILE := $(ROOT_DIR)/tests/platformSetup/.uuid
# Check if the .uuid file exists. If it does, read from it, otherwise generate a new uuid/seed
ifeq ($(wildcard $(UUID_FILE)),)
	UUID := $(shell cat /proc/sys/kernel/random/uuid)
    $(shell echo $(UUID) > $(UUID_FILE))
else
    UUID := $(shell cat $(UUID_FILE))
endif
SEED := $(shell cat $(UUID_FILE) | cut -d'-' -f1)
ifeq ($(strip $(GL_VERSION)),)
GL_VERSION := latest
endif
ifeq ($(origin GL_REGISTRY), undefined)
GL_REGISTRY := ghcr.io/gardenlinux
endif

GARDENLINUX_BUILD_CRE ?= podman

# Generate FLAVORS variable by running the flavor parser
FLAVORS := $(shell $(ROOT_DIR)/bin/flavors_parse.py --category "public-cloud" --test-platform)

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
	@echo "Available targets for Official Flavors:"
	@echo ""
	@$(foreach flavor,$(FLAVORS), \
		echo "$(flavor)-plan        Run tofu plan for $(flavor)"; \
		echo "$(flavor)-apply       Run tofu apply for $(flavor)"; \
		echo "$(flavor)-show        Run tofu show for $(flavor)"; \
		echo "$(flavor)-login       Run tofu login for $(flavor)"; \
		echo "$(flavor)-destroy     Run tofu destroy for $(flavor)"; \
	)

# flavor-specific targets
$(foreach flavor,$(FLAVORS), \
	$(eval \
		$(flavor)-plan: ; \
		mkdir -p $(MKDIRS) && \
		$(CRE_CMD_tofu) bash -c "\
			cd platformSetup/tofu && \
			tofu init && \
			tofu workspace select -or-create $(flavor)-$(SEED) && \
			tofu plan -var-file variables.$(flavor).tfvars && \
			tofu workspace select default" \
	) \
	$(eval \
		$(flavor)-apply: ; \
		mkdir -p $(MKDIRS) && \
		$(CRE_CMD_tofu) bash -c "\
			cd platformSetup/tofu && \
			tofu init && \
			tofu workspace select -or-create $(flavor)-$(SEED) && \
			tofu apply --auto-approve -var-file variables.$(flavor).tfvars && \
			./tf_pytest_ssh.py $(flavor) && \
			tofu workspace select default" \
	) \
	$(eval \
		$(flavor)-show: ; \
		mkdir -p $(MKDIRS) && \
		$(CRE_CMD_tofu) bash -c "\
			cd platformSetup/tofu && \
			tofu init && \
			tofu workspace select -or-create $(flavor)-$(SEED) && \
			tofu show && \
			tofu workspace select default" \
	) \
	$(eval \
		$(flavor)-login: ; \
		mkdir -p $(MKDIRS) && \
		$(CRE_CMD_tofu) bash -c "\
			cd platformSetup/tofu && \
			tofu init && \
			tofu workspace select -or-create $(flavor)-$(SEED) && \
			./tf_pytest_ssh.py $(flavor) && \
			tofu workspace select default && \
			./login.$(flavor).sh" \
	) \
	$(eval \
		$(flavor)-destroy: ; \
		mkdir -p $(MKDIRS) && \
		$(CRE_CMD_tofu) bash -c "\
			cd platformSetup/tofu && \
			tofu init && \
			tofu workspace select $(flavor)-$(SEED) && \
			tofu destroy --auto-approve -var-file variables.$(flavor).tfvars && \
			tofu workspace select default && \
			tofu workspace delete $(flavor)-$(SEED)" \
	) \
)
