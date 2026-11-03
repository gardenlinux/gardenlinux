---
title: "Feature: cis"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/cis/README.md
github_target_path: docs/reference/features/cis.md
---

## Feature: cis

### Description

The `cis` feature is a meta-feature that groups all [CIS benchmark](/reference/glossary#cis-center-for-internet-security) benchmark sub-features into a single composable unit.

### What it does

This feature represents a meta-feature that includes multiple sub-features, each covering a specific area of the CIS benchmark for Debian Linux. It applies the following CIS controls:

- `aide` — host-based intrusion detection
- `cisAudit` — auditd logging of security events
- `cisModprobe` — kernel module denylisting
- `cisOS` — OS-level security settings (PAM, file permissions, login options)
- `cisPackages` — required and unwanted package management
- `cisPartition` — CIS-compliant partition layout
- `cisSshd` — SSH hardening and firewall rules
- `cisSysctl` — sysctl settings (disables IPv6, IPv4 forwarding and redirects)
- `firewall` — nftables-based firewall

An `exec.config` script applies CIS-specific configuration that spans multiple sub-areas.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cis/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Applies CIS framework configuration that spans multiple sub-feature areas. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cis/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |

### Related features

**Includes:**

- [`aide`](/reference/features/aide) — host-based intrusion detection required by CIS.
- [`cisAudit`](/reference/features/cisAudit) — `auditd` logging of security events per CIS benchmark.
- [`cisModprobe`](/reference/features/cisModprobe) — kernel module denylisting per CIS benchmark.
- [`cisOS`](/reference/features/cisOS) — OS-level security settings per CIS benchmark.
- [`cisPackages`](/reference/features/cisPackages) — required and unwanted package management per CIS benchmark.
- [`cisPartition`](/reference/features/cisPartition) — CIS-compliant partition layout.
- [`cisSshd`](/reference/features/cisSshd) — SSH hardening and firewall rules per CIS benchmark.
- [`cisSysctl`](/reference/features/cisSysctl) — sysctl settings per CIS benchmark.
- [`firewall`](/reference/features/firewall) — nftables firewall required for CIS network controls.

**Excludes (incompatible with):**

- [`fedramp`](/reference/features/fedramp) — `cis` and `fedramp` both implement overlapping compliance requirements and cannot be composed together.

## Related topics

<RelatedTopics />

