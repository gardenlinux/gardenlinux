---
title: "Feature: sap"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/sap/README.md
github_target_path: docs/reference/features/sap.md
---

## Feature: sap

### Description

Configures Garden Linux for SAP workloads, including SAP-specific logging, certificates, and security audit rules.

### What it does

Installs `auditd`, `ca-certificates`, `acl`, and `python3-apt`. Configures:

- SAP-specific audit rules for privilege escalation, privileged operations, and system integrity
- Garden Linux MOTD and issue banners
- The SAP Global Root CA certificate
- tmpfiles configuration for legacy paths

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sap/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Enables `auditd` and applies SAP-specific system configuration. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sap/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`file.include.stat`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sap/file.include.stat) ([ref](/reference/features/#file-include-stat)) | Sets ownership and permissions for SAP configuration files. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sap/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sap/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `auditd`, `ca-certificates`, `acl`, `python3-apt`. |
| [`file.include/etc/issue`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sap/file.include/etc/issue) ([`file.include`](/reference/features/#file-include)) | System identification text displayed before login on physical consoles. |
| [`file.include/etc/issue.net`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sap/file.include/etc/issue.net) ([`file.include`](/reference/features/#file-include)) | System identification text displayed to remote SSH connections. |
| [`file.include/etc/motd`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sap/file.include/etc/motd) ([`file.include`](/reference/features/#file-include)) | Message of the Day displayed after login. |
| [`file.include/etc/audit/rules.d/70-privilege-escalation.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sap/file.include/etc/audit/rules.d/70-privilege-escalation.rules) ([`file.include`](/reference/features/#file-include)) | Audit rules for tracking privilege escalation events. |
| [`file.include/etc/audit/rules.d/70-privileged-special.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sap/file.include/etc/audit/rules.d/70-privileged-special.rules) ([`file.include`](/reference/features/#file-include)) | Audit rules for privileged special operations (amd64). |
| [`file.include/etc/audit/rules.d/70-privileged-special.rules.arm64`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sap/file.include/etc/audit/rules.d/70-privileged-special.rules.arm64) ([`file.include`](/reference/features/#file-include)) | Audit rules for privileged special operations (arm64). |
| [`file.include/etc/audit/rules.d/70-system-integrity.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sap/file.include/etc/audit/rules.d/70-system-integrity.rules) ([`file.include`](/reference/features/#file-include)) | Audit rules for system integrity monitoring. |
| [`file.include/etc/tmpfiles.d/legacy.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sap/file.include/etc/tmpfiles.d/legacy.conf) ([`file.include`](/reference/features/#file-include)) | Creates legacy directory paths needed by SAP applications. |
| [`file.include/usr/local/share/ca-certificates/SAP_Global_Root_CA.crt`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sap/file.include/usr/local/share/ca-certificates/SAP_Global_Root_CA.crt) ([`file.include`](/reference/features/#file-include)) | SAP Global Root Certificate Authority certificate. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

