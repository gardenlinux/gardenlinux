---
title: "Feature: _unsigned"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_unsigned/README.md
github_target_path: docs/reference/features/_unsigned.md
---

## Feature: _unsigned

### Description

Configures the build to use unsigned EFI binaries, bypassing the signing step for development and testing builds.

### What it does

`_unsigned` instructs the build system to produce EFI binaries (bootloader and Unified Kernel Image) without applying a cryptographic signature. This allows the image to boot on systems where Secure Boot is disabled or in a development key enrollment mode, without requiring access to the Garden Linux signing keys.

The `usi.config` file provides Unified System Image (USI) build configuration specific to the unsigned variant.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_unsigned/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`usi.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_unsigned/usi.config) | USI build configuration for unsigned EFI binaries, specifying signing options for the Unified Kernel Image build. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

