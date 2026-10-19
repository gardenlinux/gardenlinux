---
title: "Feature: sssd"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/sssd/README.md
github_target_path: docs/reference/features/sssd.md
---

## Feature: sssd

### Description

Installs the System Security Services Daemon (SSSD) for centralized identity and authentication management.

### What it does

Installs `sssd`, which provides authentication against identity sources such as LDAP, Active Directory, and Kerberos.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sssd/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sssd/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `sssd`. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

