---
title: "Feature: khost"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/khost/README.md
github_target_path: docs/reference/features/khost.md
---

## Feature: khost

### Description

Configures Garden Linux for running vanilla [Kubernetes](/reference/glossary#kubernetes) workloads as a Kubernetes host node.

### What it does

Installs and configures packages needed for a Kubernetes node: `conntrack`, `ipvsadm`, `socat`, `ethtool`, `apparmor`, `gnupg`. Configures:

- Bridge netfilter sysctl settings for Kubernetes networking
- IP forwarding for pod networking
- Inotify limits for large numbers of watches
- IPVS kernel module loading
- Removes AppArmor init.d script (managed by systemd instead)
- Modifies fstab to remove swap (Kubernetes requires no swap)

Requires `chost` for the container runtime.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.late`](https://github.com/gardenlinux/gardenlinux/blob/main/features/khost/exec.late) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Removes swap entries from fstab and performs late-stage Kubernetes node setup. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/khost/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes from rootfs: `/etc/init.d/apparmor` (AppArmor is managed via systemd). |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/khost/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`fstab.mod`](https://github.com/gardenlinux/gardenlinux/blob/main/features/khost/fstab.mod) ([ref](/reference/features/#fstab-fstab-mod)) | Removes the swap partition from fstab (Kubernetes requires no swap). |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/khost/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/khost/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `apparmor`, `conntrack`, `ethtool`, `ipvsadm`, `socat`, `gnupg`. |
| [`release.key`](https://github.com/gardenlinux/gardenlinux/blob/main/features/khost/release.key) | GPG signing key for a Kubernetes package repository. |
| [`file.include/etc/modules-load.d/br-nf.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/khost/file.include/etc/modules-load.d/br-nf.conf) ([`file.include`](/reference/features/#file-include)) | Loads the `br_netfilter` kernel module at boot for Kubernetes network policy. |
| [`file.include/etc/sysctl.d/20-br-nf.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/khost/file.include/etc/sysctl.d/20-br-nf.conf) ([`file.include`](/reference/features/#file-include)) | Enables bridge netfilter for Kubernetes network policy enforcement. |
| [`file.include/etc/sysctl.d/20-inotify.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/khost/file.include/etc/sysctl.d/20-inotify.conf) ([`file.include`](/reference/features/#file-include)) | Increases inotify watch limits for large Kubernetes deployments. |
| [`file.include/etc/sysctl.d/20-ip-forward.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/khost/file.include/etc/sysctl.d/20-ip-forward.conf) ([`file.include`](/reference/features/#file-include)) | Enables IP forwarding for pod-to-pod networking. |

### Related features

**Includes:**

- [`chost`](/reference/features/chost) — provides the container runtime (`containerd`) required by Kubernetes.

### Further reading

- [Kubernetes](https://kubernetes.io/)

## Related topics

<RelatedTopics />

