---
title: "Feature: aide"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/aide/README.md
github_target_path: docs/reference/features/aide.md
---

## Feature: aide

### Description

This feature installs the host-based intrusion detection system AIDE (Advanced Intrusion Detection Environment).

### What it does

This feature installs the host-based intrusion detection system AIDE by adding a configuration file, as well as the related systemd unit files that ensure an AIDE database is created. AIDE is configured to run every night.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aide/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aide/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aide/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `aide`, `aide-common`. |
| [`file.include/etc/aide/aide.conf.d/30_aide_gl`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aide/file.include/etc/aide/aide.conf.d/30_aide_gl) ([`file.include`](/reference/features/#file-include)) | Garden Linux-specific AIDE configuration defining which files to monitor. |
| [`file.include/etc/systemd/system/aide-init.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aide/file.include/etc/systemd/system/aide-init.service) ([`file.include`](/reference/features/#file-include)) | systemd service that builds the initial AIDE database on first boot. |
| [`file.include/etc/systemd/system/aide-init.timer`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aide/file.include/etc/systemd/system/aide-init.timer) ([`file.include`](/reference/features/#file-include)) | systemd timer that triggers nightly AIDE database updates. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

