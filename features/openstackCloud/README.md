---
title: "Feature: openstackCloud"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/openstackCloud/README.md
github_target_path: docs/reference/features/openstackCloud.md
---

## Feature: openstackCloud

### Description

A feature providing [OpenStack](/reference/glossary#openstack) cloud-specific configuration for environments using [VMware ESXi](/reference/glossary#vmware) as the hypervisor.

:::warning
This is a reference implementation! Adapt to your specific OpenStack environment.
:::

### What it does

Installs `open-vm-tools` and `numactl`. Configures cloud-init to disable network management (networking is handled by systemd) and sets the console parameter for OpenStack. This element targets OpenStack on VMware ESXi hypervisors specifically.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstackCloud/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstackCloud/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstackCloud/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `open-vm-tools`, `numactl`. |
| [`file.include/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstackCloud/file.include/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg) ([`file.include`](/reference/features/#file-include)) | Disables cloud-init network configuration management (networking is handled by systemd-networkd). |
| [`file.include/etc/kernel/cmdline.d/10-console.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstackCloud/file.include/etc/kernel/cmdline.d/10-console.cfg) ([`file.include`](/reference/features/#file-include)) | Sets the kernel console parameter for OpenStack. |

### Related features

**Includes:**

- [`cloud`](/reference/features/cloud) — provides common cloud infrastructure, kernel, and networking configuration.

### Further reading

- [cloud-init documentation](https://cloudinit.readthedocs.io/)

## Related topics

<RelatedTopics />

