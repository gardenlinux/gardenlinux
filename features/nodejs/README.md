---
title: "Feature: nodejs"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/nodejs/README.md
github_target_path: docs/reference/features/nodejs.md
---

## Feature: nodejs

### Description

Installs the Node.js runtime.

### What it does

Installs the `nodejs` package, providing the Node.js JavaScript runtime environment.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/nodejs/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/nodejs/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `nodejs`. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

