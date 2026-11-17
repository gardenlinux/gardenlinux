---
title: "Feature: python"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/python/README.md
github_target_path: docs/reference/features/python.md
---

## Feature: python

### Description

Installs the Python 3 runtime.

### What it does

Installs `python3` and `python-is-python3` (making `python` an alias for `python3`).

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/python/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/python/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `python3` and `python-is-python3`. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

