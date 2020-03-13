all:
	./build.sh --features full ../full bullseye now


aws:
	./build.sh --features server,cloud,aws ../aws bullseye now

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
	./build.sh --features server,kvm ../kvm bullseye now
	./makef.sh ../kvm-server ../kvm/20200313/amd64/bullseye/rootfs.tar.xz
