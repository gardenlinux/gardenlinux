---
title: "Feature: proxmox"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/proxmox/README.md
github_target_path: docs/reference/features/proxmox.md
---

## Feature: proxmox

### Description

A feature that configures Garden Linux for Proxmox

### What it does

Installs, configures and enables `cloud-init`, `sshd` and serial access.

- Uses `_usi` and fixes #5579 which would wipe `/etc` on updates (proper solution is still outstanding)
- `/usr` mounted as a separate read-only partition for immutability

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/proxmox/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Enables the SSH and cloud-init presets, and disables cloud-init's `/etc/hosts` management. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/proxmox/file.exclude) ([ref](/reference/features/#file-exclude)) | Excludes kernel symlinks (`/initrd.img*`, `/vmlinuz*`) from the root filesystem. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/proxmox/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps the serial console and on-metal udev rule files to test-coverage marker IDs. |
| [`file.include/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/proxmox/file.include/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg) ([ref](/reference/features/#file-include)) | Configures the default cloud user as `admin` with passwordless sudo. |
| [`file.include/etc/cloud/cloud.cfg.d/99_pve.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/proxmox/file.include/etc/cloud/cloud.cfg.d/99_pve.cfg) ([ref](/reference/features/#file-include)) | Enables the NoCloud and ConfigDrive cloud-init data sources and disables host-file management. |
| [`file.include/etc/issue`](https://github.com/gardenlinux/gardenlinux/blob/main/features/proxmox/file.include/etc/issue) ([ref](/reference/features/#file-include)) | Displays the OS name, release, and network interface information on login. |
| [`file.include/etc/kernel/cmdline.d/10-console.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/proxmox/file.include/etc/kernel/cmdline.d/10-console.cfg) ([ref](/reference/features/#file-include)) | Configures serial and local console output, with architecture-specific early console settings. |
| [`file.include/etc/systemd/system-preset/50-enable-cloudinit.preset`](https://github.com/gardenlinux/gardenlinux/blob/main/features/proxmox/file.include/etc/systemd/system-preset/50-enable-cloudinit.preset) ([ref](/reference/features/#file-include)) | Enables `cloud-init.target` by default. |
| [`file.include/etc/systemd/system-preset/50-enable-sshd.preset`](https://github.com/gardenlinux/gardenlinux/blob/main/features/proxmox/file.include/etc/systemd/system-preset/50-enable-sshd.preset) ([ref](/reference/features/#file-include)) | Enables the SSH service by default. |
| [`file.include/etc/udev/rules.d/60-onmetal.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/proxmox/file.include/etc/udev/rules.d/60-onmetal.rules) ([ref](/reference/features/#file-include)) | Creates stable `/dev/onmetal/` and WWN-based disk symlinks for matching device serial numbers. |
| [`fstab.mod`](https://github.com/gardenlinux/gardenlinux/blob/main/features/proxmox/fstab.mod) ([ref](/reference/features/#fstab-fstab-mod)) | Replaces any existing `/usr` entry with a read-only mount. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/proxmox/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares the Proxmox platform artifact and its included features. |
| [`initrd.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/proxmox/initrd.config) | Patches the `_usi` initrd mount unit so `/usr` setup follows `sysroot-var.mount`. |
| [`initrd.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/proxmox/initrd.exclude) | Excludes the `_usi` overlay setup script and systemd service from the initrd. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/proxmox/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `dosfstools` and `qemu-guest-agent`. |

### Related features

**Includes:**

- [`server`](/reference/features/server) — base server configuration.
- [`cloud`](/reference/features/cloud) — provides base cloud configuration shared across cloud platforms.
- [`cloudInit`](/reference/features/cloudInit) — provides common cloud-init integration
- [`_usi`](/reference/features/_usi) — makes inplace upgrades possible


### Further reading


## Related topics

<RelatedTopics />

