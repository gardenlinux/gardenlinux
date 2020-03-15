SNAPSHOT_DATE=`date -d 'today' '+%Y%m%d'`

all: aws gcp azure openstack vmware kvm

aws:
	./build.sh --features server,cloud,ghost,aws,dev .build/aws bullseye $(SNAPSHOT_DATE)
	./scripts/makef.sh --grub-target bios --fs-check-off .build/aws/aws .build/aws/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs.tar.xz

gcp:
	./build.sh --features server,cloud,ghost,gcp .build/gcp bullseye $(SNAPSHOT_DATE)
	./scripts/makef.sh --grub-target bios --fs-check-off .build/gcp/gcp .build/gcp/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs.tar.xz

azure:
	./build.sh --features server,cloud,azure .build/azure bullseye $(SNAPSHOT_DATE)

openstack:
	./build.sh --features server,cloud,openstack .build/openstack bullseye $(SNAPSHOT_DATE)

# Needs conversion to vmdk as the last step!
vmware:
	./build.sh --features server,cloud,vmware .build/vmware bullseye $(SNAPSHOT_DATE)

cloud:
	./build.sh --features server,cloud .build/cloud bullseye $(SNAPSHOT_DATE)
	
kvm:
	rm -f .build/kvm/kvm.raw 
	./build.sh --features server,kvm,chost,dev .build/kvm bullseye $(SNAPSHOT_DATE)
	./scripts/makef.sh .build/kvm/kvm .build/kvm/$(SNAPSHOT_DATE)/amd64/bullseye/rootfs.tar.xz

onmetal:
	echo "TODO: implement"
	exit 1

clean:
	rm -rf .build
