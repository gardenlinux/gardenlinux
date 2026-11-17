---
title: "Feature: stigDev"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/stigDev/README.md
github_target_path: docs/reference/features/stigDev.md
---

## Feature: stigDev

### Description

A feature that adds development access to a [Defense Information Systems Agency (DISA)](/reference/glossary#defense-information-systems-agency-disa) [Security Technical Implementation Guide (STIG)](/reference/glossary#security-technical-implementation-guide-stig) hardened image.  Adds an SSH server and `sudo` access for a development user on top of `stig`.

### What it does

Installs `openssh-server` and creates a sudoers entry for development access. Performs late-stage configuration to allow a development user to access the STIG-hardened system.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.late`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stigDev/exec.late) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Creates the development user and configures sudo access for STIG dev environments. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stigDev/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stigDev/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `openssh-server`. |
| [`file.include/etc/sudoers.d/user`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stigDev/file.include/etc/sudoers.d/user) ([`file.include`](/reference/features/#file-include)) | Grants a development user passwordless sudo access. |

### Related features

**Includes:**

- [`stig`](/reference/features/stig) — provides the STIG baseline security controls that this feature extends for development use.

## Related topics

<RelatedTopics />

