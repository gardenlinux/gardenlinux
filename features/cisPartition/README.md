---
title: "Feature: cisPartition"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/cisPartition/README.md
github_target_path: docs/reference/features/cisPartition.md
---

## Feature: cisPartition

### Description

A sub-feature of [`cis`](/reference/features/cis) that configures the partition layout per [CIS benchmark](/reference/glossary#cis-center-for-internet-security) requirements. Must be used with the [`cis`](/reference/features/cis) feature.

### What it does

Ships a CIS-compliant `fstab` with separate partitions for `/home`, `/var`, `/var/tmp`, `/var/log`, `/var/log/audit`, each mounted with `nosuid`, `noexec`, and `nodev`. Configures `/tmp` as a systemd mount unit with CIS-compliant mount options.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisPartition/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Enables relevant systemd mount units and applies partition-related configuration. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisPartition/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`fstab`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisPartition/fstab) ([ref](/reference/features/#fstab-fstab-mod)) | Defines the CIS-compliant partition layout with separate mounts for `/home`, `/var`, and audit paths. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisPartition/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`file.include/etc/systemd/system/tmp.mount`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisPartition/file.include/etc/systemd/system/tmp.mount) ([`file.include`](/reference/features/#file-include)) | Configures `/tmp` as a systemd-managed tmpfs with CIS-compliant mount options (`nosuid`, `noexec`, `nodev`). |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

