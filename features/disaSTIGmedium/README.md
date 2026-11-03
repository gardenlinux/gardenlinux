---
title: "Feature: disaSTIGmedium"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/disaSTIGmedium/README.md
github_target_path: docs/reference/features/disaSTIGmedium.md
---

## Feature: disaSTIGmedium

### Description

A feature that applies [Defense Information Systems Agency (DISA)](/reference/glossary#defense-information-systems-agency-disa) [Security Technical Implementation Guide (STIG)](/reference/glossary#security-technical-implementation-guide-stig) medium-severity controls, building on the low-security controls from [`disaSTIGlow`](/reference/features/disaSTIGlow).

### What it does

Installs `aide`, `aide-common`, `auditd`, `libpam-systemd`, `sudo`, and `systemd-timesyncd`. Configures comprehensive audit rules for DISA STIG medium controls, PAM authentication hardening, password requirements, SSH hardening, rsyslog, and scheduled AIDE integrity checks.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Applies DISA STIG medium-severity configuration: enables audit rules, PAM, and AIDE services. |
| [`exec.late`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/exec.late) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Late-stage setup for DISA STIG medium controls. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `aide`, `aide-common`, `auditd`, `libpam-systemd`, `sudo`, `systemd-timesyncd`. |
| [`file.include/etc/aide/aide.conf.d/31_aide_audit-tools`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/aide/aide.conf.d/31_aide_audit-tools) ([`file.include`](/reference/features/#file-include)) | AIDE configuration for monitoring audit tools per DISA STIG. |
| [`file.include/etc/audit/rules.d/30-disaSTIG.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/audit/rules.d/30-disaSTIG.rules) ([`file.include`](/reference/features/#file-include)) | DISA STIG audit rules for amd64. |
| [`file.include/etc/audit/rules.d/30-disaSTIG.rules.arm64`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/audit/rules.d/30-disaSTIG.rules.arm64) ([`file.include`](/reference/features/#file-include)) | DISA STIG audit rules for arm64. |
| [`file.include/etc/audit/rules.d/90-finalize.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/audit/rules.d/90-finalize.rules) ([`file.include`](/reference/features/#file-include)) | Finalizes audit rule loading (locks the audit configuration). |
| [`file.include/etc/default/aide`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/default/aide) ([`file.include`](/reference/features/#file-include)) | Configures AIDE defaults including database paths and update behavior. |
| [`file.include/etc/default/useradd`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/default/useradd) ([`file.include`](/reference/features/#file-include)) | Sets secure `useradd` defaults per DISA STIG. |
| [`file.include/etc/kernel/cmdline.d/90-audit.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/kernel/cmdline.d/90-audit.cfg) ([`file.include`](/reference/features/#file-include)) | Enables kernel auditing (`audit=1`) at boot per DISA STIG. |
| [`file.include/etc/pam.d/common-account`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/pam.d/common-account) ([`file.include`](/reference/features/#file-include)) | PAM account configuration per DISA STIG authentication requirements. |
| [`file.include/etc/pam.d/common-auth`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/pam.d/common-auth) ([`file.include`](/reference/features/#file-include)) | PAM authentication configuration per DISA STIG requirements. |
| [`file.include/etc/pam.d/common-password`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/pam.d/common-password) ([`file.include`](/reference/features/#file-include)) | PAM password configuration per DISA STIG requirements. |
| [`file.include/etc/profile.d/99-terminal_tmout.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/profile.d/99-terminal_tmout.sh) ([`file.include`](/reference/features/#file-include)) | Sets terminal auto-logout timeout per DISA STIG. |
| [`file.include/etc/rsyslog.d/50-default.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/rsyslog.d/50-default.conf) ([`file.include`](/reference/features/#file-include)) | rsyslog configuration for DISA STIG audit log forwarding. |
| [`file.include/etc/security/pwquality.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/security/pwquality.conf) ([`file.include`](/reference/features/#file-include)) | Password quality requirements per DISA STIG medium controls. |
| [`file.include/etc/ssh/sshd_config.d/50-disaSTIG.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/ssh/sshd_config.d/50-disaSTIG.conf) ([`file.include`](/reference/features/#file-include)) | SSH daemon hardening per DISA STIG (ciphers, MACs, key exchange, auth settings). |
| [`file.include/etc/sudoers.d/disaSTIG-sudo-log`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/sudoers.d/disaSTIG-sudo-log) ([`file.include`](/reference/features/#file-include)) | Configures sudo to log all commands per DISA STIG. |
| [`file.include/etc/sudoers.d/keepssh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/sudoers.d/keepssh) ([`file.include`](/reference/features/#file-include)) | Preserves `SSH_AUTH_SOCK` across sudo sessions. |
| [`file.include/etc/sudoers.d/wheel`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/sudoers.d/wheel) ([`file.include`](/reference/features/#file-include)) | Grants sudo access to the `wheel` group. |
| [`file.include/etc/sysctl.d/99-disaSTIG.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/sysctl.d/99-disaSTIG.conf) ([`file.include`](/reference/features/#file-include)) | sysctl settings per DISA STIG medium controls. |
| [`file.include/etc/systemd/system/aide-check.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/systemd/system/aide-check.service) ([`file.include`](/reference/features/#file-include)) | systemd service that runs AIDE integrity checks. |
| [`file.include/etc/systemd/system/aide-check.timer`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/systemd/system/aide-check.timer) ([`file.include`](/reference/features/#file-include)) | systemd timer that schedules periodic AIDE integrity checks. |
| [`file.include/etc/systemd/system/aide-init.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/systemd/system/aide-init.service) ([`file.include`](/reference/features/#file-include)) | Initializes the AIDE database on first boot. |
| [`file.include/etc/systemd/system/audit-rules.service.d/override.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/systemd/system/audit-rules.service.d/override.conf) ([`file.include`](/reference/features/#file-include)) | Override to ensure audit rules load correctly at boot. |
| [`file.include/etc/tmpfiles.d/zz-disastig-journal-permissions.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/etc/tmpfiles.d/zz-disastig-journal-permissions.conf) ([`file.include`](/reference/features/#file-include)) | Sets systemd journal permissions per DISA STIG. |
| [`file.include/usr/local/sbin/aide-init-onboot.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/usr/local/sbin/aide-init-onboot.sh) ([`file.include`](/reference/features/#file-include)) | Script that initializes the AIDE database on first boot if not already present. |
| [`file.include/usr/share/pam-configs/garden-disaSTIG`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGmedium/file.include/usr/share/pam-configs/garden-disaSTIG) ([`file.include`](/reference/features/#file-include)) | PAM configuration profile for DISA STIG authentication requirements. |

### Related features

**Includes:**

- [`disaSTIGlow`](/reference/features/disaSTIGlow) — applies low-severity DISA STIG controls required as a baseline.
- [`ssh`](/reference/features/ssh) — SSH configuration required for DISA STIG SSH hardening.
- [`log`](/reference/features/log) — logging infrastructure required for DISA STIG audit log controls.

## Related topics

<RelatedTopics />

