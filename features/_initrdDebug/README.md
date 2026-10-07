---
title: "Feature: _initrdDebug"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_initrdDebug/README.md
github_target_path: docs/reference/features/_initrdDebug.md
---

## Feature: _initrdDebug

### Description

Enables an interactive debug shell in the initrd by injecting a `rd.break` kernel command line parameter.

### What it does

`_initrdDebug` adds `rd.break` to the kernel command line via a `cmdline.d` configuration file. When the kernel boots with `rd.break`, dracut pauses execution before the root filesystem is mounted and drops to an emergency shell inside the initrd. This allows inspection and debugging of the early-boot environment, including dracut modules, the initrd filesystem layout, and device and network state.

A minimal `/etc/passwd` is included in the initrd via `initrd.include` to ensure user resolution works in the emergency shell.

:::warning
This feature is intended for development and troubleshooting only; do not include it in production images.
:::

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_initrdDebug/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`file.include/etc/kernel/cmdline.d/~~-rd-break.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_initrdDebug/file.include/etc/kernel/cmdline.d/~~-rd-break.cfg) ([`file.include`](/reference/features/#file-include)) | Adds `rd.break` to the kernel command line, causing dracut to drop to a shell before mounting the root filesystem. |
| [`initrd.include/etc/passwd`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_initrdDebug/initrd.include/etc/passwd) (`initrd.include`) | Minimal passwd file added to the initrd so that user names can be resolved in the debug shell. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

