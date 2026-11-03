---
title: "Feature: cisOS"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/cisOS/README.md
github_target_path: docs/reference/features/cisOS.md
---

## Feature: cisOS

### Description

A sub-feature of [`cis`](/reference/features/cis) that configures OS settings per [CIS benchmark](/reference/glossary#cis-center-for-internet-security) requirements. Must be used with the [`cis`](/reference/features/cis) feature.

### What it does

Sets `pwquality` options, file permissions, login options, PAM configuration, and udev rules per CIS benchmark requirements. Configures kernel command line parameters to enable process auditing at boot, sets audit backlog limits, and manages logrotate policies for `btmp` and `wtmp`. Also configures sysstat and SELinux settings.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Applies CIS OS-level configuration: file permissions, login settings, and udev rules. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`file.include/etc/kernel/cmdline.d/10-audit-proc.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include/etc/kernel/cmdline.d/10-audit-proc.cfg) ([`file.include`](/reference/features/#file-include)) | Enables process auditing (`audit=1`) in the kernel command line per CIS benchmark. |
| [`file.include/etc/kernel/cmdline.d/20-audit-backlog.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include/etc/kernel/cmdline.d/20-audit-backlog.cfg) ([`file.include`](/reference/features/#file-include)) | Sets the kernel audit backlog limit per CIS benchmark. |
| [`file.include/etc/kernel/postinst.d/zz-kernel-cmdline`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include/etc/kernel/postinst.d/zz-kernel-cmdline) ([`file.include`](/reference/features/#file-include)) | Regenerates the kernel command line after kernel updates. |
| [`file.include/etc/kernel/postinst.d/zz-kernel-install`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include/etc/kernel/postinst.d/zz-kernel-install) ([`file.include`](/reference/features/#file-include)) | Runs kernel install hooks after kernel package updates. |
| [`file.include/etc/kernel/postinst.d/zz-update-syslinux`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include/etc/kernel/postinst.d/zz-update-syslinux) ([`file.include`](/reference/features/#file-include)) | Updates the syslinux bootloader after kernel installs. |
| [`file.include/etc/kernel/postrm.d/zz-kernel-remove`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include/etc/kernel/postrm.d/zz-kernel-remove) ([`file.include`](/reference/features/#file-include)) | Runs kernel removal hooks after kernel package removal. |
| [`file.include/etc/kernel/postrm.d/zz-update-syslinux`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include/etc/kernel/postrm.d/zz-update-syslinux) ([`file.include`](/reference/features/#file-include)) | Updates the syslinux bootloader after kernel removal. |
| [`file.include/etc/logrotate.d/btmp`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include/etc/logrotate.d/btmp) ([`file.include`](/reference/features/#file-include)) | Logrotate configuration for `/var/log/btmp` (failed login attempts) per CIS benchmark. |
| [`file.include/etc/logrotate.d/wtmp`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include/etc/logrotate.d/wtmp) ([`file.include`](/reference/features/#file-include)) | Logrotate configuration for `/var/log/wtmp` (login records) per CIS benchmark. |
| [`file.include/etc/pam.d/common-account`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include/etc/pam.d/common-account) ([`file.include`](/reference/features/#file-include)) | PAM account configuration enforcing CIS account management requirements. |
| [`file.include/etc/pam.d/common-auth`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include/etc/pam.d/common-auth) ([`file.include`](/reference/features/#file-include)) | PAM authentication configuration enforcing CIS authentication requirements. |
| [`file.include/etc/security/limits.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include/etc/security/limits.conf) ([`file.include`](/reference/features/#file-include)) | Sets system resource limits per CIS benchmark requirements. |
| [`file.include/etc/selinux/config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include/etc/selinux/config) ([`file.include`](/reference/features/#file-include)) | SELinux configuration per CIS benchmark requirements. |
| [`file.include/etc/sysstat/sysstat`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include/etc/sysstat/sysstat) ([`file.include`](/reference/features/#file-include)) | Enables sysstat data collection per CIS benchmark requirements. |
| [`file.include/usr/lib/tmpfiles.d/var.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cisOS/file.include/usr/lib/tmpfiles.d/var.conf) ([`file.include`](/reference/features/#file-include)) | tmpfiles.d configuration ensuring correct permissions on `/var` directories per CIS benchmark. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

