---
title: "Feature: _dev"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_dev/README.md
github_target_path: docs/reference/features/_dev.md
---

## Feature: _dev

### Description

Adds development tools and enables console autologin for iterative development and testing of Garden Linux images.

### What it does

`_dev` installs `vim` and `dpkg-dev`, and reconfigures several systemd units to enable automatic root login on `tty1`, the serial console, and the rescue and emergency shells. A tmpfiles rule deploys test-related configuration for development workflows.

:::warning
Do not use this feature in production images. The autologin configuration removes authentication from the console, making the system accessible without credentials on any attached terminal.
:::

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.late`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_dev/exec.late) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Applies late-stage configuration changes to the image, such as adjusting service settings. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_dev/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_dev/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `vim` and `dpkg-dev` for editing and Debian package development. |
| [`file.include/etc/systemd/system/emergency.service.d/sulogin.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_dev/file.include/etc/systemd/system/emergency.service.d/sulogin.conf) ([`file.include`](/reference/features/#file-include)) | Overrides the emergency shell to skip `sulogin`, allowing passwordless access in emergency mode. |
| [`file.include/etc/systemd/system/getty@tty1.service.d/autologin.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_dev/file.include/etc/systemd/system/getty@tty1.service.d/autologin.conf) ([`file.include`](/reference/features/#file-include)) | Configures `getty` on `tty1` to log in automatically as root without a password prompt. |
| [`file.include/etc/systemd/system/rescue.service.d/sulogin.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_dev/file.include/etc/systemd/system/rescue.service.d/sulogin.conf) ([`file.include`](/reference/features/#file-include)) | Overrides the rescue shell to skip `sulogin`, allowing passwordless access in rescue mode. |
| [`file.include/etc/systemd/system/serial-getty@.service.d/autologin.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_dev/file.include/etc/systemd/system/serial-getty@.service.d/autologin.conf) ([`file.include`](/reference/features/#file-include)) | Configures the serial `getty` to log in automatically as root on the serial console. |
| [`file.include/usr/lib/tmpfiles.d/gardenlinux-tests-dev.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_dev/file.include/usr/lib/tmpfiles.d/gardenlinux-tests-dev.conf) ([`file.include`](/reference/features/#file-include)) | tmpfiles rule that creates or configures paths needed by development test workflows. |

### Related features

This feature has no include or exclude relationships.

## Related topics

<RelatedTopics />

