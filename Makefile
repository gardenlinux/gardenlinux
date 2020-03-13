all:
	./build.sh --features full ../full bullseye now

azure:
	./build.sh --features server,cloud,azure ../azure bullseye now

cloud:
	./build.sh --features server,cloud ../cloud bullseye now
	
kvm:
	./build.sh --features server,kvm ../kvm bullseye now
