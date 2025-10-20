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

- **Use abstractions judiciously to hide implementation details**

  - Leverage plugins for infrastructure concerns (parsing files, accessing data, establishing connections)
  - Use handlers for setup/teardown operations
  - Keep test logic visible and maintain Arrange-Act-Assert structure
  - Avoid over-abstraction that requires reading multiple plugins to understand a test

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

### Use Plugins for Infrastructure, Not Test Logic

The key is finding the right balance between abstraction and readability. Plugins should handle infrastructure concerns, not hide test logic:

**Good abstractions** (infrastructure concerns):

- File parsing and data access
- System service management
- Network connections and sockets
- Data processing and formatting

**Avoid over-abstraction** (test logic concerns):

- Business logic validation
- Test-specific assertions
- Domain-specific checks
- Complex test workflows

```python
# Good: Plugin handles system interaction, test logic is clear
def test_service_running(systemd: Systemd):
    assert systemd.is_active("ssh"), "SSH service is not running"

# Good: Clear test logic with infrastructure abstraction
def test_sshd_permit_root_login(sshd: Sshd):
    """Test that SSH root login is disabled."""
    actual_value = sshd.get_config_section("PermitRootLogin")
    assert actual_value == "No", f"Root login should be disabled, got '{actual_value}'"

# Bad: Over-abstraction hiding test logic
def test_ssh_security_compliance(ssh_security: SshSecurity):
    """Test SSH security compliance."""
    assert ssh_security.is_secure(), "SSH configuration is not secure"

# Bad: Direct shell calls when plugin abstraction exists (or could be useful)
def test_service_running(shell: ShellRunner):
    result = shell("systemctl is-active ssh")
    assert result.stdout.strip() == "active", "SSH service is not running"
```

### Handlers for Setup/Teardown

Use handlers (yield fixtures) for managing test state and cleanup:

```python
@pytest.fixture
def service_ssh(systemd: Systemd):
    """Fixture for SSH service management with cleanup."""
    service_active_initially = systemd.is_active("ssh")

    if not service_active_initially:
        systemd.start_unit("ssh")

    yield "ssh"  # This returns "ssh" to the test as the fixture's value. This can be use to parametrize tests.

    # Cleanup: restore original state
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

Prefer filesystem lookups over shell calls when possible. Use shell calls only when:

1. **Testing shell functionality itself** (command execution, shell features)
2. **No appropriate plugin abstraction exists** and/or filesystem access is very complex
3. **Testing system-level behavior** that requires shell execution

```python
# Good: Direct filesystem access
def test_os_release():
    with open("/etc/os-release", "r") as f:
        content = f.read()
        assert "ID=gardenlinux" in content

# Good: Plugin abstraction for system interactions
def test_service_status(systemd: Systemd):
    assert systemd.is_active("ssh"), "SSH service is not running"

# Acceptable: Shell call when testing shell functionality
def test_shell_command_execution(shell: ShellRunner):
    """Test that shell commands execute correctly."""
    from datetime import datetime
    result = shell("date +%Y")
    current_year = str(datetime.now().year)
    assert result.stdout.strip() == current_year, f"Shell command execution failed, expected {current_year}"

# Bad: Shell call when plugin abstraction exists
def test_service_status(shell: ShellRunner):
    result = shell("systemctl is-active ssh")
    assert result.stdout.strip() == "active", "SSH service is not running"
```

## Framework Structure

### How Tests, Plugins, and Handlers Connect

The framework uses pytest's plugin system to automatically register fixtures:

1. **Plugins** (`tests-ng/plugins/`) - Provide fixtures for system access
2. **Handlers** (`tests-ng/handlers/`) - Provide fixtures for setup/teardown
3. **Tests** (`tests-ng/test_*.py`) - Use fixtures via dependency injection

**Registration**: All plugins are automatically registered as pytest fixtures via `conftest.py`

### Plugins (`tests-ng/plugins/`)

Plugins handle infrastructure concerns and system interactions:

- **Purpose**: Provide clean APIs for system access (file parsing, service management, etc.)
- **Usage**: Provide pytest fixtures that can be injected into test functions
- **Examples**: `Systemd`, `Sshd`, `ShellRunner`, `KernelModule`
- **Guideline**: Handle "how to access" not "what to test"

```python
# Example plugin usage - fixtures injected into test functions
def test_systemd_unit(systemd: Systemd):
    assert systemd.is_active("ssh"), "SSH service is not running"

