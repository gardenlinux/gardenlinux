---
title: "Feature: _install"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
  - /tutorials/on-premises/first-boot-bare-metal
  - /how-to/installation/on-premises/iso
  - /how-to/installation/on-premises/pxe-boot
  - /how-to/installation/on-premises/disk-layout
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_install/README.md
github_target_path: docs/reference/features/_install.md
---

## Feature: _install

### Description

Provides a generic installation framework that copies a running Garden Linux live environment to a physical disk.

### What it does

`_install` places an installation script (`install.sh`) and two `systemd-repart` partition layout files into `/opt/install/` inside the image. The installation script handles partitioning (using `systemd-repart`), filesystem creation, copying the live rootfs, and bootloader installation. It supports both interactive and non-interactive modes:

- **Interactive:** prompts the user to choose a target disk and an encryption password.
- **Non-interactive:** reads the target device from the `GL_INSTALL_TARGET` environment variable, enabling use by [`_autoinstall`](/reference/features/_autoinstall).

The script installs either a UEFI (systemd-boot) or legacy BIOS (syslinux) bootloader depending on the system firmware.

`_install` does not produce a standalone bootable image on its own. Combine it with [`_iso`](/reference/features/_iso) or [`_pxe`](/reference/features/_pxe) to create a live medium with installation capability, or add [`_autoinstall`](/reference/features/_autoinstall) for unattended installation.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_install/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files in this feature to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_install/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`file.include/opt/install/install.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_install/file.include/opt/install/install.sh) ([`file.include`](/reference/features/#file-include)) | Main installation script: partitions the disk, formats it, copies the rootfs, and installs the bootloader. |
| [`file.include/opt/install/repart/00-efi.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_install/file.include/opt/install/repart/00-efi.conf) ([`file.include`](/reference/features/#file-include)) | `systemd-repart` partition definition for the EFI System Partition (ESP). |
| [`file.include/opt/install/repart/10-root.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_install/file.include/opt/install/repart/10-root.conf) ([`file.include`](/reference/features/#file-include)) | `systemd-repart` partition definition for the root filesystem partition. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

