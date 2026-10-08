---
title: "Feature: _bfpxe"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_bfpxe/README.md
github_target_path: docs/reference/features/_bfpxe.md
---

## Feature: _bfpxe

### Description

Produces a PXE boot image for NVIDIA BlueField Data Processing Units (DPUs), using a SquashFS root filesystem.

### What it does

`_bfpxe` restricts the build to produce only the BlueField-specific PXE artifacts. Unlike the general [`_pxe`](/reference/features/_pxe) flag, this variant targets the NVIDIA BlueField DPU platform, which requires a compressed SquashFS root image for network boot. It includes [`_ignite`](/reference/features/_ignite) to enable Ignition-based first-boot configuration.

The `exec.config` script, the dracut live-boot modules, and network configuration files set up the PXE boot chain for the BlueField environment.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Configures the BlueField PXE build environment, adjusting dracut and network settings for the DPU platform. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes `/etc/repart.d/root.conf` from the rootfs so that disk partitioning is skipped in the PXE-only image. |
| [`image.pxe.tar.gz`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/image.pxe.tar.gz) ([ref](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Build script that assembles the PXE tarball (`vmlinuz`, `initrd`, `cmdline`, `root.squashfs`) for BlueField. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs network and filesystem packages required for the BlueField live-boot environment. |
| [`file.include/etc/dracut.conf.d/20-gl-live.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/file.include/etc/dracut.conf.d/20-gl-live.conf) ([`file.include`](/reference/features/#file-include)) | Configures dracut to build a live-boot initrd with SquashFS and overlay support. |
| [`file.include/etc/systemd/network/91-default.network`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/file.include/etc/systemd/network/91-default.network) ([`file.include`](/reference/features/#file-include)) | Default systemd-networkd configuration that brings up the network interface during PXE boot. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/any.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/any.conf) ([`file.include`](/reference/features/#file-include)) | Dracut module configuration for the Garden Linux live-boot module. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/cleanup.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/cleanup.sh) ([`file.include`](/reference/features/#file-include)) | Cleans up the live environment after the root filesystem has been mounted. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/gl-end.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/gl-end.service) ([`file.include`](/reference/features/#file-include)) | Systemd unit run in the initrd to finalize the live-boot sequence. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/is-live-image.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/is-live-image.sh) ([`file.include`](/reference/features/#file-include)) | Helper script that detects whether the system is booting as a live image. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/live-get-squashfs.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/live-get-squashfs.sh) ([`file.include`](/reference/features/#file-include)) | Downloads or locates the SquashFS root image during initrd execution. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/live-overlay-setup.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/live-overlay-setup.sh) ([`file.include`](/reference/features/#file-include)) | Sets up the writable overlay on top of the read-only SquashFS root. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/live-sysroot-generator.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/live-sysroot-generator.sh) ([`file.include`](/reference/features/#file-include)) | Generates the sysroot mount units for the live environment. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/module-setup.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/module-setup.sh) ([`file.include`](/reference/features/#file-include)) | Registers the Garden Linux live-boot dracut module and its dependencies. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/squash-mount-generator.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_bfpxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/squash-mount-generator.sh) ([`file.include`](/reference/features/#file-include)) | Generates the systemd mount unit for the SquashFS image during early boot. |

### Related features

**Includes:**

- [`_ignite`](/reference/features/_ignite) — Provides Ignition support for first-boot configuration of the BlueField system.

## Related topics

<RelatedTopics />

