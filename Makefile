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

$(SECUREBOOT_CRT): container-cert
	$(GARDENLINUX_BUILD_CRE) run --rm --volume '$(realpath $(dir $@)):/cert' 'gardenlinux/build-cert:$(VERSION)' make --directory=/cert default

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

all_prod: ali aws gcp azure metal openstack vmware kvm

all_dev: ali-dev aws-dev gcp-dev azure-dev metal-dev openstack-dev vmware-dev kvm-dev

ALI_IMAGE_NAME=$(IMAGE_BASENAME)-ali-$(VERSION)
ali: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,gardener,ali $(BUILDDIR) $(VERSION)

ali-upload:
	aliyun oss cp $(BUILDDIR)/ali-gardener-amd64-$(VERSION)-local/rootfs.qcow2  oss://gardenlinux-development/gardenlinux/$(ALI_IMAGE_NAME).qcow2

ALI_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-ali-$(VERSION)
ali-dev: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,gardener,ali,_dev $(BUILDDIR) $(VERSION)

ali-dev-upload:
	aliyun oss cp $(BUILDDIR)/ali-gardener_dev-amd64-$(VERSION)-local/rootfs.qcow2  oss://gardenlinux-development/gardenlinux/$(ALI_DEV_IMAGE_NAME).qcow2


AWS_IMAGE_NAME=$(IMAGE_BASENAME)-aws-$(VERSION)
aws: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,gardener,aws $(BUILDDIR) $(VERSION)

aws-upload:
	./bin/make-ec2-ami --bucket gardenlinux-testing --region eu-north-1 --image-name=$(AWS_IMAGE_NAME) $(BUILDDIR)/aws-gardener-amd64-$(VERSION)-local/rootfs.raw --permission-public "$(PUBLIC)" --distribute "$(AWS_DISTRIBUTE)"

AWS_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-aws-$(VERSION)
aws-dev: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,gardener,aws,_dev $(BUILDDIR) ${VERSION}

aws-dev-upload:
	./bin/make-ec2-ami --bucket ami-debian-image-test --region eu-north-1 --image-name=$(AWS_DEV_IMAGE_NAME) $(BUILDDIR)/aws-gardener_dev-amd64-$(VERSION)-local/rootfs.raw --permission-public "$(PUBLIC)" --distribute "$(AWS_DISTRIBUTE)"

GCP_IMAGE_NAME=$(IMAGE_BASENAME)-gcp-$(VERSION)
gcp: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,gardener,gcp $(BUILDDIR) $(VERSION)

gcp-upload:
	./bin/make-gcp-ami --bucket garden-linux-test --image-name $(GCP_IMAGE_NAME) --raw-image-path $(BUILDDIR)/gcp-gardener-amd64-$(VERSION)-local/rootfs-gcpimage.tar.gz --permission-public "$(PUBLIC)"

GCP_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-gcp-$(VERSION)
gcp-dev: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,gardener,gcp,_dev $(BUILDDIR) $(VERSION)

gcp-dev-upload:
	./bin/make-gcp-ami --bucket garden-linux-test --image-name $(GCP_DEV_IMAGE_NAME) --raw-image-path $(BUILDDIR)/gcp-gardener_dev-amd64-$(VERSION)-local/rootfs-gcpimage.tar.gz --permission-public "$(PUBLIC)"

AZURE_IMAGE_NAME=$(IMAGE_BASENAME)-az-$(VERSION)
azure: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,gardener,azure $(BUILDDIR) $(VERSION)

azure-upload:
	./bin/make-azure-ami --resource-group garden-linux --storage-account-name gardenlinux --image-path=$(BUILDDIR)/azure-gardener-amd64-$(VERSION)-local/rootfs.vhd --image-name=$(AZURE_IMAGE_NAME)

AZURE_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-az-$(VERSION)
azure-dev: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,gardener,azure,_dev $(BUILDDIR) $(VERSION)

azure-dev-upload:
	./bin/make-azure-ami --resource-group garden-linux --storage-account-name gardenlinuxdev --image-path=$(BUILDDIR)/azure-gardener_dev-amd64-$(VERSION)-local/rootfs.vhd --image-name=$(AZURE_DEV_IMAGE_NAME)


OPENSTACK_IMAGE_NAME=$(IMAGE_BASENAME)-openstack-$(VERSION)
openstack: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,gardener,openstack $(BUILDDIR) $(VERSION)

