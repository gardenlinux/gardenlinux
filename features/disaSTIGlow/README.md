---
title: "Feature: disaSTIGlow"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/disaSTIGlow/README.md
github_target_path: docs/reference/features/disaSTIGlow.md
---

## Feature: disaSTIGlow

### Description

A feature that applies [Defense Information Systems Agency (DISA)](/reference/glossary#defense-information-systems-agency-disa) [Security Technical Implementation Guide (STIG)](/reference/glossary#security-technical-implementation-guide-stig) low-severity controls.

### What it does

Configures `auditd` settings, account lockout (`faillock`), resource limits, password quality requirements, and sysctl settings per DISA STIG low-impact requirements.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGlow/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Applies DISA STIG low-severity configuration. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGlow/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGlow/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`file.include/etc/audit/auditd.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGlow/file.include/etc/audit/auditd.conf) ([`file.include`](/reference/features/#file-include)) | Configures `auditd` per DISA STIG requirements. |
| [`file.include/etc/security/faillock.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGlow/file.include/etc/security/faillock.conf) ([`file.include`](/reference/features/#file-include)) | Configures account lockout per DISA STIG requirements. |
| [`file.include/etc/security/limits.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGlow/file.include/etc/security/limits.conf) ([`file.include`](/reference/features/#file-include)) | Sets resource limits per DISA STIG requirements. |
| [`file.include/etc/security/pwquality.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGlow/file.include/etc/security/pwquality.conf) ([`file.include`](/reference/features/#file-include)) | Sets password quality requirements per DISA STIG. |
| [`file.include/etc/sysctl.d/99-disaSTIG.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/disaSTIGlow/file.include/etc/sysctl.d/99-disaSTIG.conf) ([`file.include`](/reference/features/#file-include)) | Applies sysctl settings per DISA STIG requirements. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

