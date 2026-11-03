---
title: "Feature: _pxe"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
  - /tutorials/on-premises/first-boot-bare-metal
  - /how-to/installation/on-premises/iso
  - /how-to/installation/on-premises/pxe-boot
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_pxe/README.md
github_target_path: docs/reference/features/_pxe.md
---

## Feature: _pxe

### Description

Produces PXE network boot artifacts for Garden Linux, enabling live boot over the network with an optional disk installation capability.

### What it does

`_pxe` builds a `.pxe.tar.gz` archive containing the artifacts required for network booting: a compressed SquashFS root filesystem (`root.squashfs`), a Linux kernel (`vmlinuz`), an initial ramdisk (`initrd`), and a kernel command line file (`cmdline`). When combined with [`_trustedboot`](/reference/features/_trustedboot) or [`_unsigned`](/reference/features/_unsigned) for a [Unified System Image (USI)](/reference/glossary.html#usi-unified-system-image) build, a Unified Kernel Image (`boot.efi`) is also included.

The feature ships a custom dracut module (`98gardenlinux-live`) that handles fetching `root.squashfs` over HTTP at boot time and mounting it with a writable overlay. A default systemd-networkd configuration brings up the network interface during PXE boot.

`_pxe` includes [`_ignite`](/reference/features/_ignite) to support [Ignition](/reference/glossary#ignition)-based first-boot configuration.

By default, `_pxe` produces an ephemeral live boot environment. For disk installation capability, also include:

- [`_install`](/reference/features/_install) — interactive installation
- [`_autoinstall`](/reference/features/_autoinstall) — unattended installation (includes `_install`)

:::warning
`systemd-networkd-wait-online` is configured to mark the system online when at least one interface comes up. On systems with multiple NICs on different network segments, the SquashFS fetch may fail if the interface that comes up first is not the one connected to the PXE server.
:::

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Configures the image at build time for the PXE live-boot environment. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes `/etc/repart.d/root.conf` so that disk repartitioning is skipped in the PXE-only image. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files in this feature to test-coverage marker IDs. |
| [`image.pxe.tar.gz`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/image.pxe.tar.gz) ([ref](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Build script that assembles the PXE tarball from the rootfs artifacts. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag`, artifact `.pxe.tar.gz`, and included features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `curl`, `dosfstools`, `btrfs-progs`, `xfsprogs`, `dracut-network`, `ca-certificates`, and other packages needed for the live-boot and network environment. |
| [`file.include/etc/dracut.conf.d/20-gl-live.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/file.include/etc/dracut.conf.d/20-gl-live.conf) ([`file.include`](/reference/features/#file-include)) | Configures dracut to build a live-boot initrd with SquashFS and overlay support. |
| [`file.include/etc/dracut.conf.d/30-omit-cdc-ether.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/file.include/etc/dracut.conf.d/30-omit-cdc-ether.conf) ([`file.include`](/reference/features/#file-include)) | Omits the `cdc_ether` driver from the initrd to avoid conflicts with certain network adapters during PXE boot. |
| [`file.include/etc/kernel/cmdline.d/80-pxe.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/file.include/etc/kernel/cmdline.d/80-pxe.cfg) ([`file.include`](/reference/features/#file-include)) | Adds PXE-specific parameters to the kernel command line, including the SquashFS fetch URL. |
| [`file.include/etc/systemd/network/91-default.network`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/file.include/etc/systemd/network/91-default.network) ([`file.include`](/reference/features/#file-include)) | Default systemd-networkd configuration that brings up a network interface during early boot to fetch the SquashFS image. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/99-any.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/99-any.conf) ([`file.include`](/reference/features/#file-include)) | Dracut module configuration ensuring the Garden Linux live-boot module is included for any architecture. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/cleanup.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/cleanup.sh) ([`file.include`](/reference/features/#file-include)) | Cleans up the live environment after the root filesystem has been mounted. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/gl-end.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/gl-end.service) ([`file.include`](/reference/features/#file-include)) | Systemd unit run in the initrd to finalize the live-boot sequence. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/is-live-image.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/is-live-image.sh) ([`file.include`](/reference/features/#file-include)) | Helper script that detects whether the system is booting as a live image. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/live-get-squashfs.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/live-get-squashfs.sh) ([`file.include`](/reference/features/#file-include)) | Downloads the SquashFS root image from the PXE server during initrd execution. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/live-overlay-setup.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/live-overlay-setup.sh) ([`file.include`](/reference/features/#file-include)) | Sets up the writable overlay on top of the read-only SquashFS root. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/live-sysroot-generator.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/live-sysroot-generator.sh) ([`file.include`](/reference/features/#file-include)) | Generates the sysroot mount units needed to pivot into the live root filesystem. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/module-setup.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/module-setup.sh) ([`file.include`](/reference/features/#file-include)) | Registers the Garden Linux live-boot dracut module and its dependencies. |
| [`file.include/usr/lib/dracut/modules.d/98gardenlinux-live/squash-mount-generator.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_pxe/file.include/usr/lib/dracut/modules.d/98gardenlinux-live/squash-mount-generator.sh) ([`file.include`](/reference/features/#file-include)) | Generates the systemd mount unit for the SquashFS image during early boot. |

### Related features

**Includes:**

- [`_ignite`](/reference/features/_ignite) — Provides Ignition support for declarative first-boot configuration of the PXE-booted system.

## Related topics

<RelatedTopics />

