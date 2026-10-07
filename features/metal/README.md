---
title: "Feature: metal"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/metal/README.md
github_target_path: docs/reference/features/metal.md
---

## Feature: metal

### Description

A feature that provides standard kernel, physical hardware support, and server configuration for bare metal systems. Produces `.raw` and `.qcow2` artifacts. The feature is usually pulled in via the [`baremetal`](/reference/features/baremetal) platform feature.

### What it does

Installs the standard (non-cloud) kernel and physical hardware tooling: `lvm2`, `efibootmgr`, `efitools`, `ipmitool`, `ethtool`, `dosfstools`. Configures:

- Kernel command line and console settings for serial/physical consoles
- Microcode update hook (`postinst.d/00-ucode`)
- Monthly PCI/USB ID update cron jobs
- udev rules for network device naming and Intel LLDP
- Removes networking init.d scripts replaced by systemd-networkd

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Applies metal-specific configuration: removes legacy networking scripts and configures hardware services. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes from rootfs: `/etc/network`, `/etc/init.d/irqbalance`, `/etc/init.d/ipmievd`, `/etc/runit`, `/etc/sv`, ... (7 total). |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `ethtool`, `fdisk`, `lvm2`, `dosfstools`, `efibootmgr`, `efitools`, `ipmitool`, and others. |
| [`file.include/etc/cron.monthly/update-pciids`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/file.include/etc/cron.monthly/update-pciids) ([`file.include`](/reference/features/#file-include)) | Monthly cron job to update the PCI device IDs database. |
| [`file.include/etc/cron.monthly/update-usbids`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/file.include/etc/cron.monthly/update-usbids) ([`file.include`](/reference/features/#file-include)) | Monthly cron job to update the USB device IDs database. |
| [`file.include/etc/kernel/entry-token`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/file.include/etc/kernel/entry-token) ([`file.include`](/reference/features/#file-include)) | Sets the boot entry token used by systemd-boot. |
| [`file.include/etc/kernel/cmdline.d/00-default.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/file.include/etc/kernel/cmdline.d/00-default.cfg) ([`file.include`](/reference/features/#file-include)) | Default kernel command line parameters for bare metal systems. |
| [`file.include/etc/kernel/cmdline.d/10-console.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/file.include/etc/kernel/cmdline.d/10-console.cfg) ([`file.include`](/reference/features/#file-include)) | Console parameters for physical servers (serial and virtual console). |
| [`file.include/etc/kernel/postinst.d/00-kernel-cmdline`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/file.include/etc/kernel/postinst.d/00-kernel-cmdline) ([`file.include`](/reference/features/#file-include)) | Regenerates the kernel command line after kernel updates. |
| [`file.include/etc/kernel/postinst.d/00-ucode`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/file.include/etc/kernel/postinst.d/00-ucode) ([`file.include`](/reference/features/#file-include)) | Updates CPU microcode after kernel installs. |
| [`file.include/etc/kernel/postinst.d/zz-update-syslinux`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/file.include/etc/kernel/postinst.d/zz-update-syslinux) ([`file.include`](/reference/features/#file-include)) | Updates the syslinux bootloader after kernel installs. |
| [`file.include/etc/kernel/postrm.d/zz-update-syslinux`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/file.include/etc/kernel/postrm.d/zz-update-syslinux) ([`file.include`](/reference/features/#file-include)) | Updates the syslinux bootloader after kernel removal. |
| [`file.include/etc/udev/rules.d/69-nostbyrot.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/file.include/etc/udev/rules.d/69-nostbyrot.rules) ([`file.include`](/reference/features/#file-include)) | udev rules for storage device naming. |
| [`file.include/etc/udev/rules.d/71-intellldp.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/file.include/etc/udev/rules.d/71-intellldp.rules) ([`file.include`](/reference/features/#file-include)) | udev rules for the Intel LLDP agent. |
| [`file.include/usr/sbin/update-usbids`](https://github.com/gardenlinux/gardenlinux/blob/main/features/metal/file.include/usr/sbin/update-usbids) ([`file.include`](/reference/features/#file-include)) | Script to update the USB device IDs database. |

### Related features

**Includes:**

- [`server`](/reference/features/server) — provides the server base layer.
- [`_legacy`](/reference/features/_legacy) — adds BIOS/legacy boot support for physical machines that may not support UEFI.
- [`_fwcfg`](/reference/features/_fwcfg) — provides `fw_cfg` support for QEMU/KVM metadata access.

**Excludes (incompatible with):**

- [`cloud`](/reference/features/cloud) — `cloud` and `metal` are mutually exclusive due to different kernels, networking, and hardware assumptions.
- [`openstackCloud`](/reference/features/openstackCloud) — `metal` is incompatible with OpenStack cloud-specific configuration.

## Related topics

<RelatedTopics />

