---
title: "Feature: cisSshd"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/cisSshd/README.md
github_target_path: docs/reference/features/cisSshd.md
---

## Feature: cisSshd

### Description

A sub-feature of [`cis`](/reference/features/cis) that configures sshd per [CIS benchmark](/reference/glossary#cis-center-for-internet-security) requirements. Must be used with the [`cis`](/reference/features/cis) feature.

### What it does

Restricts SSH ciphers and MACs to CIS-approved algorithms and configures an SSH login banner. Also includes Garden Linux firewall rules for IPv4 and IPv6.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisSshd/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Applies CIS SSH configuration and enables the Garden Linux firewall services. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisSshd/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisSshd/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`file.include/etc/firewall/ipv4_flush.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisSshd/file.include/etc/firewall/ipv4_flush.sh) ([`file.include`](/reference/features/#file-include)) | Script that flushes all IPv4 firewall rules. |
| [`file.include/etc/firewall/ipv4_gl_default.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisSshd/file.include/etc/firewall/ipv4_gl_default.conf) ([`file.include`](/reference/features/#file-include)) | Default Garden Linux IPv4 firewall rules. |
| [`file.include/etc/firewall/ipv6_flush.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisSshd/file.include/etc/firewall/ipv6_flush.sh) ([`file.include`](/reference/features/#file-include)) | Script that flushes all IPv6 firewall rules. |
| [`file.include/etc/firewall/ipv6_gl_default.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisSshd/file.include/etc/firewall/ipv6_gl_default.conf) ([`file.include`](/reference/features/#file-include)) | Default Garden Linux IPv6 firewall rules. |
| [`file.include/etc/ssh/sshd-banner`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisSshd/file.include/etc/ssh/sshd-banner) ([`file.include`](/reference/features/#file-include)) | SSH pre-login banner text displayed to connecting users per CIS requirement. |
| [`file.include/etc/systemd/system/gardenlinux-fw-ipv4.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisSshd/file.include/etc/systemd/system/gardenlinux-fw-ipv4.service) ([`file.include`](/reference/features/#file-include)) | systemd service that applies the Garden Linux IPv4 firewall rules at boot. |
| [`file.include/etc/systemd/system/gardenlinux-fw-ipv6.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisSshd/file.include/etc/systemd/system/gardenlinux-fw-ipv6.service) ([`file.include`](/reference/features/#file-include)) | systemd service that applies the Garden Linux IPv6 firewall rules at boot. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

