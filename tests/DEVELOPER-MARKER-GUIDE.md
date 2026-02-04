# Garden Linux Setting ID Marker Guide

**Purpose:** Developer guide for creating and using GL-SET markers in Garden Linux features and tests

---

## Table of Contents

1. [Overview](#overview)
2. [Marker Schema](#marker-schema)
3. [Category Reference](#category-reference)
4. [Special Patterns](#special-patterns)
5. [When to Create Markers](#when-to-create-markers)
6. [Where to Place Markers](#where-to-place-markers)

---

## Overview

Garden Linux uses **setting identifier markers** (GL-SET-\*) to establish traceability between feature configurations and test cases. These markers enable static coverage analysis without requiring test execution.

**Key Benefits:**

- Track which feature settings have corresponding tests
- Generate coverage reports without running tests
- Maintain clear audit trail for compliance requirements
- Enable version-independent testing

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

#### setting_ids.yaml (For File Includes)

**Use For:** Files in `file.include/` and `initrd.include/` directories

**Why:** Markers should not appear in the final image files

**Format:**

```yaml
# features/$feature/setting_ids.yaml
setting_ids:
  - id: GL-SET-$feature-$category-$description
    files:
      - path/to/file1
      - path/to/file2
```

**Example:**

```yaml
# features/firewall/setting_ids.yaml
setting_ids:
  - id: GL-SET-firewall-config-nftables-include
    files:
      - file.include/etc/nftables.conf
      - file.include/etc/nftables.d/gl-default.nft
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
