---
title: "Feature: cloudInit"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/cloudInit/README.md
github_target_path: docs/reference/features/cloudInit.md
---

## Feature: cloudInit

### Description

A shared [element](/reference/glossary.html#element) feature that installs `cloud-init` and ships a
hook that recreates the cloud-init default user after an `/etc` overlay reset (see [USI in-place updates](/reference/features/_usi)).

### What it does

- Installs `cloud-init`.
- Ships `/usr/lib/gardenlinux/etc-setup-hooks/00-cloud-init-useradd`, a hook that runs after an
  `/etc` reset to recreate the default user (name, UID, GID, shell, supplementary groups, and sudo
  rule) derived from the surviving `/home/<user>` directory and the static cloud-init configuration.
- Ships a systemd drop-in (`gardenlinux-etc-setup-hooks.service.d/10-after-cloud-config.conf`) that
  orders the etc-setup-hooks service after `cloud-config.service`, so the hook observes cloud-init's
  final state without racing it.

### Files

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloudInit/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element`. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloudInit/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `cloud-init`. |
| [`file.include/usr/lib/gardenlinux/etc-setup-hooks/00-cloud-init-useradd`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloudInit/file.include/usr/lib/gardenlinux/etc-setup-hooks/00-cloud-init-useradd) ([`file.include`](/reference/features/#file-include)) | Hook that recreates the cloud-init default user after an `/etc` reset. |
| [`file.include/etc/systemd/system/gardenlinux-etc-setup-hooks.service.d/10-after-cloud-config.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloudInit/file.include/etc/systemd/system/gardenlinux-etc-setup-hooks.service.d/10-after-cloud-config.conf) ([`file.include`](/reference/features/#file-include)) | Systemd drop-in ordering the hook service after `cloud-config.service`. |

### Related features

**Included by:**

- [`ali`](/reference/features/ali), [`aws`](/reference/features/aws), [`azure`](/reference/features/azure), [`gdch`](/reference/features/gdch), [`lima`](/reference/features/lima), [`openstack`](/reference/features/openstack), [`stackit`](/reference/features/stackit), [`vmware`](/reference/features/vmware) — cloud platform features that rely on cloud-init for instance initialization.

**Works with:**

- [`_usi`](/reference/features/_usi) — provides the `/etc` overlay reset mechanism and the etc-setup-hooks runner that executes this feature's hook.

## Related topics

<RelatedTopics />
