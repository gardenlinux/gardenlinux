---
title: "Feature: k3s"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/k3s/README.md
github_target_path: docs/reference/features/k3s.md
---

## Feature: k3s

### Description

A feature that provides packages and configuration for K3s-related workloads.

### What it does

Adds Kubernetes networking and storage utilities, configures IPVS modules and dmesg access, disables daily APT jobs, and adjusts systemd and host security settings. It also removes the default nftables configuration and dmesg restriction file.

Despite its name, this feature does not currently install K3s.
K3s and the configuration / setup mode depends on how this node is used.
Additionally including the k3s binary would add ~80MiB and would require the user to use the version provided here and not what ever version they have installed or the autoupdater has upgraded to.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/k3s/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Removes set-user-ID bits from the NFS and CIFS mount helpers, removes GCE reverse-path-filter settings when present, and applies APT service presets. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/k3s/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes the dmesg restriction sysctl and the default nftables configuration. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/k3s/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps the LSM command-line fragment, IPVS module list, and dmesg sysctl to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/k3s/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares this as an element and includes `iscsi` and `_selinux`. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/k3s/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `apparmor`, `ethtool`, `ipvsadm`, `socat`, `curl`, `logrotate`, `xfsprogs`, `btrfs-progs`, `jq`, `cifs-utils`, `nfs-common`, and `netcat-openbsd`. The `containerd` package not added as k3s includes it in the k3s binary. |
| [`file.include/etc/kernel/cmdline.d/90-lsm.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/k3s/file.include/etc/kernel/cmdline.d/90-lsm.cfg) ([`file.include`](/reference/features/#file-include)) | Adds `security=apparmor` to the kernel command line. |
| [`file.include/etc/modules-load.d/ipvs.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/k3s/file.include/etc/modules-load.d/ipvs.conf) ([`file.include`](/reference/features/#file-include)) | Loads IPVS scheduler and connection-tracking kernel modules. |
| [`file.include/etc/rancher/k3s/config.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/k3s/file.include/etc/rancher/k3s/config.yaml) ([`file.include`](/reference/features/#file-include)) | Enables SELinux support in K3s. The containerd endpoint and server metrics settings are commented out. |
| [`file.include/etc/sysctl.d/40-allow-nonroot-dmesg.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/k3s/file.include/etc/sysctl.d/40-allow-nonroot-dmesg.conf) ([`file.include`](/reference/features/#file-include)) | Allows non-root users to read the kernel message buffer. |
| [`file.include/etc/systemd/system-preset/91-disable-apt-daily.preset`](https://github.com/gardenlinux/gardenlinux/blob/main/features/k3s/file.include/etc/systemd/system-preset/91-disable-apt-daily.preset) ([`file.include`](/reference/features/#file-include)) | Disables the APT daily and daily-upgrade timers and services. |

### Related features

**Includes:**

- [`iscsi`](/reference/features/iscsi) — iSCSI support; this feature also includes `multipath` through `iscsi`.
- [`_selinux`](/reference/features/_selinux) — SELinux support, as declared in `info.yaml`.

## Related topics

<RelatedTopics />

