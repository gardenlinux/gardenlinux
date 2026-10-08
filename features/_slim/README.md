---
title: "Feature: _slim"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_slim/README.md
github_target_path: docs/reference/features/_slim.md
---

## Feature: _slim

### Description

Reduces the size of the Garden Linux artifact by removing man pages, locale data, and other non-essential files.

### What it does

`_slim` runs an `exec.late` script that deletes several directories from the image after package installation completes:

- `/usr/share/man` — manual pages
- `/usr/share/locale` — locale translation files
- `/usr/share/groff` — groff typesetting data
- `/usr/share/lintian` — Debian package linting data
- `/usr/share/linda` — additional linting data

These directories contain data that is useful during development but unnecessary in a production or space-constrained image. The resulting image is smaller and has a reduced set of user-facing documentation.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.late`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_slim/exec.late) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Removes man pages, locale files, and other non-essential shared data directories from the assembled rootfs. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_slim/file.exclude) ([ref](/reference/features/#file-exclude)) | Declares paths to remove from the rootfs: `/usr/share/man`, `/usr/share/locale`, `/usr/share/groff`, `/usr/share/lintian`, and `/usr/share/linda`. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_slim/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

