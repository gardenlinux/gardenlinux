---
title: "Feature: iscsi"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/iscsi/README.md
github_target_path: docs/reference/features/iscsi.md
---

## Feature: iscsi

### Description

Enables [iSCSI](/reference/glossary#iscsi) target and initiator support in Garden Linux.

### What it does

Installs `open-iscsi` (initiator) and `tgt` (target). Configures a template-based `initiatorname.iscsi` so a unique IQN (iSCSI Qualified Name) is generated at first boot via `iscsi-initiatorname.service`. The feature depends on `multipath` for multipath I/O support.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/iscsi/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Enables the `iscsi-initiatorname` service at boot. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/iscsi/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/iscsi/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/iscsi/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `lsscsi`, `open-iscsi`, `tgt`. |
| [`file.include/etc/iscsi/initiatorname.iscsi.template`](https://github.com/gardenlinux/gardenlinux/blob/main/features/iscsi/file.include/etc/iscsi/initiatorname.iscsi.template) ([`file.include`](/reference/features/#file-include)) | Template for generating a unique iSCSI IQN at first boot. |
| [`file.include/etc/systemd/system/iscsi-initiatorname.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/iscsi/file.include/etc/systemd/system/iscsi-initiatorname.service) ([`file.include`](/reference/features/#file-include)) | Generates `/etc/iscsi/initiatorname.iscsi` at first boot if not already present. |

### Related features

**Includes:**

- [`multipath`](/reference/features/multipath) — multipath I/O is required for reliable iSCSI connectivity.

## Related topics

<RelatedTopics />

