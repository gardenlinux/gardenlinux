# Garden Linux Setting ID Marker Guide

---

## Table of Contents

1. [Overview](#overview)
2. [Coverage.py and Test Coverage Analysis](#coveragepy-and-test-coverage-analysis)
3. [Marker Schema](#marker-schema)
4. [Category Reference](#category-reference)
5. [Special Patterns](#special-patterns)
6. [When to Create Markers](#when-to-create-markers)
7. [Where to Place Markers](#where-to-place-markers)

---

## Overview

This guide explains how to create and use setting identifier markers for establishing traceability between Garden Linux features and tests. The following sections detail the tooling, marker syntax, categories and placement guidelines.

---

## Coverage.py and Test Coverage Analysis

**Tool Location:** [`tests/util/coverage.py`](../tests/util/coverage.py)

### What is coverage.py?

`coverage.py` is a static analysis tool that generates coverage reports for Garden Linux by analyzing the relationship between **setting ID markers** (`GL-SET-*`) in feature configurations and their corresponding test cases. Unlike traditional code coverage tools that require test execution, this tool performs **static analysis** to determine which features have test coverage.

These markers follow a specific format (`GL-SET-$feature-$category-$description` - see [Marker Schema](#marker-schema) for details) that enables automated parsing and analysis. The tool scans both feature definitions and test files to establish traceability between what's configured and what's tested.

### Key Capabilities

1. **Static Coverage Analysis**

   - Analyzes setting ID markers in features without running tests
   - Scans test files for `@pytest.mark.setting_ids()` decorators
   - Generates coverage reports showing which features are tested

2. **Coverage Reporting**

   - Lists all setting IDs defined in features
   - Shows which setting IDs have corresponding tests
   - Identifies untested features and gaps in test coverage
   - Provides percentage coverage statistics

3. **Traceability**
   - Establishes clear links between feature configurations and tests
   - Enables audit trail for compliance requirements
   - Supports version-independent testing strategies

### How It Works

**Step 1: Feature Scanning**

- Scans feature directories (`features/*/`) for setting ID markers
- Extracts markers from inline comments in shell scripts (see [Inline Comments](#inline-comments-preferred))
- Parses `file.include.ids.yaml` and `initrd.include.ids.yaml` files for file-based markers (see [Split ID Files](#fileincludeidsyaml-and-initrdincludeidsyaml-for-file-includes))
- Builds a complete inventory of all defined setting IDs across all marker categories (see [Category Reference](#category-reference))

**Step 2: Test Scanning**

- Scans test files (`tests/test_*.py`) for pytest markers
- Extracts setting IDs from `@pytest.mark.setting_ids()` decorators (see [Tests](#tests))
- Maps each test function to its associated setting IDs

**Step 3: Coverage Analysis**

- Matches setting IDs from features with setting IDs in tests
- Identifies covered and uncovered setting IDs
- Calculates coverage percentages and statistics

**Step 4: Report Generation**

- Produces human-readable and machine-readable coverage reports
- Highlights gaps in test coverage
- Provides actionable insights for improving test coverage

### Usage Example

```bash
# Generate coverage report
python tests/util/coverage.py

...

Summary:
  Total setting IDs defined: 614
  Setting IDs found in test files: 257
  Setting IDs not found (untested): 357
  Orphaned setting IDs (in tests but not features): 0
  Coverage: 41.9%

Coverage by feature:
--------------------------------------------------------------------------------
✓ _ephemeral: 3/3 (100.0%)
⚠ _fips: 3/7 (42.9%)

...

Untested setting IDs by feature:
--------------------------------------------------------------------------------

_fips:
  Total setting IDs: 7
  Covered: 3
  Untested: 4
  Untested setting IDs:
    - GL-SET-_fips-config-openssh-sshd-Ciphers
    - GL-SET-_fips-config-openssh-sshd-KexAlgorithms
    - GL-SET-_fips-config-openssl
    - GL-SET-_fips-config-openssl-fipsinstall

...


================================================================================

✓ JSON report written to: tests/coverage_report.json
✓ JUnit XML report written to: tests/coverage_report.xml
```

### Integration with Development Workflow

1. **During Feature Development**

   - Add setting ID markers to new features (see [When to Create Markers](#when-to-create-markers) for guidelines)
   - Place markers appropriately using inline comments or split ID files (see [Where to Place Markers](#where-to-place-markers))
   - Use coverage.py to verify markers are correctly formatted and follow the [Marker Schema](#marker-schema)
   - Identify which tests need to be created

2. **During Test Development**

   - Check coverage reports to find untested features
   - Write tests with appropriate `@pytest.mark.setting_ids()` decorators (see [Tests](#tests))
   - Ensure test markers match the exact setting IDs from features
   - Verify test coverage increases after adding new tests

3. **In CI/CD Pipelines**
   - Run coverage.py as part of automated checks
   - Enforce minimum coverage thresholds
   - Block PRs that reduce test coverage
   - Generate audit reports for compliance tracking

---

## Marker Schema

All setting ID markers follow this format:

```
GL-SET-$feature-$category-$description
```

### Components

1. **Prefix:** `GL-SET-` (fixed)
2. **Feature:** Feature directory name (e.g., `aws`, `ssh`, `cis`, `server`)
3. **Category:** Type of setting (see [Category Reference](#category-reference))
4. **Description:** Hyphenated description of what the setting does

### Examples

```
GL-SET-aws-service-aws-clocksource-enable
GL-SET-ssh-config-sshd-config-permissions
GL-SET-base-config-no-hostname
GL-SET-server-service-systemd-timesyncd-enable
GL-SET-cisOS-config-crontab-permissions
```

---

## Category Reference

Garden Linux uses **four main categories** for setting ID markers:

### 1. `config` - Configuration Settings

**Purpose:** Configuration files, system settings, kernel parameters, security policies

**Subcategories:**

| Pattern                        | Meaning                    | Example                                  |
| ------------------------------ | -------------------------- | ---------------------------------------- |
| `config-$path-$setting`        | Configuration file content | `config-ssh-sshd-config-permitrootlogin` |
| `config-$path-permissions`     | File/directory permissions | `config-hosts-permissions`               |
| `config-$path-link`            | Symbolic link              | `config-locale-link`                     |
| `config-no-$item`              | File/directory absence     | `config-no-hostname`                     |
| `config-$component-$parameter` | Configuration parameter    | `config-audit-space-left-action`         |

**Why Test This:**

- ✅ Verify configuration files are correctly rendered
- ✅ Ensure permissions are set for security
- ✅ Validate kernel parameters are active
- ✅ Confirm files are removed/present as expected

**Example Markers:**

- `GL-SET-base-config-os-release` - /etc/os-release content
- `GL-SET-server-config-hosts-permissions` - /etc/hosts permissions (0644)
- `GL-SET-server-config-locale-link` - /etc/default/locale → /etc/locale.conf
- `GL-SET-base-config-no-hostname` - /etc/hostname is removed
- `GL-SET-cisAudit-config-audit-space-left-action` - Audit daemon config parameter

### 2. `service` - Systemd Services and Timers

**Purpose:** Systemd units (services, timers, mounts, sockets)

**Subcategories:**

| Pattern                      | Meaning                 | Example                                   |
| ---------------------------- | ----------------------- | ----------------------------------------- |
| `service-$unit-enable`       | Service is enabled      | `service-systemd-timesyncd-enable`        |
| `service-$unit-disable`      | Service is disabled     | `service-systemd-timesyncd-disable`       |
| `service-$unit-mask`         | Service is masked       | `service-google-guest-agent-manager-mask` |
| `service-$unit-override`     | Override service config | `service-systemd-timesyncd-override`      |
| `service-timer-$unit-enable` | Timer is enabled        | `service-timer-aide-check-enable`         |

**Why Test This:**

- ✅ Verify services are enabled/disabled as configured
- ✅ Ensure service states for functionality

**Example Markers:**

- `GL-SET-server-service-systemd-networkd-enable` - systemd-networkd.service enabled
- `GL-SET-azure-service-systemd-timesyncd-disable` - systemd-timesyncd disabled (Azure uses chrony)
- `GL-SET-gcp-service-google-guest-agent-manager-mask` - GCP agent masked
- `GL-SET-aide-config-service-timer-aide-check-enable` - AIDE check timer enabled

### 3. `mount` - Filesystem Mounts

**Purpose:** Filesystem mount points and mount options

**Subcategories:**

| Pattern                     | Meaning             | Example                   |
| --------------------------- | ------------------- | ------------------------- |
| `config-mount-$path-enable` | Mount unit enabled  | `config-mount-tmp-enable` |
| `config-mount-$path`        | Mount configuration | `config-mount-tmp`        |

**Why Test This:**

- ✅ Ensure partitions are mounted as specified
- ✅ Validate mount flags (nosuid, noexec, nodev)

**Example Markers:**

- `GL-SET-server-config-mount-tmp-enable` - tmp.mount unit enabled
- `GL-SET-server-config-mount-tmp` - tmp.mount unit configuration

### 4. `script` - Executable Scripts

**Purpose:** Shell scripts, hooks, and executables

**Subcategories:**

| Pattern                       | Meaning              | Example                     |
| ----------------------------- | -------------------- | --------------------------- |
| `script-$name-$action`        | Script execution     | `script-clocksource-setup`  |
| `script-$component-$function` | Script functionality | `script-profile-autologout` |

**Why Test This:**

- ✅ Verify scripts are present and executable
- ✅ Ensure scripts produce expected side effects
- ✅ Validate script configurations

**Example Markers:**

- `GL-SET-aws-script-clocksource-setup` - AWS clocksource setup script
- `GL-SET-cloud-script-profile-autologout` - Auto-logout profile script

---

## Special Patterns

### Overview: `-no-` vs `-disable`

Markers use two distinct patterns to indicate negation, each with a specific semantic meaning:

| Pattern    | Meaning                           | System State           | Test Verification                  |
| ---------- | --------------------------------- | ---------------------- | ---------------------------------- |
| `-no-`     | **Absence** (does not exist)      | Completely removed     | Check file/directory doesn't exist |
| `-disable` | **Deactivation** (exists but off) | Present but turned off | Check state is "disabled"          |

**Why This Distinction Matters:**

1. **Different Test Assertions**: Tests verify different conditions
2. **Different Security Guarantees**: Absence is stronger than deactivation
3. **Different Reversibility**: Removed items need reinstallation, disabled items can be re-enabled
4. **Clear Intent**: Makes it obvious whether something is missing or just turned off

---

### The `-no-` Pattern (Absence/Removal)

**Meaning:** Indicates something **does not exist** or was **completely removed**

**Use For:**

- Files that must not exist (e.g., security-sensitive files)
- Directories that were cleaned up
- Configuration sections removed from files
- Systemd override files that don't exist

**Common Patterns:**

| Pattern                         | Meaning                     | Example                                 |
| ------------------------------- | --------------------------- | --------------------------------------- |
| `config-no-$file`               | File does not exist         | `config-no-hostname`                    |
| `config-no-$directory`          | Directory does not exist    | `config-no-initrd-img`                  |
| `service-no-$unit-override`     | No systemd override exists  | `service-no-systemd-timesyncd-override` |
| `config-$component-no-$feature` | Feature removed from config | `config-cloud-no-growpart`              |

**Why Test `-no-` Patterns:**

- ✅ Verify cleanup operations succeeded
- ✅ Ensure security-sensitive files are actually removed
- ✅ Confirm features are not present (stronger guarantee than disabled)

---

### The `-disable` Pattern (Deactivation)

**Meaning:** Indicates something **exists but is turned off** or **deactivated**

**Use For:**

- Services that exist but are disabled
- Features in configuration files set to "false" or "no"
- Kernel modules that exist but are not loaded
- Functionality that can be re-enabled without reinstalling

**Common Patterns:**

| Pattern                              | Meaning                           | Example                             |
| ------------------------------------ | --------------------------------- | ----------------------------------- |
| `service-$unit-disable`              | Service exists but disabled       | `service-systemd-timesyncd-disable` |
| `config-$component-$feature-disable` | Feature set to disabled in config | `config-sshd-x11forwarding-disable` |

**Why Test `-disable` Patterns:**

- ✅ Verify services are in correct disabled state
- ✅ Ensure features are turned off in configuration
- ✅ Confirm functionality is deactivated (but can be re-enabled if needed)

---

## When to Create Markers

### ✅ DO Create Markers For:

**Runtime-Verifiable Settings:**

- Configuration file content and structure
- File/directory permissions and ownership
- File/directory presence or absence
- Service enable/disable/mask states
- Systemd timer states
- Mount point configurations
- Symbolic links
- Kernel parameters (sysctl, cmdline)
- PAM configurations
- Audit rules

**Why:** These settings define **system behavior** that must be verified on a running system.

### ❌ DO NOT Create Markers For:

**Package Installation:**

- Packages in `pkg.include`
- Packages in `pkg.exclude`
- Package availability checks

> [!NOTE]
> If a package in `pkg.include` installs an important service, it makes sense to add a `$service-$unit-enable` marker.
> Currently there is no "more elegant" way as we do not explicitelly enable services. This is just the [debian way of doing things](https://manpages.debian.org/testing/debhelper/dh_systemd_enable.1.en.html).

**Why:**

- Package installation failures cause the **build to fail** - already validated
- If a package is missing, dependent configurations won't work (redundant testing)
- Testing `dpkg -l | grep package` adds no value

**Build-Time Operations:**

- File copying during build
- Directory creation during build
- Archive extraction during build

**Why:** These are build-time operations that cannot fail silently - build failures catch them.

---

## Where to Place Markers

### Features

#### Inline Comments (Preferred)

**Files:** `exec.config`, `exec.early`, `exec.post`, `exec.late`, `pkg.exclude`, `file.exclude`

**Format:**

1. Add markers as simple inline comments.
2. Multiple markers can be listed in multiple lines.

```bash
# GL-SET-$feature-$category1-$description1
# GL-SET-$feature-$category2-$description2
command or configuration
```

**Examples:**

```bash
# features/server/exec.config

# GL-SET-server-service-systemd-networkd-enable
systemctl enable systemd-networkd

# GL-SET-server-config-group-wheel
addgroup --system wheel

# GL-SET-server-config-hosts-permissions
chmod g-w / /etc/hosts
```

```bash
# features/base/exec.post

# GL-SET-base-config-no-hostname
rm "$rootfs/etc/hostname"

# GL-SET-base-config-resolv-conf
if [ -f "$rootfs/etc/resolv.conf" ] && [ ! -L "$rootfs/etc/resolv.conf" ]; then
    rm "$rootfs/etc/resolv.conf"
fi
```

#### file.include.ids.yaml and initrd.include.ids.yaml (For File Includes)

**Use For:** Files in `file.include/` and `initrd.include/` directories

**Why:** Markers should not appear in the final image files

**Files:**
- `file.include.ids.yaml` - for files in `file.include/` directory
- `initrd.include.ids.yaml` - for files in `initrd.include/` directory

**Format:**

```yaml
# features/$feature/file.include.ids.yaml
setting_ids:
  "path/to/file1":
    - GL-SET-$feature-$category-$description1
  "path/to/file2":
    - GL-SET-$feature-$category-$description2
```

**Important:** 
- Paths must NOT have a leading slash
- Paths must be quoted strings

**Example:**

```yaml
# features/firewall/file.include.ids.yaml
setting_ids:
  "etc/nftables.conf":
    - GL-SET-firewall-config-nftables-conf
  "etc/nftables.d/gl-default.nft":
    - GL-SET-firewall-config-nftables-default
```

```yaml
# features/_usi/initrd.include.ids.yaml
setting_ids:
  "etc/repart.d/00-efi.conf":
    - GL-SET-_usi-config-initrd-repart-efi
  "usr/bin/repart-esp-disk":
    - GL-SET-_usi-config-initrd-script-repart-esp-disk
```

### Tests

**Use For:** Referencing setting ID markers in test functions

**Format:**

1. Use the `@pytest.mark.setting_ids()` decorator on test functions
2. Pass a **list** of marker strings (even for a single marker)
3. Multiple markers can be listed for tests that verify multiple settings

```python
@pytest.mark.setting_ids(["GL-SET-$feature-$category-$description"])
def test_something(client):
    """Test implementation"""
    # test code here
```

**Example:**

```python
# tests/test_cis.py
import pytest

@pytest.mark.setting_ids([
    "GL-SET-cisOS-config-crontab-permissions",
    "GL-SET-cisOS-config-cron-hourly-permissions",
    "GL-SET-cisOS-config-cron-daily-permissions"
])
def test_cron_permissions(client):
    """Verify CIS-compliant permissions on cron directories"""
    cron_paths = ["/etc/crontab", "/etc/cron.hourly", "/etc/cron.daily"]
    for path in cron_paths:
        result = client.execute(f"stat -c '%a' {path}")
        assert result.stdout.strip() == "700"
```

---

**For more information:**

- [ADR 0031 - Static Feature/Test Coverage Analysis](docs/architecture/decisions/0031-static-feature-test-coverage-analysis.md)
- [Coverage Reporting Tool](tests/util/coverage.py)
- [Test Framework Documentation](tests/README.md)

