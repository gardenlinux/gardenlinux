---
title: "Feature: nvme"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/nvme/README.md
github_target_path: docs/reference/features/nvme.md
---

## Feature: nvme

### Description

Adds NVMe Command Line Interface (CLI) tooling and configures NVMe host identifiers.

### What it does

Installs `nvme-cli` and `cryptsetup`. Provides a systemd service (`nvme-hostid.service`) that generates `/etc/nvme/hostnqn` and `/etc/nvme/hostid` on first boot — equivalent to what the `nvme-cli` Debian package postinst script normally does, allowing images to be built without running the package scripts.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/nvme/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/nvme/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/nvme/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `cryptsetup`, `nvme-cli`. |
| [`file.include/etc/systemd/system/nvme-hostid.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/nvme/file.include/etc/systemd/system/nvme-hostid.service) ([`file.include`](/reference/features/#file-include)) | Generates `/etc/nvme/hostnqn` and `/etc/nvme/hostid` unique identifiers at first boot. |

### Related features

**Includes:**

- [`multipath`](/reference/features/multipath) — multipath I/O support used with NVMe over Fabrics (NVMe-oF/TCP).

## Related topics

<RelatedTopics />

