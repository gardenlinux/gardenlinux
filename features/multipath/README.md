---
title: "Feature: multipath"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/multipath/README.md
github_target_path: docs/reference/features/multipath.md
---

## Feature: multipath

### Description

Installs multipath I/O support, required by `iscsi` and NVMe over TCP.

### What it does

Installs `multipath-tools` and provides a configuration file for `multipath`. Multipath I/O allows a system to use multiple physical paths between host and storage devices for redundancy and performance.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/multipath/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/multipath/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/multipath/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `multipath-tools`. |
| [`file.include/etc/multipath.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/multipath/file.include/etc/multipath.conf) ([`file.include`](/reference/features/#file-include)) | Configuration file for `multipath-tools`, defining path grouping and failover policies. |

### Related features

**Includes:**

- [`server`](/reference/features/server) — provides the server base layer required for multipath operation.

## Related topics

<RelatedTopics />

