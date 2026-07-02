---
title: "Test Organization"
description: Understanding how Garden Linux tests are organized and structured
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
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/explanation/testing/test-organization.md
github_target_path: "docs/explanation/testing/test-organization.md"
---

# Test Organization

This page explains how Garden Linux tests are organized, structured, and named to improve maintainability and discoverability.

## Test Categorization

All test files are placed into `tests/integration/{category}`. The following tree structure shows how tests are organized by functional area:

```
tests/integration/
├── boot/                    # Boot-related tests (ignition, cloud-init, initrd, secureboot, etc.)
├── core/                    # Core system functionality (services, network, users, logging, etc.)
├── infrastructure/          # Infrastructure and platform tests (cloud platforms, iscsi, nvme, kvm, metal)
├── kernel/                  # Kernel-related tests (cmdline, modules, parameters, etc.)
├── runtime/                 # Runtime environment tests (containers, SAP, gardener, nodejs, etc.)
└── security/                # Security tests (SSH, firewall, PAM, capabilities, etc.)
    └── compliance/          # Compliance tests (CIS, FIPS, STIG, FedRAMP)
```

### Purpose of Categorization

The purpose of categorizing tests is to improve maintainability and discoverability, following [ADR-0008](/reference/adr/0008-unified-and-declarative-test-logic.md). By grouping related tests together, developers can more easily:

- Locate existing tests for a specific functional area
- Understand the scope and coverage of the test suite
- Organize test execution by category when needed
- Maintain consistency when adding new tests

These categories are subject to change as new tests are added and the test suite evolves.

### Category Descriptions

**boot/** - Tests related to system boot processes:

- Ignition configuration
- Cloud-init functionality
- Initial RAM disk (initrd) components
- Secure boot verification
- Boot sequence validation

**core/** - Tests for core system functionality:

- System services (enabled, disabled, running, stopped)
- Network configuration and connectivity
- User and group management
- System logging
- Basic system operations

**infrastructure/** - Tests for platform and infrastructure support:

- Cloud platform integrations (AWS, Azure, GCP, ALI, OpenStack)
- Storage technologies (iSCSI, NVMe)
- Virtualization (KVM, QEMU)
- Bare metal installations

**kernel/** - Tests related to the Linux kernel:

- Kernel command-line parameters
- Kernel modules
- Kernel parameters (sysctl)
- Kernel-level features

**runtime/** - Tests for runtime environments and applications:

- Container runtime (containerd, Docker)
- SAP-specific functionality
- Gardener integration
- Language runtimes (Node.js, Python)

**security/** - Security-related tests:

- SSH configuration and hardening
- Firewall rules
- Pluggable Authentication Modules (PAM) configuration
- Capabilities and permissions
- Compliance frameworks (CIS, Federal Information Processing Standard (FIPS), Security Technical Implementation Guide (STIG), Federal Risk and Authorization Management Program (FedRAMP))

## File Naming Convention

Test files follow the pattern `test_*.py` and should be named based on the functionality they test:

- `test_ignition.py` (in `boot/`) - Ignition configuration and functionality
- `test_services.py` (in `core/`) - Enabled, disabled, started, and stopped services
- `test_network.py` (in `core/`) - Network configuration and connectivity
- `test_ssh.py` (in `security/`) - SSH configuration and security
- `test_fips.py` (in `security/compliance/`) - FIPS compliance tests

The filename should clearly indicate what aspect of the system is being tested.

## Test Function Naming

Test functions should clearly describe what they verify by naming them accordingly and providing a useful comment:

```python
def test_sshd_has_required_config(sshd_config_item: str, sshd: Sshd):
    """Test that SSH daemon has the required configuration values."""

def test_users_have_no_authorized_keys(expected_users):
    """Test that unmanaged users don't have SSH authorized keys."""

def test_startup_time(systemd: Systemd):
    """Test that system startup time is within acceptable limits."""
```

### Naming Guidelines

- Use descriptive names that explain what breaks if the test fails
- Start with `test_` (pytest requirement)
- Use underscores to separate words (Python convention)
- Be specific about what is being tested
- Include a docstring that explains the test purpose

## Feature-Based Organization

Tests are organized by functionality rather than Garden Linux features. However, feature-specific tests use the `@pytest.mark.feature` marker to limit execution:

```python
@pytest.mark.feature("ssh")
def test_ssh_service_running(systemd: Systemd, service_ssh):
    assert systemd.is_active("ssh"), "SSH service is not running"
```

:::info
Tests are not strictly tied to features in the `features` folder. Use `@pytest.mark.feature()` if you need a test condition related to a feature.
:::

## Test Discovery

Pytest automatically discovers and runs tests based on naming conventions:

- Test files must be named `test_*.py` or `*_test.py`
- Test functions must be named `test_*`
- Test classes must be named `Test*`

The framework follows these conventions to ensure consistent test discovery across all environments.

## Organization Principles

The test organization follows these principles:

1. **Functional Grouping** - Tests are grouped by what they test, not by the feature that provides the functionality
2. **Clear Hierarchy** - Categories provide logical grouping without deep nesting
3. **Descriptive Names** - File and function names clearly indicate their purpose
4. **Flexible Structure** - Categories can evolve as new tests are added
5. **Discovery-Friendly** - Naming conventions support automatic test discovery

## Evolution and Maintenance

The test organization is not fixed. As the test suite grows:

- New categories may be added
- Tests may be reorganized for better clarity
- Subcategories may be created when a category becomes too large
- Naming conventions may be refined

The goal is always to make tests easy to find and understand.

## Related Architecture Decisions

Test organization is guided by:

- [ADR-0008: Unified Test Logic](/reference/adr/0008-unified-and-declarative-test-logic.md) - Declarative test organization
- [ADR-0010: Incremental Migration](/reference/adr/0010-incremental-migration-and-coexistence-of-tests.md) - Migration and coexistence strategy

## Related Topics

<RelatedTopics />
