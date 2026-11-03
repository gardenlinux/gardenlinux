---
title: "Feature: cisModprobe"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/cisModprobe/README.md
github_target_path: docs/reference/features/cisModprobe.md
---

## Feature: cisModprobe

### Description

A sub-feature of [`cis`](/reference/features/cis) that denies kernel modules per [CIS benchmark](/reference/glossary#cis-center-for-internet-security) requirements. Must be used with the [`cis`](/reference/features/cis) feature.

### What it does

Denies the following kernel modules: `cramfs`, `dccp`, `freevxfs`, `jffs2`, `rds`, `sctp`, `squashfs`, `tipc`, `udf`. Note: `fat` is not denied despite the CIS recommendation, as it is required for UEFI boot.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisModprobe/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisModprobe/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`file.include/etc/modprobe.d/cramfs.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisModprobe/file.include/etc/modprobe.d/cramfs.conf) ([`file.include`](/reference/features/#file-include)) | Denylists the `cramfs` filesystem module per CIS benchmark. |
| [`file.include/etc/modprobe.d/dccp.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisModprobe/file.include/etc/modprobe.d/dccp.conf) ([`file.include`](/reference/features/#file-include)) | Denylists the `dccp` network protocol module per CIS benchmark. |
| [`file.include/etc/modprobe.d/freevxfs.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisModprobe/file.include/etc/modprobe.d/freevxfs.conf) ([`file.include`](/reference/features/#file-include)) | Denylists the `freevxfs` filesystem module per CIS benchmark. |
| [`file.include/etc/modprobe.d/jffs2.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisModprobe/file.include/etc/modprobe.d/jffs2.conf) ([`file.include`](/reference/features/#file-include)) | Denylists the `jffs2` filesystem module per CIS benchmark. |
| [`file.include/etc/modprobe.d/rds.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisModprobe/file.include/etc/modprobe.d/rds.conf) ([`file.include`](/reference/features/#file-include)) | Denylists the `rds` network protocol module per CIS benchmark. |
| [`file.include/etc/modprobe.d/sctp.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisModprobe/file.include/etc/modprobe.d/sctp.conf) ([`file.include`](/reference/features/#file-include)) | Denylists the `sctp` network protocol module per CIS benchmark. |
| [`file.include/etc/modprobe.d/squashfs.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisModprobe/file.include/etc/modprobe.d/squashfs.conf) ([`file.include`](/reference/features/#file-include)) | Denylists the `squashfs` filesystem module per CIS benchmark. |
| [`file.include/etc/modprobe.d/tipc.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisModprobe/file.include/etc/modprobe.d/tipc.conf) ([`file.include`](/reference/features/#file-include)) | Denylists the `tipc` network protocol module per CIS benchmark. |
| [`file.include/etc/modprobe.d/udf.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisModprobe/file.include/etc/modprobe.d/udf.conf) ([`file.include`](/reference/features/#file-include)) | Denylists the `udf` filesystem module per CIS benchmark. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

