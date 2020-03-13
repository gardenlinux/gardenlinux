all:
	./build.sh --features server,cloud,azure azure bullseye now

azure:
	./build.sh --features server,cloud,azure azure bullseye now

cloud:
	./build.sh --features server,cloud,cloud cloud bullseye now
