---
title: "Feature: gardener"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/gardener/README.md
github_target_path: docs/reference/features/gardener.md
---

## Feature: gardener

### Description

A feature that configures Garden Linux for [Gardener](/reference/glossary#gardener) [Kubernetes](/reference/glossary#kubernetes) cluster nodes. Garden Linux is the Container Node OS for Gardener.

### What it does

Installs `containerd`, Kubernetes tooling (`ipvsadm`, `ethtool`, `socat`), filesystem clients (`btrfs-progs`, `xfsprogs`, `nfs-common`, `cifs-utils`), and standard tools (`curl`, `jq`). Configures:

- [AppArmor](/reference/glossary#apparmor) as the Linux Security Module (replaces [SELinux](/reference/glossary#selinux))
- `containerd` service (disabled by default; Gardener enables it)
- `/usr` mounted as a separate read-only partition for immutability
- `dmesg` accessible to all users (Gardener requirement)
- IPVS kernel module loading
- `apt` daily timer disabled (Gardener manages updates)

Removes `/etc/containerd/config.toml` (Gardener provides its own) and `/etc/sysctl.d/40-restrict-dmesg.conf` (must allow dmesg).

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gardener/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Configures AppArmor LSM, enables `containerd`, disables the apt daily timer, and adjusts dmesg access. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gardener/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes from rootfs: `/etc/containerd/config.toml`, `/etc/sysctl.d/40-restrict-dmesg.conf`. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gardener/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`fstab.mod`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gardener/fstab.mod) ([ref](/reference/features/#fstab-fstab-mod)) | Adds a read-only `/usr` mount entry to the fstab for immutable filesystem support. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gardener/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gardener/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `apparmor`, `containerd`, `ethtool`, `ipvsadm`, `socat`, `curl`, `logrotate`, and others. |
| [`file.include/etc/kernel/cmdline.d/90-lsm.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gardener/file.include/etc/kernel/cmdline.d/90-lsm.cfg) ([`file.include`](/reference/features/#file-include)) | Sets AppArmor as the active Linux Security Module. |
| [`file.include/etc/modules-load.d/ipvs.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gardener/file.include/etc/modules-load.d/ipvs.conf) ([`file.include`](/reference/features/#file-include)) | Loads IPVS kernel modules at boot for Kubernetes load balancing. |
| [`file.include/etc/sysctl.d/40-allow-nonroot-dmesg.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gardener/file.include/etc/sysctl.d/40-allow-nonroot-dmesg.conf) ([`file.include`](/reference/features/#file-include)) | Allows non-root users to read dmesg (required by Gardener). |
| [`file.include/etc/systemd/system/containerd.service.d/override.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gardener/file.include/etc/systemd/system/containerd.service.d/override.conf) ([`file.include`](/reference/features/#file-include)) | Sets `containerd` start dependencies and resource limits. |
| [`file.include/etc/systemd/system-preset/91-disable-apt-daily.preset`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gardener/file.include/etc/systemd/system-preset/91-disable-apt-daily.preset) ([`file.include`](/reference/features/#file-include)) | Disables the apt daily timer (Gardener manages package updates). |

### Related features

**Includes:**

- [`server`](/reference/features/server) — base server configuration.
- [`sap`](/reference/features/sap) — SAP-specific configurations used in Gardener environments.
- [`iscsi`](/reference/features/iscsi) — iSCSI support for Kubernetes persistent volumes.
- [`nvme`](/reference/features/nvme) — NVMe support for Kubernetes persistent volumes.

**Excludes (incompatible with):**

- [`_selinux`](/reference/features/_selinux) — replaced by AppArmor as the Linux Security Module.
- [`firewall`](/reference/features/firewall) — Gardener manages networking; the nftables firewall conflicts with Kubernetes CNI networking.

### Further reading

- [Gardener](https://gardener.cloud)

## Related topics

<RelatedTopics />

