---
title: "Feature: baremetal"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/baremetal/README.md
github_target_path: docs/reference/features/baremetal.md
---

## Feature: baremetal

### Description

A [platform](/reference/glossary.html#platform) feature that builds a Garden Linux
image for bare metal systems. It is a thin wrapper around the
[`metal`](/reference/features/metal) element feature.

### What it does

Pulls in the [`metal`](/reference/features/metal) element, which provides the
standard kernel, physical hardware support, and server configuration needed to
run Garden Linux on physical servers. The `baremetal` platform feature selects
this composition for bare metal deployment targets. Artifacts are delivered as
`.raw` and `.qcow2` files.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/baremetal/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: platform` and included/excluded features. |

### Related features

**Includes:**

- [`metal`](/reference/features/metal) — provides standard kernel, physical hardware components, and server configuration for bare metal deployment.

## Related topics

<RelatedTopics />

