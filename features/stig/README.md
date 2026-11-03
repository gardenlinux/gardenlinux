---
title: "Feature: stig"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/stig/README.md
github_target_path: docs/reference/features/stig.md
---

## Feature: stig

### Description

A feature that applies [Defense Information Systems Agency (DISA)](/reference/glossary#defense-information-systems-agency-disa) [Security Technical Implementation Guide (STIG)](/reference/glossary#security-technical-implementation-guide-stig) controls.

### What it does

Installs `aide`, `aide-common`, and `auditd`. Configures comprehensive STIG controls: audit rules, kernel auditing at boot, PAM hardening, password quality requirements, SSH hardening, resource limits, account lockout, sysctl settings, and rsyslog configuration.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Enables `auditd` and configures STIG-required services. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `aide`, `aide-common`, `auditd`. |
| [`file.include/etc/apt/apt.conf.d/01-vendor-Ubuntu`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/file.include/etc/apt/apt.conf.d/01-vendor-Ubuntu) ([`file.include`](/reference/features/#file-include)) | APT vendor configuration per STIG requirement. |
| [`file.include/etc/audit/auditd.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/file.include/etc/audit/auditd.conf) ([`file.include`](/reference/features/#file-include)) | `auditd` configuration per STIG requirements. |
| [`file.include/etc/audit/rules.d/stig.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/file.include/etc/audit/rules.d/stig.rules) ([`file.include`](/reference/features/#file-include)) | DISA STIG audit rules. |
| [`file.include/etc/kernel/cmdline.d/90-audit.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/file.include/etc/kernel/cmdline.d/90-audit.cfg) ([`file.include`](/reference/features/#file-include)) | Enables kernel auditing (`audit=1`) at boot per STIG. |
| [`file.include/etc/modprobe.d/disabled_usb.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/file.include/etc/modprobe.d/disabled_usb.conf) ([`file.include`](/reference/features/#file-include)) | Denylists USB storage per STIG requirement. |
| [`file.include/etc/pam.d/common-auth`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/file.include/etc/pam.d/common-auth) ([`file.include`](/reference/features/#file-include)) | PAM authentication configuration per STIG. |
| [`file.include/etc/pam.d/common-password`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/file.include/etc/pam.d/common-password) ([`file.include`](/reference/features/#file-include)) | PAM password configuration per STIG. |
| [`file.include/etc/rsyslog.d/50-default.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/file.include/etc/rsyslog.d/50-default.conf) ([`file.include`](/reference/features/#file-include)) | rsyslog configuration per STIG. |
| [`file.include/etc/security/faillock.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/file.include/etc/security/faillock.conf) ([`file.include`](/reference/features/#file-include)) | Account lockout configuration per STIG. |
| [`file.include/etc/security/limits.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/file.include/etc/security/limits.conf) ([`file.include`](/reference/features/#file-include)) | Resource limits per STIG. |
| [`file.include/etc/security/pwquality.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/file.include/etc/security/pwquality.conf) ([`file.include`](/reference/features/#file-include)) | Password quality requirements per STIG. |
| [`file.include/etc/ssh/sshd_config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/file.include/etc/ssh/sshd_config) ([`file.include`](/reference/features/#file-include)) | SSH daemon configuration hardened per STIG. |
| [`file.include/etc/sysctl.d/99-stig.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/file.include/etc/sysctl.d/99-stig.conf) ([`file.include`](/reference/features/#file-include)) | sysctl settings per STIG. |
| [`file.include/usr/share/pam-configs/garden-stig`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stig/file.include/usr/share/pam-configs/garden-stig) ([`file.include`](/reference/features/#file-include)) | PAM profile for STIG authentication requirements. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

