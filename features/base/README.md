---
title: "Feature: base"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/base/README.md
github_target_path: docs/reference/features/base.md
---

## Feature: base

### Description

This feature installs the `base` layer for Garden Linux.

### What it does

All artifacts and images are based on the `base` layer, which represents a minimal setup to run the OS itself. This is achieved by debootstrapping the `minbase` variant. Within this feature all OS-related base configurations (which may still be adjusted by other features on top of it) are applied.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Applies base OS configuration: locale, APT settings, and initial system setup. |
| [`exec.post`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/exec.post) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Post-build cleanup: removes package caches and build-time artifacts. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes from rootfs: `/etc/group-`, `/etc/gshadow-`, `/etc/passwd-`, `/etc/shadow-`, `/etc/subgid-`, ... (11 total). |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`fstab`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/fstab) ([ref](/reference/features/#fstab-fstab-mod)) | Defines partition layout. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/pkg.exclude) ([ref](/reference/features/#pkg-exclude)) | Prevents installation of: `gcc-9-base`, `gcc-10-base`, `gcc-11-base`. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `garden-repo-manager`, `rng-tools`. |
| [`file.include/etc/ucf.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.include/etc/ucf.conf) ([`file.include`](/reference/features/#file-include)) | Configuration for `ucf` (Update Configuration File), controlling how config file updates are handled during package upgrades. |
| [`file.include/etc/veritytab`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.include/etc/veritytab) ([`file.include`](/reference/features/#file-include)) | dm-verity table definition for read-only verified root filesystem support. |
| [`file.include/etc/apt/apt.conf.d/autoclean`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.include/etc/apt/apt.conf.d/autoclean) ([`file.include`](/reference/features/#file-include)) | APT configuration to automatically clean the package cache after installs. |
| [`file.include/etc/apt/apt.conf.d/gzip-indexes`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.include/etc/apt/apt.conf.d/gzip-indexes) ([`file.include`](/reference/features/#file-include)) | APT configuration to store package indexes in compressed form to reduce disk usage. |
| [`file.include/etc/apt/apt.conf.d/no-caches`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.include/etc/apt/apt.conf.d/no-caches) ([`file.include`](/reference/features/#file-include)) | APT configuration that disables caching of downloaded packages. |
| [`file.include/etc/apt/apt.conf.d/no-languages`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.include/etc/apt/apt.conf.d/no-languages) ([`file.include`](/reference/features/#file-include)) | APT configuration that disables downloading of translation files. |
| [`file.include/etc/apt/apt.conf.d/no-recommends`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.include/etc/apt/apt.conf.d/no-recommends) ([`file.include`](/reference/features/#file-include)) | APT configuration that disables automatic installation of recommended packages. |
| [`file.include/etc/apt/apt.conf.d/no-suggests`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.include/etc/apt/apt.conf.d/no-suggests) ([`file.include`](/reference/features/#file-include)) | APT configuration that disables automatic installation of suggested packages. |
| [`file.include/etc/apt/preferences.d/gardenlinux`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.include/etc/apt/preferences.d/gardenlinux) ([`file.include`](/reference/features/#file-include)) | APT pinning preferences for the Garden Linux repository. |
| [`file.include/etc/dpkg/dpkg.cfg.d/forceold`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.include/etc/dpkg/dpkg.cfg.d/forceold) ([`file.include`](/reference/features/#file-include)) | dpkg configuration to keep existing configuration files when packages are updated. |
| [`file.include/etc/dpkg/dpkg.cfg.d/speedup`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.include/etc/dpkg/dpkg.cfg.d/speedup) ([`file.include`](/reference/features/#file-include)) | dpkg configuration that speeds up installation by disabling certain checks. |
| [`file.include/etc/dpkg/origins/gardenlinux`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.include/etc/dpkg/origins/gardenlinux) ([`file.include`](/reference/features/#file-include)) | Declares Garden Linux as the OS origin for dpkg. |
| [`file.include/etc/sysctl.d/10-disable-sysrq.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.include/etc/sysctl.d/10-disable-sysrq.conf) ([`file.include`](/reference/features/#file-include)) | Disables the SysRq key to prevent privileged keyboard shortcuts on physical consoles. |
| [`file.include/var/www/.gitignore`](https://github.com/gardenlinux/gardenlinux/blob/main/features/base/file.include/var/www/.gitignore) ([`file.include`](/reference/features/#file-include)) | Placeholder that ensures `/var/www` exists in the rootfs. |

### Related features

**Includes:**

- [`_slim`](/reference/features/_slim) — provides a slimmed-down package selection for minimal images.

## Related topics

<RelatedTopics />

