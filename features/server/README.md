---
title: "Feature: server"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/server/README.md
github_target_path: docs/reference/features/server.md
---

## Feature: server

### Description

A feature that provides the Garden Linux server layer: security services (`auditd`, SELinux), systemd-based service management, networking, and essential server tooling. Most platform features inherit `server` transitively.

### What it does

Installs a comprehensive set of server packages including `sudo`, `sysstat`, `dnsutils`, `iproute2`, `ca-certificates`. Configures:

- systemd-networkd with a default DHCP network and `networkd-wait-online` set to `--any`
- systemd-resolved with LLMNR and mDNS disabled
- PAM with Garden Linux-specific profiles
- Dracut for UEFI stub and general initramfs generation
- Kernel coredump and growfs service overrides
- kexec support
- MOTD scripts showing system information (hostname, kernel, load, network)
- Shell profiles: no command history, auto-logout timeout
- sudo configuration (`wheel` group, SSH agent forwarding)
- Removes numerous init.d and legacy service scripts superseded by systemd

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Configures PAM, enables systemd units, and applies server-specific settings. |
| [`exec.early`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/exec.early) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Early-stage configuration applied before packages are installed. |
| [`exec.post`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/exec.post) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Post-build step applied after all packages are installed. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes from rootfs: `/etc/ufw`, `/etc/init.d/auditd`, `/etc/init.d/dbus`, `/etc/monit`, `/etc/init.d/sudo`, ... (24 total). |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `adduser`, `bsdextrautils`, `ca-certificates`, `dnsutils`, `iproute2`, `iptables`, and others. |
| [`todo`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/todo) | Internal notes file (not rendered in docs). |
| [`file.include/etc/kernel-img.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/kernel-img.conf) ([`file.include`](/reference/features/#file-include)) | Kernel image configuration for bootloader scripts. |
| [`file.include/etc/locale.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/locale.conf) ([`file.include`](/reference/features/#file-include)) | Sets system locale. |
| [`file.include/etc/machine-id`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/machine-id) ([`file.include`](/reference/features/#file-include)) | Empty machine-id placeholder (regenerated at first boot). |
| [`file.include/etc/dracut.conf.d/25-uefi-stub.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/dracut.conf.d/25-uefi-stub.conf) ([`file.include`](/reference/features/#file-include)) | Configures dracut to produce a UEFI stub image. |
| [`file.include/etc/dracut.conf.d/general.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/dracut.conf.d/general.conf) ([`file.include`](/reference/features/#file-include)) | General dracut configuration for initramfs generation. |
| [`file.include/etc/profile.d/50-nohistory.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/profile.d/50-nohistory.sh) ([`file.include`](/reference/features/#file-include)) | Disables shell command history. |
| [`file.include/etc/sudoers.d/keepssh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/sudoers.d/keepssh) ([`file.include`](/reference/features/#file-include)) | Preserves `SSH_AUTH_SOCK` across sudo sessions. |
| [`file.include/etc/sudoers.d/wheel`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/sudoers.d/wheel) ([`file.include`](/reference/features/#file-include)) | Grants sudo access to the `wheel` group. |
| [`file.include/etc/sysctl.d/40-enable-unprivileged-user-namespaces.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/sysctl.d/40-enable-unprivileged-user-namespaces.conf) ([`file.include`](/reference/features/#file-include)) | Enables unprivileged user namespaces. |
| [`file.include/etc/sysctl.d/40-restrict-dmesg.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/sysctl.d/40-restrict-dmesg.conf) ([`file.include`](/reference/features/#file-include)) | Restricts dmesg output to root. |
| [`file.include/etc/sysctl.d/90-allow-ping-for-non-root-user.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/sysctl.d/90-allow-ping-for-non-root-user.conf) ([`file.include`](/reference/features/#file-include)) | Allows non-root users to send ICMP pings. |
| [`file.include/etc/systemd/network/99-default.network`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/systemd/network/99-default.network) ([`file.include`](/reference/features/#file-include)) | Default systemd-networkd DHCP configuration for all Ethernet interfaces. |
| [`file.include/etc/systemd/networkd.conf.d/00-gardenlinux-server.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/systemd/networkd.conf.d/00-gardenlinux-server.conf) ([`file.include`](/reference/features/#file-include)) | Global systemd-networkd settings for Garden Linux server. |
| [`file.include/etc/systemd/resolved.conf.d/00-disable-llmnr.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/systemd/resolved.conf.d/00-disable-llmnr.conf) ([`file.include`](/reference/features/#file-include)) | Disables LLMNR in systemd-resolved. |
| [`file.include/etc/systemd/resolved.conf.d/01-disable-mdns.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/systemd/resolved.conf.d/01-disable-mdns.conf) ([`file.include`](/reference/features/#file-include)) | Disables mDNS in systemd-resolved. |
| [`file.include/etc/systemd/system/kexec-load@.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/systemd/system/kexec-load@.service) ([`file.include`](/reference/features/#file-include)) | systemd service for loading a kexec kernel. |
| [`file.include/etc/systemd/system/tmp.mount`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/systemd/system/tmp.mount) ([`file.include`](/reference/features/#file-include)) | Configures `/tmp` as a systemd-managed tmpfs. |
| [`file.include/etc/systemd/system/systemd-coredump@.service.d/override.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/systemd/system/systemd-coredump@.service.d/override.conf) ([`file.include`](/reference/features/#file-include)) | Adjusts systemd-coredump behavior. |
| [`file.include/etc/systemd/system/systemd-growfs@.service.d/override.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/systemd/system/systemd-growfs@.service.d/override.conf) ([`file.include`](/reference/features/#file-include)) | Adjusts systemd-growfs ordering. |
| [`file.include/etc/systemd/system/systemd-networkd-wait-online.service.d/any.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/systemd/system/systemd-networkd-wait-online.service.d/any.conf) ([`file.include`](/reference/features/#file-include)) | Configures `networkd-wait-online` to succeed when any interface is up. |
| [`file.include/etc/systemd/system/systemd-resolved.service.d/wait-for-networkd.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/systemd/system/systemd-resolved.service.d/wait-for-networkd.conf) ([`file.include`](/reference/features/#file-include)) | Orders systemd-resolved after systemd-networkd. |
| [`file.include/etc/systemd/system/systemd-timesyncd.service.d/override.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/systemd/system/systemd-timesyncd.service.d/override.conf) ([`file.include`](/reference/features/#file-include)) | Adjusts timesyncd startup ordering. |
| [`file.include/etc/systemd/system.conf.d/00-gardenlinux-server.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/systemd/system.conf.d/00-gardenlinux-server.conf) ([`file.include`](/reference/features/#file-include)) | systemd system-wide configuration for Garden Linux server. |
| [`file.include/etc/update-motd.d/05-logo`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/update-motd.d/05-logo) ([`file.include`](/reference/features/#file-include)) | MOTD script that displays the Garden Linux logo. |
| [`file.include/etc/update-motd.d/10-hostname`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/update-motd.d/10-hostname) ([`file.include`](/reference/features/#file-include)) | MOTD script that displays the system hostname. |
| [`file.include/etc/update-motd.d/20-uname`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/update-motd.d/20-uname) ([`file.include`](/reference/features/#file-include)) | MOTD script that displays the kernel version. |
| [`file.include/etc/update-motd.d/30-load`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/update-motd.d/30-load) ([`file.include`](/reference/features/#file-include)) | MOTD script that displays the system load average. |
| [`file.include/etc/update-motd.d/40-free`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/update-motd.d/40-free) ([`file.include`](/reference/features/#file-include)) | MOTD script that displays free memory information. |
| [`file.include/etc/update-motd.d/45-line`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/update-motd.d/45-line) ([`file.include`](/reference/features/#file-include)) | MOTD separator line. |
| [`file.include/etc/update-motd.d/50-network`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/update-motd.d/50-network) ([`file.include`](/reference/features/#file-include)) | MOTD script that displays network interface information. |
| [`file.include/etc/update-motd.d/55-line`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/update-motd.d/55-line) ([`file.include`](/reference/features/#file-include)) | MOTD separator line. |
| [`file.include/etc/update-motd.d/92-unattended-upgrades`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/update-motd.d/92-unattended-upgrades) ([`file.include`](/reference/features/#file-include)) | MOTD script that displays unattended-upgrades status. |
| [`file.include/etc/update-motd.d/95-needrestart`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/update-motd.d/95-needrestart) ([`file.include`](/reference/features/#file-include)) | MOTD script that alerts when a restart is needed after package updates. |
| [`file.include/usr/lib/systemd/system/dbus.socket`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/usr/lib/systemd/system/dbus.socket) ([`file.include`](/reference/features/#file-include)) | D-Bus socket unit. |
| [`file.include/usr/share/pam-configs/garden`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/usr/share/pam-configs/garden) ([`file.include`](/reference/features/#file-include)) | Garden Linux PAM configuration profile. |
| [`file.include/usr/share/pam-configs/garden-extra`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/usr/share/pam-configs/garden-extra) ([`file.include`](/reference/features/#file-include)) | Additional Garden Linux PAM configuration profile. |

### Related features

**Includes:**

- [`base`](/reference/features/base) — the minimal debootstrapped Garden Linux base.
- [`ssh`](/reference/features/ssh) — SSH server and client.
- [`log`](/reference/features/log) — logging infrastructure (auditd, rsyslog, journal-remote).
- [`_selinux`](/reference/features/_selinux) — SELinux security policy.

## Related topics

<RelatedTopics />

