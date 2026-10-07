---
title: "Feature: clamav"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/clamav/README.md
github_target_path: docs/reference/features/clamav.md
---

## Feature: clamav

### Description

Installs and configures [ClamAV antivirus](/reference/glossary#clamav-antivirus).

### What it does

Installs `clamav`. Configures `freshclam` to keep virus definitions up to date. Schedules a nightly virus scan via a cron job in `/var/spool/cron/crontabs/root`. The cron schedule can be adjusted by editing that file.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/clamav/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/clamav/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/clamav/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `clamav`. |
| [`file.include/var/spool/cron/crontabs/root`](https://github.com/gardenlinux/gardenlinux/blob/main/features/clamav/file.include/var/spool/cron/crontabs/root) ([`file.include`](/reference/features/#file-include)) | Cron job that triggers a nightly ClamAV virus scan. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

