---
title: "Feature: vhost"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/vhost/README.md
github_target_path: docs/reference/features/vhost.md
---

## Feature: vhost

### Description

Configures Garden Linux to host virtual machine workloads using [KVM](/reference/glossary#kvm) and [libvirt](/reference/glossary#libvirt).

### What it does

Installs KVM/QEMU and libvirt tooling including `qemu-system-x86` (amd64) or equivalent, `dnsmasq-base`, `dmidecode`. Configures the libvirt TLS socket to be disabled (not started by default). Sets up the environment for running and managing virtual machines via libvirt.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vhost/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vhost/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vhost/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `dmidecode`, `dnsmasq-base`, `qemu-system-x86` (amd64) or equivalent, and others. |
| [`file.include/etc/systemd/system-preset/00-disable-libvirtd-tls-socket.preset`](https://github.com/gardenlinux/gardenlinux/blob/main/features/vhost/file.include/etc/systemd/system-preset/00-disable-libvirtd-tls-socket.preset) ([`file.include`](/reference/features/#file-include)) | Disables the libvirt TLS socket activation by default. |

### Related features

**Includes:**

- [`server`](/reference/features/server) — provides the server base layer required for hypervisor operation.

## Related topics

<RelatedTopics />

