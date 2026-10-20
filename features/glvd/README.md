---
title: "Feature: glvd"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/glvd/README.md
github_target_path: docs/reference/features/glvd.md
---

## Feature: glvd

### Description

Provides the [Garden Linux Vulnerability Database (GLVD)](/reference/glossary#glvd) client for checking Garden Linux instances against known Vulnerabilities.

### What it does

Installs the `glvd` CLI tool. Run `glvd check` to see potential security issues for your Garden Linux version and installed packages. Also adds a MOTD script that displays a vulnerability summary at login.

Note: `glvd` is in development and requires an HTTPS connection to the `glvd` backend, which may delay SSH login.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/glvd/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/glvd/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/glvd/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `glvd`. |
| [`file.include/etc/update-motd.d/99-glvd`](https://github.com/gardenlinux/gardenlinux/blob/main/features/glvd/file.include/etc/update-motd.d/99-glvd) ([`file.include`](/reference/features/#file-include)) | MOTD script that displays a summary of potential security issues from the glvd vulnerability database. |

### Related features

This feature has no include or exclude relationships.

### Further reading

- [GLVD](https://github.com/gardenlinux/glvd)

## Related topics

<RelatedTopics />

