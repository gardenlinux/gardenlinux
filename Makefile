VERSION=$(shell bin/garden-version)
IMAGE_BASENAME=garden-linux
PUBLIC=true
AWS_DISTRIBUTE=
BUILDDIR=.build

ARCH ?= $(shell bin/get_arch.sh)
override BUILD_OPTS += --arch=$(ARCH)

ifneq ($(wildcard local_packages),)
LOCAL_PKGS=local_packages
endif

ifdef LOCAL_PKGS
$(info using local packages from $(LOCAL_PKGS))
override BUILD_OPTS += --local-pkgs=$(LOCAL_PKGS)
endif

GARDENLINUX_BUILD_CRE ?= sudo podman

.PHONY:all
all: all_dev all_prod

SECUREBOOT_CRT=cert/secureboot.db.auth

ifdef CERT_USE_KMS
CERT_CONTAINER_OPTS=$(shell env | grep '^AWS_' | sed 's/^/-e /')
CERT_MAKE_OPTS=USE_KMS=1
endif

$(SECUREBOOT_CRT): | container-cert
	$(GARDENLINUX_BUILD_CRE) run --rm --volume '$(realpath $(dir $@)):/cert' $(CERT_CONTAINER_OPTS) 'gardenlinux/build-cert:$(VERSION)' make --directory=/cert $(CERT_MAKE_OPTS) default

.PHONY: container-build container-cert container-test container-integration

container-build:
	make --directory=container build-image

container-cert:
	make --directory=container build-cert

container-test:
	make --directory=container build-base-test

container-integration:
	make --directory=container build-integration-test

build-environment: container-test container-build

all_prod: ali aws gcp azure metal openstack vmware kvm metalv

all_dev: ali-dev aws-dev gcp-dev azure-dev metal-dev openstack-dev vmware-dev kvm-dev metalv-dev

%: make_targets/% build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features "$$(cat $<)" $(BUILDDIR) $(VERSION)

%-dev: make_targets/% build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features "$$(cat $<),_dev" $(BUILDDIR) $(VERSION)

%-prod: make_targets/% build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features "$$(cat $<),_prod" $(BUILDDIR) $(VERSION)

onmetal: metal

ALI_IMAGE_NAME=$(IMAGE_BASENAME)-ali-$(VERSION)
ali-upload:
	aliyun oss cp $(BUILDDIR)/ali-gardener-amd64-$(VERSION)-local/rootfs.qcow2  oss://gardenlinux-development/gardenlinux/$(ALI_IMAGE_NAME).qcow2

ALI_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-ali-$(VERSION)
ali-dev-upload:
	aliyun oss cp $(BUILDDIR)/ali-gardener_dev-amd64-$(VERSION)-local/rootfs.qcow2  oss://gardenlinux-development/gardenlinux/$(ALI_DEV_IMAGE_NAME).qcow2

AWS_IMAGE_NAME=$(IMAGE_BASENAME)-aws-$(VERSION)
aws-upload:
	./bin/make-ec2-ami --bucket gardenlinux-testing --region eu-north-1 --image-name=$(AWS_IMAGE_NAME) $(BUILDDIR)/aws-gardener-amd64-$(VERSION)-local/rootfs.raw --permission-public "$(PUBLIC)" --distribute "$(AWS_DISTRIBUTE)"

AWS_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-aws-$(VERSION)
aws-dev-upload:
	./bin/make-ec2-ami --bucket ami-debian-image-test --region eu-north-1 --image-name=$(AWS_DEV_IMAGE_NAME) $(BUILDDIR)/aws-gardener_dev-amd64-$(VERSION)-local/rootfs.raw --permission-public "$(PUBLIC)" --distribute "$(AWS_DISTRIBUTE)"

GCP_IMAGE_NAME=$(IMAGE_BASENAME)-gcp-$(VERSION)
gcp-upload:
	./bin/make-gcp-ami --bucket garden-linux-test --image-name $(GCP_IMAGE_NAME) --raw-image-path $(BUILDDIR)/gcp-gardener-amd64-$(VERSION)-local/rootfs-gcpimage.tar.gz --permission-public "$(PUBLIC)"

GCP_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-gcp-$(VERSION)
gcp-dev-upload:
	./bin/make-gcp-ami --bucket garden-linux-test --image-name $(GCP_DEV_IMAGE_NAME) --raw-image-path $(BUILDDIR)/gcp-gardener_dev-amd64-$(VERSION)-local/rootfs-gcpimage.tar.gz --permission-public "$(PUBLIC)"

AZURE_IMAGE_NAME=$(IMAGE_BASENAME)-az-$(VERSION)
azure-upload:
	./bin/make-azure-ami --resource-group garden-linux --storage-account-name gardenlinux --image-path=$(BUILDDIR)/azure-gardener-amd64-$(VERSION)-local/rootfs.vhd --image-name=$(AZURE_IMAGE_NAME)

AZURE_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-az-$(VERSION)
azure-dev-upload:
	./bin/make-azure-ami --resource-group garden-linux --storage-account-name gardenlinuxdev --image-path=$(BUILDDIR)/azure-gardener_dev-amd64-$(VERSION)-local/rootfs.vhd --image-name=$(AZURE_DEV_IMAGE_NAME)

OPENSTACK_IMAGE_NAME=$(IMAGE_BASENAME)-openstack-$(VERSION)
openstack-upload:
	./bin/upload-openstack $(BUILDDIR)/openstack-gardener-amd64-$(VERSION)-local/rootfs.vmdk $(OPENSTACK_IMAGE_NAME)

OPENSTACK_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-openstack-dev-$(VERSION)
openstack-dev-upload:
	./bin/upload-openstack $(BUILDDIR)/openstack-gardener_dev-amd64-$(VERSION)-local/rootfs.vmdk $(OPENSTACK_DEV_IMAGE_NAME)

OPENSTACK_BM_IMAGE_NAME=$(IMAGE_BASENAME)-openstack-baremetal-$(VERSION)
openstack-bm-upload:
	./bin/upload-openstack $(BUILDDIR)/openstack-baremetal-gardener-amd64-$(VERSION)-local/rootfs.vmdk $(OPENSTACK_IMAGE_NAME)

OPENSTACK_BM_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-openstack-baremetal-dev-$(VERSION)
openstack-bm-dev-upload:
	./bin/upload-openstack $(BUILDDIR)/openstack-baremetal-gardener_dev-amd64-$(VERSION)-local/rootfs.vmdk $(OPENSTACK_DEV_IMAGE_NAME)

clean:
	@echo "emptying $(BUILDDIR)"
	@rm -rf $(BUILDDIR)/*
	@echo "deleting all containers running gardenlinux/build-image"
	@-$(GARDENLINUX_BUILD_CRE) container rm $$($(GARDENLINUX_BUILD_CRE) container ls -a | awk '{ print $$1,$$2 }' | grep gardenlinux/build-image: | awk '{ print $$1 }') 2> /dev/null || true
	@echo "deleting all containers running gardenlinux/integration-test"
	@-$(GARDENLINUX_BUILD_CRE) container rm $$($(GARDENLINUX_BUILD_CRE) container ls -a | awk '{ print $$1,$$2 }' | grep gardenlinux/integration-test: | awk '{ print $$1 }') 2> /dev/null || true

distclean: clean
	make --directory=container clean
