---
title: "Test Framework Architecture"
description: Understanding the Garden Linux Test Framework Architecture
related_topics:
  - /contributing/testing.md
  - /explanation/testing/test-framework-architecture.md
  - /explanation/testing/test-organization.md
  - /how-to/testing/run-tests.md
  - /how-to/testing/setup-test-environment.md
  - /how-to/testing/debug-tests.md
  - /how-to/testing/test-in-cloud.md
  - /reference/testing/developing-tests.md
  - /reference/testing/test-coverage-markers.md
  - /reference/testing/test-cli.md
migration_status: "done"
migration_issue: https://github.com/gardenlinux/gardenlinux/issues/4748
migration_source: "tests/DEVELOPER.md, tests/README.md"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/explanation/testing/test-framework-architecture.md
github_target_path: "docs/explanation/testing/test-framework-architecture.md"
---

# Test Framework Architecture

This page explains the design and architecture of the Garden Linux test framework, including how tests, plugins, and handlers interact, and how the test distribution system works.

## Framework components

The Garden Linux test framework is built on pytest and uses a modular architecture with three main components, as defined in [ADR-0006](/reference/adr/0006-new-test-framework-in-place-self-contained-test-execution.md) and [ADR-0008](/reference/adr/0008-unified-and-declarative-test-logic.md):

### How tests, plugins, and handlers connect

The framework uses pytest's plugin system to automatically register fixtures:

1. **Plugins** (`tests/plugins/`) - Provide fixtures for system access
2. **Handlers** (`tests/handlers/`) - Provide fixtures for setup and teardown
3. **Tests** (`tests/integration/test_*.py`) - Use fixtures via dependency injection

**Registration**: All plugins are automatically registered as pytest fixtures via `conftest.py`.

## Directory structure

```
tests/
├── util/                   # Utility scripts for running tests
│   ├── run.sh              # Main entry point for running tests
│   ├── run_chroot.sh       # Chroot testing environment
│   ├── run_qemu.sh         # QEMU VM testing environment
│   ├── run_cloud.sh        # Cloud provider testing
│   ├── run_oci.sh          # OCI container testing
│   ├── login_qemu.sh       # SSH login to QEMU VM
│   ├── login_cloud.sh      # SSH login to cloud VM
│   └── tf/                 # Terraform configurations for cloud
├── plugins/                # Test plugins
│   └── ...
├── handlers/               # Test handlers
│   └── ...
├── integration/            # Directory for all tests and their categories
│   ├── boot/               # Boot category
│   │   └── test_*.py       # Individual tests
│   ├── core/               # Core category
│   │   └── test_*.py       # Individual tests
│   └── ...
```

## Plugins

Plugins are pytest fixtures that handle infrastructure concerns and system interactions.

**Purpose**: Provide clean Application Programming Interfaces (APIs) for system access (file parsing, service management, and similar tasks).

**Usage**: Provide pytest fixtures that can be injected into test functions.

**Examples**: `Systemd`, `Sshd`, `ShellRunner`, `KernelModule`

**Guideline**: Handle "how to access" not "what to test".

### Plugin design philosophy

Plugins focus on infrastructure concerns:

- File parsing and data access
- System service management
- Network connections and sockets
- Data processing and formatting

Plugins do not contain test logic or assertions. They provide the tools tests need to interact with the system under test.

## Handlers

Handlers are pytest fixtures that manage test setup and teardown.

**Purpose**: Setup and teardown of test state (connections, services, environments).

**Pattern**: Yield fixtures that prepare resources and explicitly clean up after tests.

**Usage**: Used as pytest fixtures with `yield` for cleanup.

**Examples**: `service_ssh`, `service_containerd`

**Key distinction**: Unlike regular fixtures that provide data, handlers manage stateful resources that need explicit cleanup.

### Handler responsibilities

Handlers must:

- Save the initial system state before making changes
- Yield to the test
- Restore the original state in the teardown phase
- Only restore what they changed
- Clean up in reverse order of setup (especially important for dependencies like kernel modules)

## Utility functions

Utility functions (`tests/plugins/utils.py`) provide reusable functionality.

**Purpose**: Helper functions not used directly in tests.

**Usage**: Used by plugins and handlers.

**Examples**: `equals_ignore_case`, `parse_etc_file`

These functions are building blocks for plugins and handlers, not directly accessible to tests.

## Test distribution system

