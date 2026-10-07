---
title: "Feature: sapmachine"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/sapmachine/README.md
github_target_path: docs/reference/features/sapmachine.md
---

## Feature: sapmachine

### Description

Installs [SapMachine](/reference/glossary#sapmachine), an OpenJDK release maintained and supported by SAP. 

### What it does

Adds the SapMachine package repository (using the GPG signing key in `sapmachine.key`) via `exec.late`, then installs `gnupg` for key handling. The SapMachine JDK itself is installed from the SapMachine repository.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.late`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sapmachine/exec.late) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Adds the SapMachine Debian package repository and imports its GPG signing key. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sapmachine/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sapmachine/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `gnupg`. |
| [`sapmachine.key`](https://github.com/gardenlinux/gardenlinux/blob/main/features/sapmachine/sapmachine.key) | GPG signing key for the SapMachine package repository. |

### Related features

**Includes:**

- [`_curl`](/reference/features/_curl) — provides `curl` for downloading the SapMachine repository configuration.

### Further reading

- [SapMachine documentation](https://sapmachine.io/)
- [SapMachine OCI Images based on Garden Linux](https://sapmachine.io/docs/docker-images)

## Related topics

<RelatedTopics />

