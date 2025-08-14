SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c

# get git root - if running as git submodule, return parent project root
ROOT_DIR := $(shell git rev-parse --show-toplevel --show-superproject-working-tree | tail -n1)
UUID_FILE := $(ROOT_DIR)/tests/platformSetup/.uuid
# Check if the .uuid file exists. If it does, read from it, otherwise generate a new uuid/seed
ifeq ($(wildcard $(UUID_FILE)),)
	UUID := $(shell uuidgen | tr A-F a-f)
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
ifeq ($(origin TEST_PREFIX), undefined)
TEST_PREFIX := $(shell echo $(USER) | cut -c1-10)
endif
ifeq ($(origin IMAGE_PATH), undefined)
IMAGE_PATH_CMD :=
else
IMAGE_PATH_CMD := --image-path $(IMAGE_PATH)
endif
ifeq ($(origin IMAGE_NAME), undefined)
IMAGE_NAME_CMD :=
else
IMAGE_NAME_CMD := --image-name $(IMAGE_NAME)
endif

GARDENLINUX_BUILD_CRE ?= podman
KVM_DEVICE := $(shell if [ -e /dev/kvm ] && [ -w /dev/kvm ]; then echo "--device=/dev/kvm"; else echo ""; fi)

# OpenTofu provider dummy variable initialization
ifeq ($(origin OS_CLOUD), undefined)
ifeq ($(origin OS_AUTH_URL), undefined)
OS_AUTH_URL := http://localhost:3000
endif
endif
ifeq ($(origin TF_VAR_gcp_project_id), undefined)
TF_VAR_gcp_project_id := dummy-gcp-project-id
endif
ifeq ($(origin ARM_SUBSCRIPTION_ID), undefined)
ARM_SUBSCRIPTION_ID := xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
endif

# Generate FLAVORS variable by running the flavor parser
FLAVORS_IMAGE := $(shell $(ROOT_DIR)/bin/flavors_parse.py --exclude "bare-*" --build)
FLAVORS_PUBLIC_CLOUD := $(shell $(ROOT_DIR)/bin/flavors_parse.py --include-only "ali-*" --include-only "aws-*" --include-only "azure-*" --include-only "gcp-*" --include-only "openstack-*")

CRE_CMD_BASE = $(GARDENLINUX_BUILD_CRE) run -it -v $(ROOT_DIR):/gardenlinux
CRE_CMD_security = --cap-add SYS_ADMIN,MKNOD,AUDIT_WRITE,NET_RAW --security-opt apparmor=unconfined
CRE_CMD_privileged = --privileged
# privileged is required for virt-copy-in/guestfish
CRE_CMD_kvm = $(CRE_CMD_BASE) $(CRE_CMD_privileged) $(KVM_DEVICE)
CRE_CMD_kvm_image = $(GL_REGISTRY)/gardenlinux/platform-test-kvm:$(GL_VERSION)
CRE_CMD_tofu = $(CRE_CMD_BASE) -e TF_* -e TOFU_* -e TOFUENV_* -v ~/.aliyun:/root/.aliyun -e ALIBABA_* -v ~/.aws:/root/.aws -e AWS_* -v ~/.azure:/root/.azure -e azure_* -e ARM_* -e ACTIONS_* -v ~/.config/gcloud:/root/.config/gcloud -e GOOGLE_* -e CLOUDSDK_* -e OS_* --rm -v ~/.ssh:/root/.ssh:ro $(GL_REGISTRY)/gardenlinux/platform-test-tofu:$(GL_VERSION)
MKDIRS = ~/.aliyun ~/.aws ~/.azure ~/.config/gcloud

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
	@echo "Available Resource Provisioning targets for Official Flavors:"
	@echo ""
	@echo "Qemu Provisioner Provisioning targets:"
	@$(foreach flavor,$(FLAVORS_IMAGE), \
		printf "%-80s%s\n" "  $(flavor)-qemu-apply" "Create qemu resources for $(flavor)"; \
		printf "%-80s%s\n" "  $(flavor)-qemu-login" "Login to qemu $(flavor)"; \
		printf "%-80s%s\n" "  $(flavor)-qemu-destroy" "Destroy qemu resources for $(flavor)"; \
	)
	@echo ""
	@echo "Tofu Provisioner Provisioning targets:"
	@$(foreach flavor,$(FLAVORS_PUBLIC_CLOUD), \
		printf "%-80s%s\n" "  $(flavor)-tofu-config" "Create tofu config for $(flavor)"; \
		printf "%-80s%s\n" "  $(flavor)-tofu-plan" "Run tofu plan for $(flavor)"; \
		printf "%-80s%s\n" "  $(flavor)-tofu-apply" "Run tofu apply for $(flavor)"; \
		printf "%-80s%s\n" "  $(flavor)-tofu-show" "Run tofu show for $(flavor)"; \
		printf "%-80s%s\n" "  $(flavor)-tofu-login" "Run tofu login for $(flavor)"; \
		printf "%-80s%s\n" "  $(flavor)-tofu-destroy" "Run tofu destroy for $(flavor)"; \
	)