def test_ssh_config(sshd: Sshd):
    config_value = sshd.get_config_section("PermitRootLogin")
    assert config_value == "No", f"Expected 'No', got '{config_value}'"
```

### Handlers (`tests-ng/handlers/`)

Handlers are pytest fixtures that manage test setup and teardown:

- **Purpose**: Setup/teardown of test state (connections, services, environments)
- **Pattern**: Yield fixtures that prepare resources and explicitly clean up after tests
- **Usage**: Used as pytest fixtures with `yield` for cleanup
- **Examples**: `service_ssh`, `service_containerd`

**Key distinction**: Unlike regular fixtures that provide data, handlers manage stateful resources that need explicit cleanup.

```python
# Example handler usage - setup/teardown pattern
@pytest.fixture
def service_ssh(systemd: Systemd):
    """Fixture for SSH service management with cleanup."""
    service_active_initially = systemd.is_active("ssh")

    if not service_active_initially:
        systemd.start_unit("ssh")

    yield "ssh"  # Provide service name to test

    # Cleanup: restore original state
    if not service_active_initially:
        systemd.stop_unit("ssh")
```

### Test Integration Example

Here's how tests use both plugins and handlers together:

```python
# In test_ssh.py
import pytest
from handlers.services import service_ssh  # Handler fixture
from plugins.sshd import Sshd             # Plugin fixture
from plugins.systemd import Systemd       # Plugin fixture

@pytest.mark.booted(reason="SSH tests require running system")
def test_ssh_service_running(service_ssh, systemd: Systemd):
    """Test that SSH service is running after handler setup."""
    assert systemd.is_active("ssh"), "SSH service is not running"

def test_ssh_config_values(sshd: Sshd):
    """Test SSH configuration using plugin fixture."""
    config_value = sshd.get_config_section("PermitRootLogin")
    assert config_value == "No", f"Expected 'No', got '{config_value}'"
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

Use `@pytest.mark.parametrize` to avoid repetitive, nearly identical tests where the differences can naturally be expressed via parameters. However, don't overuse parametrization or strive for ultra-generic test functions at the expense of clarity. If extracting a parameter makes the test clearer and avoids straightforward duplication, use it. But a small amount of code duplication is perfectly acceptable in tests if it keeps things readable and concrete.

**Yes – good use of parametrization:**

```python
@pytest.mark.parametrize("username", ["alice", "bob", "peter"])
def test_home_directory_exists(username):
    home = Path(f"/home/{username}")
    assert home.exists(), f"Missing home for {username}"
```

**No – avoid excessive abstraction for unclear wins:**

```python
# This is too abstract—each "case" has different logic, result, or context.
@pytest.mark.parametrize("input_val,expected", [(1, True), ("foo", False), ([], Exception)])
def test_weird_cases(input_val, expected):
    # ...too much unrelated logic for one test
```

**Guideline:** Prefer clarity and intent over DRY-ness in tests. Parametrize when it makes tests simpler, not just shorter.

### Missing Markers (TODO)

#### `@pytest.mark.security_id`

TODO: Explain what this marker is good for.

## Python Best Practices

### Code Style and CI Enforcement

The project enforces code quality through CI linting (see `.github/workflows/lint_tests-ng.yml`):

- **[Black](https://black.readthedocs.io/en/stable/)**: Automatic code formatting
- **[isort](https://pycqa.github.io/isort/)**: Import statement sorting
- **[Pyright](https://github.com/microsoft/pyright/blob/main/docs/getting-started.md)**: Static type checking

**Guidelines:**

- Follow [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- Use type hints for function parameters and return values
- Prefer descriptive variable names
- Use docstrings for complex functions

> [!TIP]
> Run `make -f tests-ng/dev.makefile format` locally before committing

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
