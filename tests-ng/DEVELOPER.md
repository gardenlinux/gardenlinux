# Garden Linux Tests Next Generation - Developer Guide

This document provides comprehensive guidelines for developing and maintaining tests in the Garden Linux tests-ng framework.

## Table of Contents

- [Test Development Principles](#test-development-principles)
- [Test Organization and Naming](#test-organization-and-naming)
- [Test Writing Best Practices](#test-writing-best-practices)
- [Framework Structure](#framework-structure)
- [Markers and Test Configuration](#markers-and-test-configuration)
- [Python Best Practices](#python-best-practices)
- [External Dependencies](#external-dependencies)
- [Resources](#resources)

## Test Development Principles

The following principles guide all test development in Garden Linux:

### Core Principles

- **Be easy to read and understand** without extensive knowledge of Garden Linux internals

  - Use native Python APIs over shell scripts where feasible
  - Write clear, self-documenting test names and assertions
  - Avoid complex logic in test functions

- **Be explicit about what quality they ensure**

  - Test names must clearly communicate what is broken if the test fails
  - In general, one test should not have multiple assertions (there might be valid exceptions)
  - Each test should verify a single, specific behavior

- **Be very strict about declaring if they mutate system state**

  - Use appropriate markers (`@pytest.mark.modify`, `@pytest.mark.root`) to declare system modifications
  - Document (`reason=`) why system modifications are necessary
  - Ensure tests clean up after themselves.
    - If new functionality is added, check if `tests-ng/plugins/sysdiff.py` collects modifications.

- **Only run as root when needed**

  - Use `@pytest.mark.root` only when root privileges are absolutely necessary
  - Document (`reason=`) why root access is required
  - Prefer unprivileged testing when possible

- **Only require a booted system when needed**

  - Use `@pytest.mark.booted` only when a running system is required
  - Document why a booted system is necessary
  - Prefer chroot testing for filesystem-only tests

- **Use abstractions to hide implementation details**

  - Leverage plugins to abstract system interactions
  - Use handlers for setup/teardown operations
  - Keep utility functions separate from test logic

- **Be mindful about external dependencies**
  - Prefer Python standard library over third-party packages
  - Only add PyPI dependencies when there's clear benefit
  - Document why external dependencies are necessary

## Test Organization and Naming

### File Naming Convention

Test files follow the pattern `test_*.py` and should be named based on the functionality they test:

- `test_ssh.py` - SSH configuration and functionality
- `test_packages.py` - Package installation and configuration
- `test_network.py` - Network configuration and connectivity

> [!NOTE]
> Tests are not strictly tied to features in the `features` folder anymore. Have a look at `@pytest.mark.feature()` if you need a test condition related to a feature.

### Test Function Naming and Comments

Test functions should clearly describe what they verify by naming them accordingly and providing a useful comment:

```python
def test_sshd_has_required_config(sshd_config_item: str, sshd: Sshd):
    """Test that SSH daemon has the required configuration values."""

def test_users_have_no_authorized_keys(expected_users):
    """Test that unmanaged users don't have SSH authorized keys."""

def test_startup_time(systemd: Systemd):
    """Test that system startup time is within acceptable limits."""
```

### Feature-Based Organization

Tests are organized by functionality rather than Garden Linux features. However, feature-specific tests use the `@pytest.mark.feature` marker to limit execution:

```python
@pytest.mark.feature("ssh")
def test_ssh_service_running(systemd: Systemd, service_ssh):
    assert systemd.is_active("ssh"), "SSH service is not running"
```

## Test Writing Best Practices

### Assertions Only in Test Code

Test functions should contain only assertions and minimal logic:

```python
# Good: Clear assertion with descriptive message
def test_sshd_config(sshd: Sshd):
    actual_value = sshd.get_config_section("PermitRootLogin")
    assert actual_value == "No", f"PermitRootLogin should be 'No', got '{actual_value}'"

# Bad: Complex logic in test
def test_sshd_config(sshd: Sshd):
    config = sshd.get_all_config()
    for key, value in config.items():
        if key == "PermitRootLogin":
            if value != "No":
                raise AssertionError(f"Expected No, got {value}")
            break
```

### Use Reusable Plugins

Plugins provide abstractions for system interactions:

```python
# Good: Using plugin abstraction
def test_service_running(systemd: Systemd):
    assert systemd.is_active("ssh"), "SSH service is not running"

# Bad: Direct shell calls
def test_service_running(shell: ShellRunner):
    result = shell("systemctl is-active ssh")
    assert result.stdout.strip() == "active", "SSH service is not running"
```

### Handlers for Setup/Teardown

Use handlers for managing test state and cleanup:

```python
@pytest.fixture
def service_ssh(systemd: Systemd):
    """Fixture for SSH service management."""
    service_active_initially = systemd.is_active("ssh")

    if not service_active_initially:
        systemd.start_unit("ssh")

    yield "ssh"

    if not service_active_initially:
        systemd.stop_unit("ssh")
```

### Utils for Helper Functions

Utility functions should not be used directly in tests but provide reusable functionality:

```python
# In plugins/utils.py
def equals_ignore_case(a: str, b: str) -> bool:
    return a.casefold() == b.casefold()

# In test files - use through plugins
def test_config_value(sshd: Sshd):
    actual_value = sshd.get_config_section("LogLevel")
    assert equals_ignore_case(actual_value, "VERBOSE"), f"Expected VERBOSE, got {actual_value}"
```

### Shell Calls vs Filesystem Lookups

Prefer filesystem lookups over shell calls when possible:

```python
# Good: Direct filesystem access
def test_os_release():
    with open("/etc/os-release", "r") as f:
        content = f.read()
        assert "ID=gardenlinux" in content

# Acceptable: Shell call when filesystem access is complex
def test_service_status(systemd: Systemd):
    assert systemd.is_active("ssh"), "SSH service is not running"
```

## Framework Structure

### Plugins (`tests-ng/plugins/`)

Plugins provide abstractions for system interactions:

- **Purpose**: Hide implementation details and provide clean APIs
- **Usage**: Imported and used directly in tests
- **Examples**: `Systemd`, `Sshd`, `ShellRunner`, `KernelModule`

```python
# Example plugin usage
def test_systemd_unit(systemd: Systemd):
    assert systemd.is_active("ssh"), "SSH service is not running"
```

### Handlers (`tests-ng/handlers/`)

Handlers manage test setup and teardown:

- **Purpose**: Setup/teardown of test state
- **Usage**: Used as pytest fixtures
- **Examples**: `service_ssh`, `service_containerd`

```python
# Example handler usage
@pytest.fixture
def service_ssh(systemd: Systemd):
    yield from handle_service(systemd, "ssh")
```

### Utils (`tests-ng/plugins/utils.py`)

Utility functions provide reusable functionality:

- **Purpose**: Helper functions not used directly in tests
- **Usage**: Used by plugins and handlers
- **Examples**: `equals_ignore_case`, `parse_etc_file`

```python
# Example utility usage in plugin
def get_config_section(self, section: str):
    # Uses utils internally
    return parse_etc_file(self.config_path, [section])
```

## Markers and Test Configuration

### Core Markers

#### `@pytest.mark.booted(reason="...")`

Indicates the test requires a booted system:

```python
@pytest.mark.booted(reason="Calling sshd -T requires a booted system")
def test_sshd_config(sshd: Sshd):
    # Test implementation
```

#### `@pytest.mark.modify(reason="...")`

Indicates the test modifies system state:

```python
@pytest.mark.modify(reason="Starting the unit modifies the system state")
def test_service_start(systemd: Systemd):
    # Test implementation
```

#### `@pytest.mark.root(reason="...")`

Indicates the test requires root privileges:

```python
@pytest.mark.root(reason="Starting the unit requires root")
def test_service_start(systemd: Systemd):
    # Test implementation
```

#### `@pytest.mark.feature("condition", reason="...")`

Limits test execution based on feature conditions:

```python
@pytest.mark.feature("ssh and not (ali or aws or azure or openstack)",
                     reason="We want no authorized_keys for unmanaged users")
def test_users_have_no_authorized_keys(expected_users):
    # Test implementation
```

#### `@pytest.mark.performance_metric`

Marks performance tests that can be skipped under emulation:

```python
@pytest.mark.performance_metric
@pytest.mark.booted(reason="We can only measure startup time if we actually boot the system")
def test_startup_time(systemd: Systemd):
    # Test implementation
```

### Parametrization

Use `@pytest.mark.parametrize` for testing multiple scenarios:

```python
@pytest.mark.parametrize("sshd_config_item", required_sshd_config)
def test_sshd_has_required_config(sshd_config_item: str, sshd: Sshd):
    actual_value = sshd.get_config_section(sshd_config_item)
    expected_value = required_sshd_config[sshd_config_item]
    # Test implementation
```

### Missing Markers (TODO)

#### `@pytest.mark.security_id`

TODO: Explain what this marker is good for.

## Python Best Practices

### Code Style

- Follow [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- Use type hints for function parameters and return values
- Prefer descriptive variable names
- Use docstrings for complex functions

### Error Handling

- Use descriptive assertion messages
- Handle expected failures gracefully
- Use appropriate exception types

```python
def test_config_file_exists():
    config_path = Path("/etc/ssh/sshd_config")
    assert config_path.exists(), f"SSH config file not found: {config_path}"
```

### Imports

- Group imports: standard library, third-party, local
- Use specific imports when possible
- Avoid wildcard imports

```python
import difflib
import gzip
import json
import os
import re
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pytest
from debian import deb822

from .dpkg import Dpkg
from .kernel_module import KernelModule, LoadedKernelModule
from .shell import ShellRunner
from .sysctl import Sysctl, SysctlParam
from .systemd import Systemd, SystemdUnit
```

## External Dependencies

### Policy

- **Prefer Python standard library** over third-party packages
- **Only add PyPI dependencies** when there's clear benefit
- **Document why** external dependencies are necessary
- **Consider maintenance cost** of external dependencies

### Current Dependencies

See `tests-ng/util/requirements.txt` for current dependencies. Each dependency should be justified.

### Adding New Dependencies

When adding new dependencies:

1. **Justify the need** - Why can't the standard library solve this?
2. **Document the benefit** - What does this library provide?
3. **Consider alternatives** - Are there lighter alternatives?
4. **Update requirements.txt** - Include version constraints

## Resources

- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://docs.python.org/3/library/unittest.html)
- [Garden Linux Tests-NG README](./README.md) - For usage and running tests

