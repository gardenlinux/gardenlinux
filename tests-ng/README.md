# Garden Linux Tests-NG

This directory contains the next-generation testing framework for Garden Linux. It provides a modern, streamlined approach to testing Garden Linux images across different platforms and architectures.

## What is Tests-NG?

Tests-NG is a lightweight, portable testing framework that:

- **Bundles Python runtime and dependencies** into self-contained archives
- **Provides cross-architecture support** (x86_64 and aarch64)
- **Offers platform-agnostic testing** that works on chroot, containers, QEMU, cloud platforms, and bare metal
- **Uses pytest** as the underlying test framework for familiar syntax and powerful features

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

### Container Platform Tests

Simply invoke this `podman` command:

```bash
podman run --rm -v "$PWD/.build/tests-ng-dist.tar.gz:/mnt/tests-ng-dist.tar.gz:ro" --read-only --tmpfs /opt/tests -w /opt/tests ghcr.io/gardenlinux/gardenlinux /bin/bash -c 'gzip -d < /mnt/tests-ng-dist.tar.gz | tar -x && ./run_tests'
```

