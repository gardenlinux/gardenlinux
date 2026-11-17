---
title: "Feature: cisAudit"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/cisAudit/README.md
github_target_path: docs/reference/features/cisAudit.md
---

## Feature: cisAudit

### Description

A sub-feature of [`cis`](/reference/features/cis) that installs and configures `auditd` per [CIS benchmark](/reference/glossary#cis-center-for-internet-security) requirements. Must be used with the [`cis`](/reference/features/cis) feature.

### What it does

Configures `auditd` logging of security events including date/time changes, sudo usage, and disk-space failure handling. Provides audit rules in `/etc/audit/rules.d/99-cis.rules` and a systemd service override to ensure audit rules are loaded correctly at boot.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisAudit/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Enables `auditd` and applies CIS audit configuration. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisAudit/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisAudit/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`file.include/etc/audit/rules.d/99-cis.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisAudit/file.include/etc/audit/rules.d/99-cis.rules) ([`file.include`](/reference/features/#file-include)) | CIS benchmark audit rules covering date/time changes, sudo usage, and disk-space failure handling. |
| [`file.include/etc/systemd/system/audit-rules.service.d/override.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisAudit/file.include/etc/systemd/system/audit-rules.service.d/override.conf) ([`file.include`](/reference/features/#file-include)) | systemd override to ensure audit rules are loaded correctly after `auditd` starts. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

