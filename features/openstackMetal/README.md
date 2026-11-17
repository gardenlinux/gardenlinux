---
title: "Feature: openstackMetal"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/openstackMetal/README.md
github_target_path: docs/reference/features/openstackMetal.md
---

## Feature: openstackMetal

### Description

A feature providing [OpenStack](/reference/glossary#openstack) bare-metal configuration. Use with the `metal` platform.

:::warning
This is a reference implementation! Adapt to your specific OpenStack environment.
:::

### What it does

Provides configuration for OpenStack on bare-metal hardware (Ironic): installs `netplan.io` and `rng-tools`, configures cloud-init networking via Netplan, loads Broadcom NIC drivers in the initramfs, disables the Nouveau GPU driver, and configures cloud-like sysctl and root partition settings for bare-metal deployment.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstackMetal/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstackMetal/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstackMetal/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `rng-tools`, `netplan.io`. |
| [`file.include/etc/cloud/cloud.cfg.d/65-network-config.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstackMetal/file.include/etc/cloud/cloud.cfg.d/65-network-config.cfg) ([`file.include`](/reference/features/#file-include)) | Configures cloud-init to use Netplan for network configuration. |
| [`file.include/etc/dracut.conf.d/49-include-bnxt-drivers.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstackMetal/file.include/etc/dracut.conf.d/49-include-bnxt-drivers.conf) ([`file.include`](/reference/features/#file-include)) | Includes Broadcom NIC (`bnxt_en`) drivers in the initramfs. |
| [`file.include/etc/kernel/cmdline.d/40-enable-swap-cgroup-accounting.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstackMetal/file.include/etc/kernel/cmdline.d/40-enable-swap-cgroup-accounting.cfg) ([`file.include`](/reference/features/#file-include)) | Enables swap cgroup accounting for memory management. |
| [`file.include/etc/modprobe.d/10-disallow-nouveau.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstackMetal/file.include/etc/modprobe.d/10-disallow-nouveau.conf) ([`file.include`](/reference/features/#file-include)) | Denylists the Nouveau GPU driver. |
| [`file.include/etc/profile.d/50-autologout.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstackMetal/file.include/etc/profile.d/50-autologout.sh) ([`file.include`](/reference/features/#file-include)) | Configures automatic session logout after inactivity. |
| [`file.include/etc/repart.d/root.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstackMetal/file.include/etc/repart.d/root.conf) ([`file.include`](/reference/features/#file-include)) | systemd-repart root partition definition for auto-growth. |
| [`file.include/etc/sysctl.d/20-cloud.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstackMetal/file.include/etc/sysctl.d/20-cloud.conf) ([`file.include`](/reference/features/#file-include)) | Cloud-optimized sysctl settings applied to this bare-metal OpenStack configuration. |

### Related features

This feature has no include or exclude relationships.

### Further reading

- [cloud-init documentation](https://cloudinit.readthedocs.io/)

## Related topics

<RelatedTopics />

