---
title: "Feature: cisPackages"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/cisPackages/README.md
github_target_path: docs/reference/features/cisPackages.md
---

## Feature: cisPackages

### Description

A sub-feature of [`cis`](/reference/features/cis) that manages required and unwanted packages per [CIS benchmark](/reference/glossary#cis-center-for-internet-security) requirements. Must be used with the [`cis`](/reference/features/cis) feature.

### What it does

Installs `git`, `syslog-ng`, `libpam-pwquality`, and `tcpd`. Also removes packages that are unwanted per CIS requirements.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisPackages/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisPackages/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `git`, `libpam-pwquality`, `libpam-modules-bin`, `logrotate`, `tcpd`, and others. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

