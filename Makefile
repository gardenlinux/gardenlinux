SNAPSHOT_DATE=`date -d 'today' '+%Y%m%d'`
IMAGE_BASENAME=garden-linux
VERSION=40-2
PUBLIC=

all: all_dev all_prod

all_prod: aws gcp azure openstack vmware kvm

all_dev: aws-dev gcp-dev azure-dev openstack-dev vmware-dev

AWS_IMAGE_NAME=$(IMAGE_BASENAME)-aws-$(VERSION)
aws:
	./build.sh --features server,cloud,gardener,aws .build/aws bullseye $(SNAPSHOT_DATE)

aws-upload:
	./bin/make-ec2-ami --bucket ami-debian-image-test --region eu-central-1 --image-name=$(AWS_IMAGE_NAME) .build/aws/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs.raw

AWS_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-aws-$(VERSION)
aws-dev:
	./build.sh --features server,cloud,gardener,aws,dev .build/aws-dev bullseye $(SNAPSHOT_DATE)

aws-dev-upload:
	./bin/make-ec2-ami --bucket ami-debian-image-test --region eu-central-1 --image-name=$(AWS_DEV_IMAGE_NAME) .build/aws-dev/aws-dev.raw

GCP_IMAGE_NAME=$(IMAGE_BASENAME)-gcp-$(VERSION)
gcp:
	./build.sh --features server,cloud,gardener,gcp .build/gcp bullseye $(SNAPSHOT_DATE)

gcp-upload:
	./bin/make-gcp-ami --bucket garden-linux-test --image-name $(GCP_IMAGE_NAME) --raw-image-path .build/gcp/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs-gcpimage.tar.gz --permission-public "$(PUBLIC)"

GCP_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-gcp-$(VERSION)
gcp-dev:
	./build.sh --features server,cloud,gardener,gcp,dev .build/gcp-dev bullseye $(SNAPSHOT_DATE)

gcp-dev-upload:
	./bin/make-gcp-ami --bucket garden-linux-test --image-name $(GCP_DEV_IMAGE_NAME) --raw-image-path .build/gcp-dev/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs-gcpimage.tar.gz --permission-public "$(PUBLIC)"

AZURE_IMAGE_NAME=$(IMAGE_BASENAME)-az-$(VERSION)
azure:
	./build.sh --features server,cloud,gardener,azure .build/azure-dev bullseye $(SNAPSHOT_DATE)

azure-upload:
	./bin/make-azure-ami --resource-group garden-linux --storage-account-name gardenlinux --image-path=.build/azure/$(AZURE_IMAGE_NAME).vhd --image-name=$(AZURE_IMAGE_NAME)

AZURE_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-az-$(VERSION)
azure-dev:
	./build.sh --features server,cloud,gardener,azure,dev .build/azure-dev bullseye $(SNAPSHOT_DATE)

azure-dev-upload:
	./bin/make-azure-ami --resource-group garden-linux --storage-account-name gardenlinux --image-path=.build/azure-dev/$(AZURE_DEV_IMAGE_NAME).vhd --image-name=$(AZURE_DEV_IMAGE_NAME)


OPENSTACK_IMAGE_NAME=$(IMAGE_BASENAME)-openstack-$(VERSION)
openstack:
	./build.sh --features server,cloud,gardener,openstack .build/openstack-dev bullseye $(SNAPSHOT_DATE)

OPENSTACK_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-openstack-dev-$(VERSION)
openstack-dev:
	./build.sh --features server,cloud,gardener,openstack,dev .build/openstack-dev bullseye $(SNAPSHOT_DATE)

openstack-dev-upload:
	./bin/upload-openstack .build/openstack-dev/$(OPENSTACK_DEV_IMAGE_NAME).vmdk $(OPENSTACK_DEV_IMAGE_NAME)

VMWARE_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-vmware-dev-$(VERSION)
vmware-dev:
	./build.sh --features server,cloud,gardener,vmware,dev .build/vmware-dev bullseye $(SNAPSHOT_DATE)

vmware:
	./build.sh --features server,cloud,gardener,vmware .build/vmware bullseye $(SNAPSHOT_DATE)

cloud:
	./build.sh --features server,cloud .build/cloud bullseye $(SNAPSHOT_DATE)

kvm:
	./build.sh --features server,cloud,kvm,dev .build/kvm bullseye $(SNAPSHOT_DATE)

onmetal:
	echo "TODO: implement"
	exit 1

clean:
	rm -rf .build
