---
title: "Feature: _iso"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
  - /tutorials/on-premises/first-boot-bare-metal
  - /how-to/installation/on-premises/iso
  - /how-to/installation/on-premises/pxe-boot
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_iso/README.md
github_target_path: docs/reference/features/_iso.md
---

## Feature: _iso

### Description

Produces a hybrid bootable ISO artifact that supports both UEFI and legacy BIOS boot for use on physical hardware, virtual machines, or USB media.

### What it does

`_iso` assembles a bootable `.iso` image containing a live Garden Linux system. The ISO includes a compressed SquashFS root filesystem (`/live/squashfs.img`), a UEFI boot path using systemd-boot with a [Unified Kernel Image (UKI)](/reference/glossary.html#uki-unified-kernel-image), and a legacy BIOS boot path using syslinux/isolinux. Console autologin is enabled on both `tty1` and the serial console, so the live environment is accessible immediately without credentials.

The ISO includes [`_install`](/reference/features/_install) so the running live system can install Garden Linux to disk. For fully unattended installation, also add [`_autoinstall`](/reference/features/_autoinstall).

The feature uses `dracut` with the `dracut-live` module to build the initrd and `python3-pefi` (and related tools) to produce the UKI. `isolinux` provides the legacy BIOS boot support.

`_iso` is incompatible with [`_selinux`](/reference/features/_selinux) because SELinux extended-attribute labeling cannot be applied to the live SquashFS environment at build time.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_iso/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files in this feature to test-coverage marker IDs. |
| [`image.iso`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_iso/image.iso) ([ref](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Build script that assembles the final `.iso` file from the rootfs, bootloader, and live SquashFS. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_iso/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag`, artifact `.iso`, and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_iso/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `dracut`, `dracut-core`, `dracut-live`, `binutils`, `isolinux`, `python3-pefi`, and related tools needed to build the ISO. |
| [`file.include/etc/systemd/system/getty@tty1.service.d/autologin.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_iso/file.include/etc/systemd/system/getty@tty1.service.d/autologin.conf) ([`file.include`](/reference/features/#file-include)) | Configures `getty` on `tty1` for automatic root login in the live environment. |
| [`file.include/etc/systemd/system/serial-getty@.service.d/autologin.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_iso/file.include/etc/systemd/system/serial-getty@.service.d/autologin.conf) ([`file.include`](/reference/features/#file-include)) | Configures the serial `getty` for automatic root login on the serial console in the live environment. |

### Related features

**Includes:**

- [`_install`](/reference/features/_install) — Provides `/opt/install/install.sh` so the live ISO can install Garden Linux to disk.

**Excludes (incompatible with):**

- [`_selinux`](/reference/features/_selinux) — SELinux extended-attribute labeling is incompatible with the live SquashFS build process.

## Related topics

<RelatedTopics />