The test framework is automatically built and packaged when running tests. The build process creates a self-contained distribution, as specified in [ADR-0006](/reference/adr/0006-new-test-framework-in-place-self-contained-test-execution.md), that includes the Python runtime, test framework, and all dependencies.

### Build components

The build system creates several artifacts:

- `.build/runtime.tar.gz` - Python runtime environment with dependencies
- `.build/dist.tar.gz` - Test framework and test files
- `.build/dist.ext2.raw` - Raw ext2 filesystem image for mounting in virtual machines (VMs)
- `.build/dist.ext2.raw.tar.gz` - Compressed tar file including `disk.raw` (Raw ext2 filesystem image to import to Google Cloud Platform (GCP))
- `.build/dist.vhd` - Virtual Hard Disk (VHD) filesystem image for import in Azure
- `.build/edk2-*` - EFI Development Kit II (EDK2) firmware files for QEMU boot

### Build process

The build system follows these steps:

1. **Runtime Environment** - Downloads standalone Python binaries for x86_64 and aarch64 architectures and installs required packages from `requirements.txt`
2. **Test Framework** - Bundles all test files, plugins, and the test runner script
3. **Distribution** - Creates both a compressed tar archive and an ext2 filesystem image
4. **Firmware** - Downloads EDK2 firmware files for QEMU virtualization

### Automatic building

The build process runs automatically when you execute `./test`:

```bash
# Build artifacts are created automatically
./test .build/image.raw

# Or build manually
cd tests
make -f util/build.makefile
```

### Distribution structure

The built distribution contains:

```
dist/
├── runtime/           # Python runtime and dependencies
│   ├── x86_64/        # x86_64 Python binaries
│   ├── aarch64/       # aarch64 Python binaries
│   └── site-packages/ # Python packages
├── tests/             # Test framework and test files
│   ├── plugins/       # Test plugins
│   ├── handlers/      # Test plugins
│   ├── test_*.py      # Individual test modules
│   └── conftest.py    # Pytest configuration
├── integration/       # Directory for all tests and their categories
│   ├── boot/          # Boot category
│   │   └── test_*.py  # Individual tests
│   ├── core/          # Core category
│   │   └── test_*.py  # Individual tests
│   └── ...
└── run_tests          # Test execution script
```

This self-contained distribution can be:

- Mounted directly in QEMU VMs
- Uploaded to cloud instances via SSH
- Extracted into chroot environments
- Run in OCI containers

The distribution approach ensures that:

- Tests run in a consistent Python environment across all platforms
- No dependencies on the host system's Python installation
- Tests can run on minimal systems without Python pre-installed
- The same test code runs identically across all test environments

## Design principles

The architecture follows these key principles, derived from [ADR-0006](/reference/adr/0006-new-test-framework-in-place-self-contained-test-execution.md), [ADR-0007](/reference/adr/0007-non-invasive-read-only-testing.md), and [ADR-0008](/reference/adr/0008-unified-and-declarative-test-logic.md):

1. **Separation of Concerns** - Tests contain assertions, plugins handle infrastructure, handlers manage state
2. **Dependency Injection** - Pytest's fixture system provides clean dependency management
3. **Self-Contained** - Distribution includes all dependencies (no host system requirements)
4. **Environment Agnostic** - Same tests run in chroot, QEMU, cloud, and OCI environments
5. **Extensible** - New plugins and handlers can be added without modifying the core framework
   [text](/how-to/releases/index.md)

## Related architecture decisions

The test framework architecture is based on several key decisions:

- [ADR-0006: New Test Framework](/reference/adr/0006-new-test-framework-in-place-self-contained-test-execution.md) - In-place, self-contained test execution
- [ADR-0007: Non-Invasive Testing](/reference/adr/0007-non-invasive-read-only-testing.md) - Read-only testing principles
- [ADR-0008: Unified Test Logic](/reference/adr/0008-unified-and-declarative-test-logic.md) - Declarative test design
- [ADR-0009: Flexible Distribution](/reference/adr/0009-flexible-distribution-and-reporting.md) - Distribution and reporting mechanisms
- [ADR-0010: Incremental Migration](/reference/adr/0010-incremental-migration-and-coexistence-of-tests.md) - Migration strategy
- [ADR-0016: Minimal Host Dependencies](/reference/adr/0016-minimal-host-dependencies-for-test-ng.md) - Reducing host requirements
- [ADR-0022: System State Diffing](/reference/adr/0022-test-ng-system-state-diffing.md) - Detecting system modifications

## Related topics

<RelatedTopics />
