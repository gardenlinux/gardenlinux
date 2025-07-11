# Garden Linux Tests-NG

This directory contains the next-generation testing framework for Garden Linux. It provides a modern, streamlined approach to testing Garden Linux images across different platforms and architectures.

## What is Tests-NG?

Tests-NG is a lightweight, portable testing framework that:

- **Bundles Python runtime and dependencies** into self-contained archives
- **Provides cross-architecture support** (x86_64 and aarch64)
- **Offers platform-agnostic testing** that works on chroot, containers, QEMU, cloud platforms, and bare metal
- **Uses pytest** as the underlying test framework for familiar syntax and powerful features
- **Implements content-based checksums** for reproducible builds and caching

## Directory Structure

```
tests-ng/
├── README.md             # This file
├── Makefile              # Build system
├── conftest.py           # Pytest configuration
├── test_*.py             # Individual test files
├── plugins/              # Pytest plugins
├── util/                 # Build utilities
│   ├── build_runtime.sh  # Runtime builder with caching
│   ├── build_dist.sh     # Distribution packager
│   └── requirements.txt  # Python dependencies
├── .build                # Built runtimes and distributables (gitignored)
│   ├── tests-ng-dist.tar.gz        # Symlink to checksummed distribution
│   ├── tests-ng-dist-{hash}.tar.gz # Checksummed distribution file
│   ├── checksum          # Content checksum of source files
│   └── runtime-*.tar.gz  # Runtime archive by arch
└── .cache/               # Cached runtime files (gitignored)
    └── runtime/
        └── runtime-*.tar.gz
```

## Usage

### Building the Distribution

```bash
# Build the tests-ng distribution
make --directory=tests-ng
```

This creates `.build/tests-ng-dist.tar.gz` containing:

- Python runtimes for supported architectures
- All test files and plugins
- Self-contained `run_tests` script

### Content-Based Checksums

The build system calculates a checksum based on all source files:

- Test files (`test_*.py`)
- Configuration (`conftest.py`, `Makefile`)
- Build utilities (`util/build_*.sh`, `util/requirements.txt`)
- Plugin files (`plugins/*.py`)

When source files change, a new checksum is generated and the distribution is rebuilt. This ensures:

- **Reproducible builds** - Same source always produces same checksum
- **Efficient caching** - Unchanged sources reuse existing distributions
- **Version tracking** - Each unique version has a unique identifier


Simply invoke this `podman` command:

```bash
podman run --rm -v "$PWD/.build/tests-ng-dist.tar.gz:/mnt/tests-ng-dist.tar.gz:ro" --read-only --tmpfs /opt/tests -w /opt/tests ghcr.io/gardenlinux/gardenlinux /bin/bash -c 'gzip -d < /mnt/tests-ng-dist.tar.gz | tar -x && ./run_tests'
```

### QEMU Platform Tests

Complete workflow for testing with QEMU:

```bash
# 1. Build the Garden Linux image
make kvm-gardener_prod-amd64-build

# 2. Start QEMU VM with the image
make --directory=tests/platformSetup kvm-gardener_prod-amd64-qemu-apply

# 3. Run tests-ng platform tests
make --directory=tests kvm-gardener_prod-amd64-qemu-test-ng-platform
```

### Cloud Platform Tests

#### Option 1: Build Your Own Image

```bash
# 1. Build the Garden Linux image for GCP
make gcp-gardener_prod-amd64-build

# 2. Configure cloud infrastructure
make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-config

# 3. Deploy to cloud platform
make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-apply

# 4. Run tests-ng platform tests
make --directory=tests gcp-gardener_prod-amd64-tofu-test-ng-platform
```

#### Option 2: Use Existing Cloud Image

```bash
# 1. Configure with existing image for GCP
IMAGE_PATH=cloud:// IMAGE_NAME=projects/sap-se-gcp-gardenlinux/global/images/gardenlinux-gcp-ff804026cbe7b5f2d6f729e4-1592-11-9ce205a2 \
  make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-config

# 2. Deploy to cloud platform
make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-apply

# 3. Run tests-ng platform tests
make --directory=tests gcp-gardener_prod-amd64-tofu-test-ng-platform
```