openstack-upload:
	./bin/upload-openstack $(BUILDDIR)/openstack-gardener-amd64-$(VERSION)-local/rootfs.vmdk $(OPENSTACK_IMAGE_NAME)

OPENSTACK_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-openstack-dev-$(VERSION)
openstack-dev: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,gardener,openstack,_dev $(BUILDDIR) $(VERSION)

openstack-dev-upload:
	./bin/upload-openstack $(BUILDDIR)/openstack-gardener_dev-amd64-$(VERSION)-local/rootfs.vmdk $(OPENSTACK_DEV_IMAGE_NAME)

openstack-qcow2: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --features server,cloud,gardener,openstack-qcow2 $(BUILDDIR) $(VERSION)

VMWARE_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-vmware-dev-$(VERSION)
vmware-dev: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,gardener,vmware,_dev $(BUILDDIR) $(VERSION)

VMWARE_VMOPERATOR_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-vmware-vmoperator-dev-$(VERSION)
vmware-vmoperator-dev: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,gardener,vmware-vmoperator,_dev $(BUILDDIR)/vmware-vmoperator-dev $(VERSION)

vmware: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,gardener,vmware $(BUILDDIR) $(VERSION)

cloud: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud $(BUILDDIR) $(VERSION)

kvm: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,kvm $(BUILDDIR) $(VERSION)

kvm-secureboot: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,kvm,_secureboot $(BUILDDIR) $(VERSION)

kvm-dev: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,kvm,_dev $(BUILDDIR) $(VERSION)

kvm-secureboot-dev: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,kvm,_secureboot,_dev $(BUILDDIR) $(VERSION)

firecracker: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features firecracker $(BUILDDIR) $(VERSION)

firecracker-dev: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features firecracker,_dev $(BUILDDIR) $(VERSION)

pxe: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features metal,server,_pxe $(BUILDDIR) $(VERSION)

pxe-dev: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features metal,server,_dev,_pxe $(BUILDDIR) $(VERSION)

metal-iso: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features metal,server,_iso $(BUILDDIR) $(VERSION)

anvil: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud-anvil,kvm,_dev $(BUILDDIR) $(VERSION)

onmetal: metal
metal: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,metal $(BUILDDIR) $(VERSION)

metal-dev: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,metal,_dev $(BUILDDIR) $(VERSION)

metalk: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features metal,khost,_pxe $(BUILDDIR) $(VERSION)

metalk-dev: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features metal,khost,_pxe,_dev $(BUILDDIR) $(VERSION)

metal-secureboot: build-environment $(SECUREBOOT_CRT) cert/sign.pub
	./build.sh $(BUILD_OPTS) --skip-build --features server,metal,_secureboot $(BUILDDIR) $(VERSION)

metal-secureboot-dev: build-environment $(SECUREBOOT_CRT) cert/sign.pub
	./build.sh $(BUILD_OPTS) --skip-build --features server,metal,_secureboot,_dev $(BUILDDIR) $(VERSION)

metalv: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,metal,vhost $(BUILDDIR) $(VERSION)

metalv-dev: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,metal,vhost,_dev $(BUILDDIR) $(VERSION)

github_action_runner: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,aws,github_action_runner $(BUILDDIR) $(VERSION)

github_action_runner-dev: build-environment $(SECUREBOOT_CRT)
	./build.sh $(BUILD_OPTS) --skip-build --features server,cloud,aws,github_action_runner,_dev $(BUILDDIR) $(VERSION)

clean:
	@echo "emptying $(BUILDDIR)"
	@rm -rf $(BUILDDIR)/*
	@echo "deleting all containers running gardenlinux/build-image"
	@-$(GARDENLINUX_BUILD_CRE) container rm $$($(GARDENLINUX_BUILD_CRE) container ls -a | awk '{ print $$1,$$2 }' | grep gardenlinux/build-image: | awk '{ print $$1 }') 2> /dev/null || true
	@echo "deleting all containers running gardenlinux/integration-test"
	@-$(GARDENLINUX_BUILD_CRE) container rm $$($(GARDENLINUX_BUILD_CRE) container ls -a | awk '{ print $$1,$$2 }' | grep gardenlinux/integration-test: | awk '{ print $$1 }') 2> /dev/null || true

distclean: clean
	make --directory=container clean
