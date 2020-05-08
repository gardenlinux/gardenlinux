#SNAPSHOT_DATE=`date -d 'today' '+%Y%m%d'`

# This is the snapshot date candidate for the first Garden Linux release
SNAPSHOT_DATE=20200427
IMAGE_BASENAME=garden-linux
VERSION=29-2
PUBLIC=true
AWS_DISTRIBUTE=

all: all_dev all_prod

all_prod: aws gcp azure openstack vmware kvm

all_dev: aws-dev gcp-dev azure-dev openstack-dev vmware-dev

AWS_IMAGE_NAME=$(IMAGE_BASENAME)-aws-$(VERSION)
aws:
	./build.sh --features server,cloud,gardener,aws .build/aws bullseye $(SNAPSHOT_DATE)

aws-upload:
	./bin/make-ec2-ami --bucket gardenlinux --region eu-central-1 --image-name=$(AWS_IMAGE_NAME) .build/aws/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs.raw --permission-public "$(PUBLIC)" --distribute "$(AWS_DISTRIBUTE)"

AWS_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-aws-$(VERSION)
aws-dev:
	./build.sh --features server,cloud,gardener,aws,_dev .build/aws-dev bullseye $(SNAPSHOT_DATE)

aws-dev-upload:
	./bin/make-ec2-ami --bucket ami-debian-image-test --region eu-central-1 --image-name=$(AWS_DEV_IMAGE_NAME) .build/aws-dev/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs.raw --permission-public "$(PUBLIC)" --distribute "$(AWS_DISTRIBUTE)"

GCP_IMAGE_NAME=$(IMAGE_BASENAME)-gcp-$(VERSION)
gcp:
	./build.sh --features server,cloud,gardener,gcp .build/gcp bullseye $(SNAPSHOT_DATE)

gcp-upload:
	./bin/make-gcp-ami --bucket gardenlinux-images --image-name $(GCP_IMAGE_NAME) --raw-image-path .build/gcp/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs-gcpimage.tar.gz --permission-public "$(PUBLIC)"

GCP_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-gcp-$(VERSION)
gcp-dev:
	./build.sh --features server,cloud,gardener,gcp,_dev .build/gcp-dev bullseye $(SNAPSHOT_DATE)

gcp-dev-upload:
	./bin/make-gcp-ami --bucket garden-linux-test --image-name $(GCP_DEV_IMAGE_NAME) --raw-image-path .build/gcp-dev/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs-gcpimage.tar.gz --permission-public "$(PUBLIC)"

AZURE_IMAGE_NAME=$(IMAGE_BASENAME)-az-$(VERSION)
azure:
	./build.sh --features server,cloud,gardener,azure .build/azure bullseye $(SNAPSHOT_DATE)

azure-upload:
	./bin/make-azure-ami --resource-group garden-linux --storage-account-name gardenlinux --image-path=.build/azure/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs.vhd --image-name=$(AZURE_IMAGE_NAME)

AZURE_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-dev-az-$(VERSION)
azure-dev:
	./build.sh --features server,cloud,gardener,azure,_dev .build/azure-dev bullseye $(SNAPSHOT_DATE)

azure-dev-upload:
	./bin/make-azure-ami --resource-group garden-linux --storage-account-name gardenlinux --image-path=.build/azure-dev/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs.vhd --image-name=$(AZURE_DEV_IMAGE_NAME)


OPENSTACK_IMAGE_NAME=$(IMAGE_BASENAME)-openstack-$(VERSION)
openstack:
	./build.sh --features server,cloud,gardener,openstack .build/openstack bullseye $(SNAPSHOT_DATE)

openstack-upload:
	./bin/upload-openstack .build/openstack/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs.vmdk $(OPENSTACK_IMAGE_NAME)

OPENSTACK_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-openstack-dev-$(VERSION)
openstack-dev:
	./build.sh --features server,cloud,gardener,openstack,_dev .build/openstack-dev bullseye $(SNAPSHOT_DATE)

openstack-dev-upload:
	./bin/upload-openstack .build/openstack-dev/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs.vmdk $(OPENSTACK_DEV_IMAGE_NAME)

VMWARE_DEV_IMAGE_NAME=$(IMAGE_BASENAME)-vmware-dev-$(VERSION)
vmware-dev:
	./build.sh --features server,cloud,gardener,vmware,_dev .build/vmware-dev bullseye $(SNAPSHOT_DATE)

vmware:
	./build.sh --features server,cloud,gardener,vmware .build/vmware bullseye $(SNAPSHOT_DATE)

cloud:
	./build.sh --features server,cloud .build/cloud bullseye $(SNAPSHOT_DATE)

kvm:
	./build.sh --features server,cloud,kvm,_dev .build/kvm bullseye $(SNAPSHOT_DATE)

onmetal:
	echo "TODO: implement"
	exit 1

clean:
	rm -rf .build
