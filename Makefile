SNAPSHOT_DATE=`date -d 'today' '+%Y%m%d'`
IMAGE_BASENAME=garden-linux
VERSION=17

all: all_dev all_prod

all_prod: aws gcp azure openstack vmware kvm

all_dev: aws-dev gcp-dev azure-dev openstack-dev vmware-dev

AWS_IMAGE_NAME=$(IMAGE_BASENAME)-aws-$(VERSION)
aws:
	./build.sh --features server,cloud,ghost,aws .build/aws bullseye $(SNAPSHOT_DATE)

aws-upload:
	./scripts/make-ec2-ami --bucket ami-debian-image-test --region eu-central-1 --image-name=$(AWS_IMAGE_NAME) .build/aws/aws.raw

AWS_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-aws-$(VERSION)
aws-dev:
	./build.sh --features server,cloud,ghost,aws,dev .build/aws-dev bullseye $(SNAPSHOT_DATE)

aws-dev-upload:
	./scripts/make-ec2-ami --bucket ami-debian-image-test --region eu-central-1 --image-name=$(AWS_DEV_IMAGE_NAME) .build/aws-dev/aws-dev.raw

AWS_CHOST_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-chost-dev-aws-$(VERSION)
aws-chost-dev:
	./build.sh --features server,cloud,chost,aws,dev .build/aws-chost-dev bullseye $(SNAPSHOT_DATE)

aws-chost-dev-upload:
	./scripts/make-ec2-ami --bucket ami-debian-image-test --region eu-central-1 --image-name=$(AWS_CHOST_DEV_IMAGE_NAME) .build/aws-chost-dev/aws-chost-dev.raw


GCP_IMAGE_NAME=$(IMAGE_BASENAME)-gcp-$(VERSION)
gcp:
	./build.sh --features server,cloud,ghost,gcp .build/gcp bullseye $(SNAPSHOT_DATE)

gcp-upload:
	./scripts/make-gcp-ami --bucket garden-linux-test --image-name $(GCP_IMAGE_NAME) --raw-image-path .build/gcp/$(GCP_IMAGE_NAME).tar.gz

GCP_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-gcp-$(VERSION)
gcp-dev:
	./build.sh --features server,cloud,ghost,gcp,dev .build/gcp-dev bullseye $(SNAPSHOT_DATE)

gcp-dev-upload:
	./scripts/make-gcp-ami --bucket garden-linux-test --image-name $(GCP_DEV_IMAGE_NAME) --raw-image-path .build/gcp-dev/$(GCP_DEV_IMAGE_NAME).tar.gz

AZURE_IMAGE_NAME=$(IMAGE_BASENAME)-az-$(VERSION)
azure:
	./build.sh --features server,cloud,ghost,azure .build/azure-dev bullseye $(SNAPSHOT_DATE)

azure-upload:
	./scripts/make-azure-ami --resource-group garden-linux --storage-account-name gardenlinux --image-path=.build/azure/$(AZURE_IMAGE_NAME).vhd --image-name=$(AZURE_IMAGE_NAME)

AZURE_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-az-$(VERSION)
azure-dev:
	./build.sh --features server,cloud,ghost,azure,dev .build/azure-dev bullseye $(SNAPSHOT_DATE)

azure-dev-upload:
	./scripts/make-azure-ami --resource-group garden-linux --storage-account-name gardenlinux --image-path=.build/azure-dev/$(AZURE_DEV_IMAGE_NAME).vhd --image-name=$(AZURE_DEV_IMAGE_NAME)


OPENSTACK_IMAGE_NAME=$(IMAGE_BASENAME)-openstack-$(VERSION)
openstack:
	./build.sh --features server,cloud,ghost,openstack .build/openstack-dev bullseye $(SNAPSHOT_DATE)

OPENSTACK_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-openstack-dev-$(VERSION)
openstack-dev:
	./build.sh --features server,cloud,ghost,openstack,dev .build/openstack-dev bullseye $(SNAPSHOT_DATE)

openstack-dev-upload:
	./scripts/upload-openstack .build/openstack-dev/$(OPENSTACK_DEV_IMAGE_NAME).vmdk $(OPENSTACK_DEV_IMAGE_NAME)

VMWARE_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-vmware-dev-$(VERSION)
vmware-dev:
	./build.sh --features server,cloud,ghost,vmware,dev .build/vmware-dev bullseye $(SNAPSHOT_DATE)

vmware:
	./build.sh --features server,cloud,ghost,vmware .build/vmware bullseye $(SNAPSHOT_DATE)

cloud:
	./build.sh --features server,cloud .build/cloud bullseye $(SNAPSHOT_DATE)

kvm:
	./build.sh --features server,kvm,dev .build/kvm bullseye $(SNAPSHOT_DATE)

onmetal:
	echo "TODO: implement"
	exit 1

clean:
	rm -rf .build
