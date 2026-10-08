---
title: "Feature: fedramp"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/fedramp/README.md
github_target_path: docs/reference/features/fedramp.md
---

## Feature: fedramp

### Description

A feature that configures Garden Linux for [Federal Risk and Authorization Management Program (FedRAMP)](/reference/glossary#federal-risk-and-authorization-management-program-fedramp) compliance. It is a meta-feature that includes sub-features for intrusion detection, antivirus, and firewall hardening.

### What it does

Installs `apparmor` and `chrony` (replacing `systemd-timesyncd`). Configures FedRAMP-required settings including: FIPS and AppArmor kernel parameters, SSH hardening, resource limits, a pre-login banner, and an IPv4/IPv6 firewall. Includes `aide` and `clamav` for intrusion detection and antivirus scanning.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Switches from `systemd-timesyncd` to `chrony`, enables AppArmor, and applies FedRAMP configuration. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/pkg.exclude) ([ref](/reference/features/#pkg-exclude)) | Prevents installation of: `systemd-timesyncd`. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `apparmor`, `chrony`. |
| [`file.include/etc/issue.net`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/file.include/etc/issue.net) ([`file.include`](/reference/features/#file-include)) | Pre-login banner displayed to remote users per FedRAMP requirement. |
| [`file.include/etc/chrony/chrony.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/file.include/etc/chrony/chrony.conf) ([`file.include`](/reference/features/#file-include)) | NTP configuration using `chrony` instead of `systemd-timesyncd`. |
| [`file.include/etc/firewall/ipv4_flush.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/file.include/etc/firewall/ipv4_flush.sh) ([`file.include`](/reference/features/#file-include)) | Script that flushes all IPv4 firewall rules. |
| [`file.include/etc/firewall/ipv4_gl_default.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/file.include/etc/firewall/ipv4_gl_default.conf) ([`file.include`](/reference/features/#file-include)) | Default Garden Linux IPv4 firewall rules. |
| [`file.include/etc/firewall/ipv6_flush.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/file.include/etc/firewall/ipv6_flush.sh) ([`file.include`](/reference/features/#file-include)) | Script that flushes all IPv6 firewall rules. |
| [`file.include/etc/firewall/ipv6_gl_default.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/file.include/etc/firewall/ipv6_gl_default.conf) ([`file.include`](/reference/features/#file-include)) | Default Garden Linux IPv6 firewall rules. |
| [`file.include/etc/kernel/cmdline.d/30-fips.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/file.include/etc/kernel/cmdline.d/30-fips.cfg) ([`file.include`](/reference/features/#file-include)) | Enables FIPS mode in the kernel command line per FedRAMP requirement. |
| [`file.include/etc/kernel/cmdline.d/90-lsm.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/file.include/etc/kernel/cmdline.d/90-lsm.cfg) ([`file.include`](/reference/features/#file-include)) | Sets AppArmor as the active Linux Security Module. |
| [`file.include/etc/security/limits.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/file.include/etc/security/limits.conf) ([`file.include`](/reference/features/#file-include)) | Resource limits per FedRAMP requirements. |
| [`file.include/etc/ssh/sshd_config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/file.include/etc/ssh/sshd_config) ([`file.include`](/reference/features/#file-include)) | SSH daemon configuration hardened per FedRAMP requirements. |
| [`file.include/etc/systemd/system/gardenlinux-fw-ipv4.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/file.include/etc/systemd/system/gardenlinux-fw-ipv4.service) ([`file.include`](/reference/features/#file-include)) | systemd service that applies the Garden Linux IPv4 firewall rules at boot. |
| [`file.include/etc/systemd/system/gardenlinux-fw-ipv6.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/fedramp/file.include/etc/systemd/system/gardenlinux-fw-ipv6.service) ([`file.include`](/reference/features/#file-include)) | systemd service that applies the Garden Linux IPv6 firewall rules at boot. |

### Related features

**Includes:**

- [`aide`](/reference/features/aide) — host-based intrusion detection required by FedRAMP.
- [`clamav`](/reference/features/clamav) — antivirus scanning required by FedRAMP.

**Excludes (incompatible with):**

- [`cis`](/reference/features/cis) — `fedramp` and `cis` both implement overlapping compliance requirements and cannot be composed together.

## Related topics

<RelatedTopics />

