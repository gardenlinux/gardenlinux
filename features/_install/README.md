---
title: "Feature: _install"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_install/README.md
github_target_path: docs/reference/features/_install.md
---

## Feature: _install

### Description
<website-feature>
Provides a generic installation framework for Garden Linux, enabling installation to disk from live environments (ISO, PXE).
</website-feature>

### Features
This feature provides:
- `/opt/install/install.sh` — Main installation script (partitioning, formatting, copying, bootloader)
- `/opt/install/install.part` — Default GPT partition layout template
- `/opt/install/install.fstab` — Default fstab configuration

The install script supports:
- Interactive installation (prompts for disk and password)
- Non-interactive installation via `GL_INSTALL_TARGET` environment variable
- Automatic rootfs source detection (`/run/rootfsbase` for ISO, `/run/rootfs` for PXE)
- UEFI (systemd-boot) and Legacy BIOS (syslinux) bootloaders

### Unit testing
This feature does not support unit tests.

### Meta
|||
|---|---|
|type|flag|
|artifact|None|
|included_features|None|
|excluded_features|None|
