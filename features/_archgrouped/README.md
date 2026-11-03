---
title: "Feature: _archgrouped"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_archgrouped/README.md
github_target_path: docs/reference/features/_archgrouped.md
---

## Feature: _archgrouped

### Description

Publishes all architecture-specific builds of a Garden Linux artifact as a single grouped multi-architecture artifact.

### What it does

When added to a build, `_archgrouped` instructs the publishing pipeline to group the resulting artifacts for all target architectures (for example, `amd64` and `arm64`) under a single combined entry. Without this flag, each architecture produces a separate, independent artifact. This flag is typically used to produce a unified multi-arch image reference for registries or release systems that support multi-arch manifests.

The `requirements.mod` file captures the publishing group identifier, which the build system uses to associate the per-architecture builds with each other.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_archgrouped/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`requirements.mod`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_archgrouped/requirements.mod) | Sets the `publishing_group` variable used to link per-architecture builds into a single grouped artifact. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

