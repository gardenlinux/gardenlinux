---
title: "Feature: _curl"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_curl/README.md
github_target_path: docs/reference/features/_curl.md
---

## Feature: _curl

### Description

Installs `curl` and its CA certificate dependencies into the Garden Linux image.

### What it does

`_curl` adds `curl` and `ca-certificates` to the image. Many platform and cloud features require `curl` to fetch metadata, tokens, or configuration from instance metadata services. Including `_curl` as a flag allows any feature that needs `curl` to declare a dependency on it without bundling the installation logic itself.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_curl/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_curl/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `ca-certificates` and `curl`. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

