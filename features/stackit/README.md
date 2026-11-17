---
title: "Feature: stackit"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/stackit/README.md
github_target_path: docs/reference/features/stackit.md
---

## Feature: stackit

### Description

A [platform](/reference/glossary.html#platform) feature that builds a Garden Linux
image for [STACKIT](/reference/glossary#stackit), a cloud platform by Schwarz Group,
built on [OpenStack](/reference/glossary#openstack).
The artifact is delivered as a `.raw` file.

### What it does

Installs `cloud-init` and configures the OpenStack/ConfigDrive datasource for
instance initialization. Time synchronization is provided by `chrony` using the
KVM PTP hardware clock (`/dev/ptp_kvm`) via the `ptp_kvm` kernel module, which
offers nanosecond-level precision by reading the host clock directly via hypercall
— no NTP server is required. The `ptp_kvm` module is loaded at boot via
`modules-load.d` and a udev rule creates the stable `/dev/ptp_kvm` symlink that
`chrony` and systemd depend on.

Key configurations:

- **Time synchronization**: replaces `systemd-timesyncd` with `chrony` backed by
  the KVM PTP hardware clock.
- **Cloud-init datasource**: configures `ConfigDrive` and `OpenStack` as the
  primary datasources; disables cloud-init network management.
- **Cloud-init setup**: removes `growpart`, `resizefs`, and `ntp` modules (partition
  growth handled in the initramfs; NTP managed by `chrony`).
- **Platform variant**: writes `GARDENLINUX_PLATFORM_VARIANT=stackit` to
  `/etc/os-release`.
- **Architecture handling**: removes the `ptp_kvm` module-load configuration on
  `arm64`, where `ptp_kvm` is built-in rather than a loadable module.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Strips `growpart`, `resizefs`, and `ntp` from cloud-init; writes `GARDENLINUX_PLATFORM_VARIANT=stackit` to `/etc/os-release`; removes `ptp_kvm.conf` on `arm64`. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes from rootfs: the `systemd-timesyncd` service override and the `udf` module denylist (both are incompatible with the chrony/PTP setup). |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: platform` and included/excluded features. |
| [`pkg.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/pkg.exclude) ([ref](/reference/features/#pkg-exclude)) | Prevents installation of `systemd-timesyncd` (replaced by `chrony`). |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `cloud-init`, `chrony`, `dmidecode`, and `python3-cffi-backend`. |
| [`file.include/etc/chrony/chrony.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/file.include/etc/chrony/chrony.conf) ([`file.include`](/reference/features/#file-include)) | Configures `chrony` to use the KVM PTP hardware clock (`/dev/ptp_kvm`) as stratum-1 reference, providing nanosecond-level time synchronization without a network NTP server. |
| [`file.include/etc/cloud/ds-identify.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/file.include/etc/cloud/ds-identify.cfg) ([`file.include`](/reference/features/#file-include)) | Configures `ds-identify` to select the OpenStack datasource for cloud-init. |
| [`file.include/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/file.include/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg) ([`file.include`](/reference/features/#file-include)) | Debian-specific cloud-init configuration: default user (`admin`), sudo access, APT sources preservation, and hostname management. |
| [`file.include/etc/cloud/cloud.cfg.d/50-datasource.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/file.include/etc/cloud/cloud.cfg.d/50-datasource.cfg) ([`file.include`](/reference/features/#file-include)) | Restricts cloud-init datasource detection to `ConfigDrive`, `OpenStack`, and `Ec2`. |
| [`file.include/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/file.include/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg) ([`file.include`](/reference/features/#file-include)) | Disables cloud-init network configuration management (networking handled by systemd-networkd). |
| [`file.include/etc/kernel/cmdline.d/10-console.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/file.include/etc/kernel/cmdline.d/10-console.cfg) ([`file.include`](/reference/features/#file-include)) | Sets kernel console parameters for the STACKIT virtual serial console (`tty0` and `ttyS0`). |
| [`file.include/etc/modules-load.d/ptp_kvm.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/file.include/etc/modules-load.d/ptp_kvm.conf) ([`file.include`](/reference/features/#file-include)) | Loads the `ptp_kvm` kernel module at boot on `amd64` (removed on `arm64` where it is built-in). |
| [`file.include/etc/systemd/system/chronyd.service.d/10-after_dev-ptp_kvm.device.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/file.include/etc/systemd/system/chronyd.service.d/10-after_dev-ptp_kvm.device.conf) ([`file.include`](/reference/features/#file-include)) | Systemd drop-in that orders `chronyd` to start after the `dev-ptp_kvm.device` unit is available. |
| [`file.include/etc/systemd/system-preset/00-chrony-disable.preset`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/file.include/etc/systemd/system-preset/00-chrony-disable.preset) ([`file.include`](/reference/features/#file-include)) | Disables `chrony-wait.service` and `chronyd-restricted.service` by preset (not needed in this PTP-backed setup). |
| [`file.include/etc/udev/rules.d/60-kvm-ptp.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/stackit/file.include/etc/udev/rules.d/60-kvm-ptp.rules) ([`file.include`](/reference/features/#file-include)) | Creates a stable `/dev/ptp_kvm` symlink when the KVM PTP device appears and tags it as a systemd device unit (`dev-ptp_kvm.device`), enabling service ordering on it. |

### Related features

**Includes:**

- [`cloud`](/reference/features/cloud) — provides the cloud-optimized kernel, shared cloud configuration, and systemd-networkd networking used by all cloud platform features.

### Further reading

- [STACKIT hyperscaler](https://www.stackit.de/)
- [cloud-init documentation](https://cloudinit.readthedocs.io/)
- [chrony documentation](https://chrony-project.org/documentation.html)
- [Linux PTP project](https://linuxptp.nwtime.org/)

## Related topics

<RelatedTopics />

