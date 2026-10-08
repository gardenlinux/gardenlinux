---
title: "Feature: chost"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/chost/README.md
github_target_path: docs/reference/features/chost.md
---

## Feature: chost

### Description

The `chost` feature adjusts Garden Linux to support running [OCI containers](/reference/glossary#oci-oci-image-format) and [Kubernetes](/reference/glossary#kubernetes) workloads.

### What it does

The `chost` feature adjusts Garden Linux to support running container and Kubernetes workloads and installs and configures all related packages like `containerd`. It enables the overlay filesystem, bridge netfilter, and IP tables kernel modules, and configures IP forwarding for pod networking. AppArmor is installed for container security. The default `containerd` configuration file is removed so that Gardener or other orchestrators can supply their own.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/chost/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes from rootfs: `/etc/init.d/apparmor`, `/var/lib/containerd/opt`. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/chost/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/chost/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/chost/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `apparmor`, `containerd`, `ethtool`, `dbus-user-session`. |
| [`file.include/etc/crictl.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/chost/file.include/etc/crictl.yaml) ([`file.include`](/reference/features/#file-include)) | Configuration for `crictl`, the container runtime CLI tool for interacting with containerd. |
| [`file.include/etc/containerd/config.toml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/chost/file.include/etc/containerd/config.toml) ([`file.include`](/reference/features/#file-include)) | Default `containerd` configuration, including runtime and snapshot settings. |
| [`file.include/etc/modprobe.d/overlayfs.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/chost/file.include/etc/modprobe.d/overlayfs.conf) ([`file.include`](/reference/features/#file-include)) | Loads the `overlay` kernel module required for container image layering. |
| [`file.include/etc/modules-load.d/br_netfilter.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/chost/file.include/etc/modules-load.d/br_netfilter.conf) ([`file.include`](/reference/features/#file-include)) | Loads the `br_netfilter` kernel module at boot for bridge-based container networking. |
| [`file.include/etc/modules-load.d/ip_tables.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/chost/file.include/etc/modules-load.d/ip_tables.conf) ([`file.include`](/reference/features/#file-include)) | Loads the `ip_tables` kernel module at boot for container network policy. |
| [`file.include/etc/modules-load.d/overlay.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/chost/file.include/etc/modules-load.d/overlay.conf) ([`file.include`](/reference/features/#file-include)) | Loads the `overlay` filesystem kernel module at boot. |
| [`file.include/etc/sysctl.d/ip-forward.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/chost/file.include/etc/sysctl.d/ip-forward.conf) ([`file.include`](/reference/features/#file-include)) | Enables IPv4 and IPv6 forwarding for pod-to-pod networking. |
| [`file.include/etc/sysctl.d/nf-call-iptables.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/chost/file.include/etc/sysctl.d/nf-call-iptables.conf) ([`file.include`](/reference/features/#file-include)) | Enables iptables calls on bridge traffic, required for Kubernetes network policy. |
| [`file.include/etc/systemd/system/containerd.service.d/override.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/chost/file.include/etc/systemd/system/containerd.service.d/override.conf) ([`file.include`](/reference/features/#file-include)) | systemd override that sets containerd startup dependencies and resource limits. |
| [`file.include/opt/cni/bin`](https://github.com/gardenlinux/gardenlinux/blob/main/features/chost/file.include/opt/cni/bin) ([`file.include`](/reference/features/#file-include)) | Directory placeholder for Container Network Interface (CNI) plugin binaries. |
| [`file.include/usr/lib/cni`](https://github.com/gardenlinux/gardenlinux/blob/main/features/chost/file.include/usr/lib/cni) ([`file.include`](/reference/features/#file-include)) | Directory placeholder for system-level CNI plugin libraries. |

### Related features

**Includes:**

- [`server`](/reference/features/server) — provides the base server configuration required for container hosting.

## Related topics

<RelatedTopics />