# flavor-specific targets - public cloud
$(foreach flavor,$(FLAVORS_PUBLIC_CLOUD), \
	$(eval \
		$(flavor)-tofu-config: ; \
		export OS_AUTH_URL=$(OS_AUTH_URL) TF_VAR_gcp_project_id=$(TF_VAR_gcp_project_id) ARM_SUBSCRIPTION_ID=$(ARM_SUBSCRIPTION_ID) && \
		mkdir -p $(MKDIRS) && \
		$(CRE_CMD_tofu) bash -c "\
			cd platformSetup/tofu && \
			../platformSetup.py --provisioner tofu --flavor $(flavor) $(IMAGE_PATH_CMD) $(IMAGE_NAME_CMD) --test-prefix $(TEST_PREFIX) --create-tfvars" \
	) \
	$(eval \
		$(flavor)-tofu-plan: ; \
		export OS_AUTH_URL=$(OS_AUTH_URL) TF_VAR_gcp_project_id=$(TF_VAR_gcp_project_id) ARM_SUBSCRIPTION_ID=$(ARM_SUBSCRIPTION_ID) && \
		mkdir -p $(MKDIRS) && \
		$(CRE_CMD_tofu) bash -c "\
			cd platformSetup/tofu && \
			tofu init && \
			tofu workspace select -or-create $(flavor)-$(SEED) && \
			tofu plan -var-file variables.$(flavor).tfvars && \
			tofu workspace select default" \
	) \
	$(eval \
		$(flavor)-tofu-apply: ; \
		export OS_AUTH_URL=$(OS_AUTH_URL) TF_VAR_gcp_project_id=$(TF_VAR_gcp_project_id) ARM_SUBSCRIPTION_ID=$(ARM_SUBSCRIPTION_ID) && \
		mkdir -p $(MKDIRS) && \
		$(CRE_CMD_tofu) bash -c "\
			cd platformSetup/tofu && \
			test -f cert/secureboot.db.der || CERT_CN=OpenTofu make --directory=cert && \
			tofu init && \
			tofu workspace select -or-create $(flavor)-$(SEED) && \
			tofu apply --auto-approve -var-file variables.$(flavor).tfvars && \
			../platformSetup.py --provisioner tofu --flavor $(flavor) && \
			tofu workspace select default" \
	) \
	$(eval \
		$(flavor)-tofu-show: ; \
		export OS_AUTH_URL=$(OS_AUTH_URL) TF_VAR_gcp_project_id=$(TF_VAR_gcp_project_id) ARM_SUBSCRIPTION_ID=$(ARM_SUBSCRIPTION_ID) && \
		mkdir -p $(MKDIRS) && \
		$(CRE_CMD_tofu) bash -c "\
			cd platformSetup/tofu && \
			tofu init && \
			tofu workspace select -or-create $(flavor)-$(SEED) && \
			tofu show && \
			tofu workspace select default" \
	) \
	$(eval \
		$(flavor)-tofu-login: ; \
		export OS_AUTH_URL=$(OS_AUTH_URL) TF_VAR_gcp_project_id=$(TF_VAR_gcp_project_id) ARM_SUBSCRIPTION_ID=$(ARM_SUBSCRIPTION_ID) && \
		mkdir -p $(MKDIRS) && \
		$(CRE_CMD_tofu) bash -c "\
			cd platformSetup/tofu && \
			tofu init && \
			tofu workspace select -or-create $(flavor)-$(SEED) && \
			../platformSetup.py --provisioner tofu --flavor $(flavor) && \
			tofu workspace select default && \
			../../login.tofu.$(flavor).sh" \
	) \
	$(eval \
		$(flavor)-tofu-destroy: ; \
		export OS_AUTH_URL=$(OS_AUTH_URL) TF_VAR_gcp_project_id=$(TF_VAR_gcp_project_id) ARM_SUBSCRIPTION_ID=$(ARM_SUBSCRIPTION_ID) && \
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

# flavor-specific targets - local
$(foreach flavor,$(FLAVORS_IMAGE), \
	$(eval \
		$(flavor)-qemu-apply: ; \
		mkdir -p $(MKDIRS) && \
		$(CRE_CMD_kvm) --name qemu-$(flavor) -d --replace $(CRE_CMD_kvm_image) bash -c "\
			/gardenlinux/tests/platformSetup/platformSetup.py --provisioner qemu --flavor $(flavor) $(IMAGE_NAME_CMD) && \
			/gardenlinux/tests/pytest.qemu.$(flavor).apply.sh && \
			sleep 86400 \
		" && \
		$(GARDENLINUX_BUILD_CRE) exec -it qemu-$(flavor) bash -c "\
			until test -f /tmp/qemu.pid; do echo 'Waiting for qemu to start...'; sleep 1; done && \
			/gardenlinux/tests/pytest.qemu.$(flavor).apply.sh \
		" \
	) \
	$(eval \
		$(flavor)-qemu-login: ; \
		$(GARDENLINUX_BUILD_CRE) exec -it qemu-$(flavor) bash -c "\
			/gardenlinux/tests/login.qemu.$(flavor).sh \
		" \
	) \
	$(eval \
		$(flavor)-qemu-destroy: ; \
		$(GARDENLINUX_BUILD_CRE) rm -f qemu-$(flavor) \
	) \
)
