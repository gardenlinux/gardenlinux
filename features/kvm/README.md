---
title: "Feature: kvm"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/kvm/README.md
github_target_path: docs/reference/features/kvm.md
---

## Feature: kvm

### Description

A [platform](/reference/glossary.html#platform) feature that builds Garden Linux
images for [KVM](/reference/glossary#kvm) and [QEMU](/reference/glossary#qemu) virtualization. Artifacts are delivered as `.raw` and
`.qcow2` files.

### What it does

Configures Garden Linux for KVM and QEMU guests:

- **QEMU guest agent**: installs `qemu-guest-agent` to enable host-guest
  communication (live migration signaling, in-guest command execution).
- **Kernel command line**: sets the console parameter for KVM serial consoles
  and enables Ignition-based first-boot configuration.
- **Ignition integration**: includes the `ignition-disable.service` unit to
  disable Ignition after first boot; the `_ignite` feature provides the full
  Ignition support.
- **FAT filesystem tools**: installs `dosfstools` for EFI partition management.
- **Filesystem cleanup**: removes stale initrd and kernel symlinks from the
  rootfs that are not needed in the image.

The `kvm` platform is also the recommended base for local unit testing that
requires a running OS.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/kvm/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Enables `ignition-disable.service`. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/kvm/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes stale `/initrd.img`, `/initrd.img.old`, `/vmlinuz`, and `/vmlinuz.old` symlinks from the rootfs. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/kvm/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/kvm/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: platform` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/kvm/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `dosfstools` and `qemu-guest-agent`. |
| [`file.include/etc/kernel/cmdline.d/10-console.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/kvm/file.include/etc/kernel/cmdline.d/10-console.cfg) ([`file.include`](/reference/features/#file-include)) | Sets the kernel console parameter for the KVM serial console. |
| [`file.include/etc/kernel/cmdline.d/50-ignition.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/kvm/file.include/etc/kernel/cmdline.d/50-ignition.cfg) ([`file.include`](/reference/features/#file-include)) | Enables Ignition-based first-boot configuration via kernel parameter. |
| [`file.include/etc/systemd/system/ignition-disable.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/kvm/file.include/etc/systemd/system/ignition-disable.service) ([`file.include`](/reference/features/#file-include)) | Systemd service that disables the Ignition kernel parameter after first boot. |
| [`file.include/etc/udev/rules.d/60-onmetal.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/kvm/file.include/etc/udev/rules.d/60-onmetal.rules) ([`file.include`](/reference/features/#file-include)) | udev rules for on-metal disk device naming in the KVM environment. |

### Related features

**Includes:**

- [`cloud`](/reference/features/cloud) — provides common cloud-init integration and base cloud configuration.
- [`_ignite`](/reference/features/_ignite) — provides Ignition-based first-boot configuration support.

### Further reading

- [cloud-init documentation](https://cloudinit.readthedocs.io/)
- [QEMU guest agent documentation](https://wiki.qemu.org/Features/GuestAgent)

## Related topics

<RelatedTopics />

