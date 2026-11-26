---
title: "Feature: dbPerf"
description: "Performance tuning for resource intensive database applications (e.g."
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/dbPerf/README.md
github_target_path: docs/reference/features/dbPerf.md
---

# Feature: dbPerf

## Description

Performance tuning for resource intensive database applications (e.g. SAP HANA).

## What it does

Applies kernel and system-level tuning to optimize the host for resource-intensive database workloads. Sets kernel command line options and sysctl parameters for improved database performance.

## Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/dbPerf/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element`. |
| [`file.include/etc/kernel/cmdline.d/30-dbPerf.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/dbPerf/file.include/etc/kernel/cmdline.d/30-dbPerf.cfg) ([`file.include`](/reference/features/#file-include)) | Kernel command line tuning for database performance. |
| [`file.include/etc/sysctl.d/30-dbPerf.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/dbPerf/file.include/etc/sysctl.d/30-dbPerf.conf) ([`file.include`](/reference/features/#file-include)) | Sysctl parameters tuned for database workloads. |

## Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />
