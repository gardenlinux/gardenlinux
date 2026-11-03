---
title: "Feature: azure"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/azure/README.md
github_target_path: docs/reference/features/azure.md
---

## Feature: azure

### Description

A [platform](/reference/glossary.html#platform) feature that builds a Garden Linux
image for [Microsoft Azure](/reference/glossary#azure). Artifacts are delivered as `.raw` and `.vhd` files.

### What it does

Installs `cloud-init` and `azure-vm-utils` for instance initialization on Azure
and configures platform-specific settings:

- **Time synchronization**: uses `chrony` (instead of `systemd-timesyncd`,
  which is excluded) synchronized to the Hyper-V PTP clock device.
- **Cloud-init**: removes `growpart`, `resizefs`, and `ntp` modules (partition
  growth is handled in the initramfs; NTP is managed by `chrony`).
- **Kernel command line**: sets console and NVMe timeout parameters for the
  Azure environment.
- **NVMe**: includes NVMe modules in the initramfs via a dracut drop-in.
- **Network**: marks Azure-managed network devices as unmanaged so that
  systemd-networkd does not interfere with them.
- **Image conversion**: `convert.vhd` produces a fixed-size `.vhd` image for
  Azure.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`convert.vhd`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/convert.vhd) ([ref](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Converts the `.raw` artifact to a fixed-size `.vhd` image for Azure import. |
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Strips `growpart`, `resizefs`, and `ntp` modules from `cloud-init` configuration and disables cloud-init network management. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes the `systemd-timesyncd` override and the `udf` module blacklist from the rootfs. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: platform` and included/excluded features. |
| [`pkg.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/pkg.exclude) ([ref](/reference/features/#pkg-exclude)) | Prevents installation of `systemd-timesyncd` (replaced by `chrony`). |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `chrony`, `cloud-init`, `azure-vm-utils`, `python3-passlib`, and `python3-cffi-backend`. |
| [`file.include/etc/chrony/chrony.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/file.include/etc/chrony/chrony.conf) ([`file.include`](/reference/features/#file-include)) | Configures `chrony` to use the Hyper-V PTP clock device (`/dev/ptp_hyperv`) as the primary time source. |
| [`file.include/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/file.include/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg) ([`file.include`](/reference/features/#file-include)) | Debian-specific cloud-init configuration baseline. |
| [`file.include/etc/dracut.conf.d/67-azure-nvme-modules.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/file.include/etc/dracut.conf.d/67-azure-nvme-modules.conf) ([`file.include`](/reference/features/#file-include)) | Includes Azure NVMe kernel modules in the initramfs. |
| [`file.include/etc/kernel/cmdline.d/10-console.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/file.include/etc/kernel/cmdline.d/10-console.cfg) ([`file.include`](/reference/features/#file-include)) | Sets the kernel console parameter for the Azure serial console. |
| [`file.include/etc/kernel/cmdline.d/45-nvme-timeout.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/file.include/etc/kernel/cmdline.d/45-nvme-timeout.cfg) ([`file.include`](/reference/features/#file-include)) | Sets NVMe I/O timeout parameters for Azure storage. |
| [`file.include/etc/systemd/99-azure-unmanaged-devices.network`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/file.include/etc/systemd/99-azure-unmanaged-devices.network) ([`file.include`](/reference/features/#file-include)) | Marks Azure-internal network interfaces as unmanaged by systemd-networkd. |
| [`file.include/etc/systemd/system/chronyd.service.d/10-after_dev-ptp_hyperv.device.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/file.include/etc/systemd/system/chronyd.service.d/10-after_dev-ptp_hyperv.device.conf) ([`file.include`](/reference/features/#file-include)) | Orders `chronyd` to start after the Hyper-V PTP device is available. |
| [`file.include/etc/systemd/system-preset/00-chrony-disable.preset`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/file.include/etc/systemd/system-preset/00-chrony-disable.preset) ([`file.include`](/reference/features/#file-include)) | Disables `chronyd` by default so it is only activated when the PTP device is present. |
| [`file.include/etc/udev/rules.d/60-hyperv-ptp.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/file.include/etc/udev/rules.d/60-hyperv-ptp.rules) ([`file.include`](/reference/features/#file-include)) | Creates a stable `/dev/ptp_hyperv` symlink when the Hyper-V PTP device appears. |
| [`file.include/etc/udev/rules.d/66-azure-storage.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/file.include/etc/udev/rules.d/66-azure-storage.rules) ([`file.include`](/reference/features/#file-include)) | Sets Azure storage device attributes via udev. |
| [`file.include/etc/udev/rules.d/99-azure-product-uuid.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/azure/file.include/etc/udev/rules.d/99-azure-product-uuid.rules) ([`file.include`](/reference/features/#file-include)) | Makes the Azure product UUID available as a udev property for cloud-init. |

### Related features

**Includes:**

- [`cloud`](/reference/features/cloud) — provides common cloud-init integration and base cloud configuration shared across cloud platforms.

### Further reading

- [cloud-init documentation](https://cloudinit.readthedocs.io/)
- [azure-vm-utils](https://github.com/microsoft/azure-vm-utils)
- [chrony documentation](https://chrony-project.org/documentation.html)
- [Linux PTP project](https://linuxptp.nwtime.org/)

## Related topics

<RelatedTopics />

