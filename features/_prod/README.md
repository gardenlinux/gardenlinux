---
title: "Feature: _prod"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_prod/README.md
github_target_path: docs/reference/features/_prod.md
---

## Feature: _prod

### Description

Marks a Garden Linux image as a production artifact and sets settings for production environments.

### What it does

`_prod` signals that the resulting image is intended for production use.

In addition, `_prod` disables core dump generation through three complementary mechanisms: a `sysctl` configuration (`99-disable-core-dump.conf`), a `limits.conf` entry, and a `coredump.conf.d` drop-in for systemd-coredump. The `systemd-coredump` package and its service override files are also excluded entirely. This reduces the risk of sensitive data being written to disk in the event of a process crash.

A `file.include.markers.yaml` maps the installed configuration files to test-coverage markers for automated verification.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_prod/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes `systemd-coredump` service override files from the image. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_prod/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files in this feature to test-coverage marker IDs for production-readiness tests. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_prod/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag`. |
| [`pkg.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_prod/pkg.exclude) ([ref](/reference/features/#pkg-exclude)) | Prevents `systemd-coredump` from being installed. |
| [`file.include/etc/security/limits.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_prod/file.include/etc/security/limits.conf) ([`file.include`](/reference/features/#file-include)) | Sets `core` size limits to zero for all users, disabling core dump creation via PAM. |
| [`file.include/etc/sysctl.d/99-disable-core-dump.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_prod/file.include/etc/sysctl.d/99-disable-core-dump.conf) ([`file.include`](/reference/features/#file-include)) | Sets `kernel.core_pattern` and related sysctls to disable core dumps at the kernel level. |
| [`file.include/etc/systemd/coredump.conf.d/disable_coredump.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_prod/file.include/etc/systemd/coredump.conf.d/disable_coredump.conf) ([`file.include`](/reference/features/#file-include)) | Configures systemd-coredump to discard all core dumps. |

## Related topics

<RelatedTopics />

