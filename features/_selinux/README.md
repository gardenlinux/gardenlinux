---
title: "Feature: _selinux"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_selinux/README.md
github_target_path: docs/reference/features/_selinux.md
---

## Feature: _selinux

### Description

Enables [Security-Enhanced Linux (SELinux)](/reference/glossary#selinux) mandatory access control by installing a default policy and configuring the system to boot in SELinux enforcing mode.

### What it does

`_selinux` installs the `selinux-basics`, `selinux-policy-default`, and `gardenlinux-selinux-module` packages, and adds a `cmdline.d` configuration file that sets the Linux Security Module (LSM) to `selinux` on the kernel command line. An `exec.post` script runs after the rootfs is assembled to apply SELinux extended-attribute labels to the filesystem.

Tests verify that the LSM is correctly set on the kernel command line and that the required SELinux policy rules are present.

`_selinux` is incompatible with [`_iso`](/reference/features/_iso) because SELinux filesystem labeling cannot be applied to the live SquashFS image produced by that feature.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.post`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_selinux/exec.post) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Applies SELinux extended-attribute labels to the assembled rootfs after all other build steps complete. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_selinux/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files in this feature to test-coverage marker IDs for SELinux verification tests. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_selinux/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_selinux/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `selinux-basics`, `selinux-policy-default`, and `gardenlinux-selinux-module`. |
| [`file.include/etc/kernel/cmdline.d/90-lsm.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_selinux/file.include/etc/kernel/cmdline.d/90-lsm.cfg) ([`file.include`](/reference/features/#file-include)) | Sets `lsm=selinux` on the kernel command line to activate SELinux at boot. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

