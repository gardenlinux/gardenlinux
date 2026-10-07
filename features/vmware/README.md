---
title: "Feature: vmware"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/vmware/README.md
github_target_path: docs/reference/features/vmware.md
---

## Feature: vmware

### Description

A [platform](/reference/glossary.html#platform) feature that builds a Garden Linux
image for [VMware](/reference/glossary#vmware) platforms. Artifacts are delivered as `.vmdk` and `.ova` files.

### What it does

Installs `cloud-init`, `open-vm-tools`, and a custom VMware GuestInfo datasource
for cloud-init, enabling instance metadata delivery via VMware GuestInfo variables.
Platform-specific configuration includes:

- **Cloud-init**: removes `growpart`, `resizefs`, and `ntp` modules; configures
  the VMware GuestInfo datasource; disables cloud-init network management on
  `arm64` where Ignition configuration is incompatible.
- **Kernel command line**: sets console and VMware-specific kernel parameters.
- **Ignition integration**: includes the `ignition-disable.service` unit and
  Ignition kernel parameter (disabled on `arm64`).
- **Image conversion**: `convert.ova` packages the `.vmdk` into an OVA archive
  using the `vmware.ovf.template` descriptor.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`convert.ova`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vmware/convert.ova) ([ref](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Packages the `.vmdk` disk image into an `.ova` archive using `vmware.ovf.template` and `make-ova`. |
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vmware/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Strips `growpart`, `resizefs`, and `ntp` from cloud-init; removes Ignition config on `arm64`; marks `libmspack0t64` as manually installed to prevent deborphan false positives. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vmware/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vmware/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: platform` and included/excluded features. |
| [`make-ova`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vmware/make-ova) | Script that assembles the `.ova` archive from the `.vmdk` and OVF descriptor. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vmware/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `cloud-init`, `open-vm-tools`, `dmidecode`, and `python3-cffi-backend`. |
| [`vmware.ovf.template`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vmware/vmware.ovf.template) | OVF descriptor template used by `make-ova` when creating the `.ova` archive. |
| [`file.include/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vmware/file.include/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg) ([`file.include`](/reference/features/#file-include)) | Debian-specific cloud-init configuration baseline. |
| [`file.include/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vmware/file.include/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg) ([`file.include`](/reference/features/#file-include)) | Disables cloud-init network configuration management. |
| [`file.include/etc/cloud/cloud.cfg.d/99_enabled-datasources.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vmware/file.include/etc/cloud/cloud.cfg.d/99_enabled-datasources.cfg) ([`file.include`](/reference/features/#file-include)) | Restricts cloud-init datasource detection to VMwareGuestInfo. |
| [`file.include/etc/kernel/cmdline.d/10-console.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vmware/file.include/etc/kernel/cmdline.d/10-console.cfg) ([`file.include`](/reference/features/#file-include)) | Sets the kernel console parameter for VMware serial consoles. |
| [`file.include/etc/kernel/cmdline.d/50-ignition.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vmware/file.include/etc/kernel/cmdline.d/50-ignition.cfg) ([`file.include`](/reference/features/#file-include)) | Enables Ignition-based first-boot configuration via kernel parameter. |
| [`file.include/etc/systemd/system/ignition-disable.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vmware/file.include/etc/systemd/system/ignition-disable.service) ([`file.include`](/reference/features/#file-include)) | Systemd service that disables the Ignition kernel parameter after first boot. |
| [`file.include/usr/bin/dscheck_VMwareGuestInfo`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vmware/file.include/usr/bin/dscheck_VMwareGuestInfo) ([`file.include`](/reference/features/#file-include)) | Helper script used by cloud-init `ds-identify` to detect the VMwareGuestInfo datasource. |
| [`file.include/usr/lib/python3/dist-packages/cloudinit/sources/DataSourceVMwareGuestInfo.py`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vmware/file.include/usr/lib/python3/dist-packages/cloudinit/sources/DataSourceVMwareGuestInfo.py) ([`file.include`](/reference/features/#file-include)) | Custom cloud-init datasource that reads instance metadata from VMware GuestInfo variables. |

### Related features

**Includes:**

- [`cloud`](/reference/features/cloud) — provides common cloud-init integration and base cloud configuration.
- [`_ignite`](/reference/features/_ignite) — provides Ignition-based first-boot configuration support.

### Further reading

- [open-vm-tools](https://github.com/vmware/open-vm-tools)
- [cloud-init documentation](https://cloudinit.readthedocs.io/)

## Related topics

<RelatedTopics />

