SNAPSHOT_DATE=`date -d 'yesterday' '+%Y%m%d'`

all:
	echo "Building Garden Linux 11-$(SNAPSHOT_DATE).0"
	./build.sh --features full ../full bullseye $(SNAPSHOT_DATE)

aws:
#	./build.sh --features server,cloud,aws,dev ../aws bullseye now
	./makef.sh --grub-target bios --fs-check-off ../aws/aws ../aws/20200314/amd64/bullseye/rootfs.tar.xz

gcp:
	./build.sh --features server,cloud,gcp ../gcp bullseye now

azure:
	./build.sh --features server,cloud,azure ../azure bullseye now

openstack:
	./build.sh --features server,cloud,openstack ../openstack bullseye now

# Needs conversion to vmdk as the last step!
vmware:
	./build.sh --features server,cloud,vmware ../vmware bullseye now

cloud:
	./build.sh --features server,cloud ../cloud bullseye now
	
kvm:
	./build.sh --features server,kvm,dev ../kvm bullseye now
	./makef.sh ../kvm-server ../kvm/20200314/amd64/bullseye/rootfs.tar.xz
