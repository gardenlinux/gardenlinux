---
title: "Feature: _iso"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_iso/README.md
github_target_path: docs/reference/features/_iso.md
---

## Feature: _iso

### Description
<website-feature>
Creates a bootable `.iso` artifact for use on physical hardware, virtual machines, or USB media.
</website-feature>

### Features
This feature creates a hybrid bootable ISO with:
- UEFI boot support (systemd-boot with UKI)
- Legacy BIOS boot support (syslinux/isolinux)
- Live root filesystem (squashfs in `/live/squashfs.img`)
- Auto-login as root on console

Includes [`_install`](/reference/features/_install) for disk installation capability.

For automatic installation on boot, combine with [`_autoinstall`](/reference/features/_autoinstall).

### Unit testing
This feature does not support unit tests.

### Meta
|||
|---|---|
|type|flag|
|artifact|`.iso`|
|included_features|[`_install`](/reference/features/_install)|
|excluded_features|[`_selinux`](/reference/features/_selinux)|
