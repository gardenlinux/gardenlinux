---
title: "Feature: _autoinstall"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_autoinstall/README.md
github_target_path: docs/reference/features/_autoinstall.md
---

## Feature: _autoinstall

### Description

Enables automatic, non-interactive installation of Garden Linux to disk on first boot.

### What it does

`_autoinstall` adds a systemd service (`gl-autoinstall.service`) that triggers on first boot and installs Garden Linux to disk without user input. The service invokes the wrapper script `gl-autoinstall`, which auto-detects the first suitable block device (or reads the target from the `gl.install.target` kernel parameter) and delegates to the [`_install`](/reference/features/_install) feature's `/opt/install/install.sh`. The system reboots into the installed image once installation completes.

The service runs only when `/opt/install/install.sh` is present and skips silently if the `/.installed` marker already exists, preventing accidental re-installation on subsequent boots.

Combine `_autoinstall` with [`_iso`](/reference/features/_iso) or [`_pxe`](/reference/features/_pxe) to produce a bootable image that installs itself to disk on first boot.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_autoinstall/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Configures the image at build time to enable the autoinstall service. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_autoinstall/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`requirements.mod`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_autoinstall/requirements.mod) | Declares kernel module requirements for the autoinstall environment. |
| [`file.include/etc/systemd/system/gl-autoinstall.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_autoinstall/file.include/etc/systemd/system/gl-autoinstall.service) ([`file.include`](/reference/features/#file-include)) | Systemd unit that runs `gl-autoinstall` on first boot to trigger unattended disk installation. |
| [`file.include/usr/local/sbin/gl-autoinstall`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_autoinstall/file.include/usr/local/sbin/gl-autoinstall) ([`file.include`](/reference/features/#file-include)) | Wrapper script that detects the target block device, calls `install.sh`, and reboots the system. |

### Related features

**Includes:**

- [`_install`](/reference/features/_install) — Provides the core installation script (`install.sh`) that `_autoinstall` delegates to.

## Related topics

<RelatedTopics />

