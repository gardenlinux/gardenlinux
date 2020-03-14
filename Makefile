SNAPSHOT_DATE=`date -d 'yesterday' '+%Y%m%d'`

all: aws gcp azure openstack vmware kvm

aws:
	./build.sh --features server,cloud,aws,dev ../aws bullseye $(SNAPSHOT_DATE)
	./makef.sh --grub-target bios --fs-check-off ../aws/aws ../aws/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs.tar.xz

gcp:
	./build.sh --features server,cloud,gcp ../gcp bullseye $(SNAPSHOT_DATE)

azure:
	./build.sh --features server,cloud,azure ../azure bullseye $(SNAPSHOT_DATE)

openstack:
	./build.sh --features server,cloud,openstack ../openstack bullseye $(SNAPSHOT_DATE)

# Needs conversion to vmdk as the last step!
vmware:
	./build.sh --features server,cloud,vmware ../vmware bullseye $(SNAPSHOT_DATE)

cloud:
	./build.sh --features server,cloud ../cloud bullseye $(SNAPSHOT_DATE)
	
kvm:
	./build.sh --features server,kvm,dev ../kvm bullseye $(SNAPSHOT_DATE)
	./makef.sh ../kvm-server ../kvm/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs.tar.xz

onmetal:
	echo "TODO: implement"
	exit 1
