---
title: "Feature: _autoinstall"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_autoinstall/README.md
github_target_path: docs/reference/features/_autoinstall.md
---

## Feature: _autoinstall

### Description
<website-feature>
Enables automatic unattended installation of Garden Linux to disk on first boot.
</website-feature>

### Features
This feature adds automatic installation by:
- Providing `gl-autoinstall.service` — Systemd service triggered on first boot
- Providing `/usr/local/sbin/gl-autoinstall` — Wrapper script that:
  - Auto-detects first suitable block device (or uses `gl.install.target` kernel parameter)
  - Calls [`_install`](/reference/features/_install)'s `/opt/install/install.sh`
  - Uses kexec to boot into installed system

Service conditions:
- Runs only when `/opt/install/install.sh` exists
- Skips if `/.installed` marker is present

Combine with [`_iso`](/reference/features/_iso) or [`_pxe`](/reference/features/_pxe) for bootable images.

### Unit testing
This feature does not support unit tests.

### Meta
|||
|---|---|
|type|flag|
|artifact|None|
|included_features|[`_install`](/reference/features/_install)|
|excluded_features|None|
