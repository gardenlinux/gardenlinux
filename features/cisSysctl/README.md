---
title: "Feature: cisSysctl"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/cisSysctl/README.md
github_target_path: docs/reference/features/cisSysctl.md
---

## Feature: cisSysctl

### Description

A sub-feature of [`cis`](/reference/features/cis) that configures `sysctl` settings per [CIS benchmark](/reference/glossary#cis-center-for-internet-security) requirements. Must be used with the [`cis`](/reference/features/cis) feature.

### What it does

Disables IPv6 entirely. Disables IPv4 forwarding and redirects. Applies these settings via a sysctl drop-in at `/etc/sysctl.d/99-cis.conf`.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisSysctl/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisSysctl/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`file.include/etc/sysctl.d/99-cis.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisSysctl/file.include/etc/sysctl.d/99-cis.conf) ([`file.include`](/reference/features/#file-include)) | Sets sysctl parameters per CIS benchmarks: disables IPv6, IPv4 forwarding, and IPv4 redirects. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

