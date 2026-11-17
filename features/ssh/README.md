---
title: "Feature: ssh"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/ssh/README.md
github_target_path: docs/reference/features/ssh.md
---

## Feature: ssh

### Description

Adds the OpenSSH server (`openssh-server`) and `sshguard` to Garden Linux.

### What it does

Installs and configures OpenSSH and `sshguard` (brute-force protection). SSH host keys are removed at build time and regenerated at first boot via `ssh-keygen.service`. A Diffie-Hellman moduli regeneration service (`ssh-moduli.service`) generates strong DH parameters. The systemd SSH socket activation is disabled in favor of the traditional daemon mode. `sshguard` uses `nftables` (from the `firewall` feature); it falls back to `iptables` if available, or disables itself if neither is present.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ssh/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Disables SSH socket activation preset and configures `sshguard`. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ssh/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes from rootfs: `/etc/init.d/ssh`, `/etc/ssh/ssh_host_*`. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ssh/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ssh/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ssh/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `openssh-server`, `openssh-client`, `sshguard`, `python3-systemd`. |
| [`file.include/etc/ssh/ssh_config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ssh/file.include/etc/ssh/ssh_config) ([`file.include`](/reference/features/#file-include)) | SSH client configuration. |
| [`file.include/etc/ssh/sshd_config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ssh/file.include/etc/ssh/sshd_config) ([`file.include`](/reference/features/#file-include)) | SSH daemon configuration (cipher suites, authentication methods, hardening). |
| [`file.include/etc/systemd/system/ssh-keygen.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ssh/file.include/etc/systemd/system/ssh-keygen.service) ([`file.include`](/reference/features/#file-include)) | Generates SSH host keys on first boot. |
| [`file.include/etc/systemd/system/ssh-moduli.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ssh/file.include/etc/systemd/system/ssh-moduli.service) ([`file.include`](/reference/features/#file-include)) | Regenerates DH moduli for stronger SSH key exchange. |
| [`file.include/etc/systemd/system-preset/00-sshsocket-disable.preset`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ssh/file.include/etc/systemd/system-preset/00-sshsocket-disable.preset) ([`file.include`](/reference/features/#file-include)) | Disables SSH socket activation in favor of the traditional daemon mode. |

### Related features

**Includes:**

- [`firewall`](/reference/features/firewall) — nftables firewall used by `sshguard` for brute-force IP blocking.

## Related topics

<RelatedTopics />

