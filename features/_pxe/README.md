---
title: "Feature: _pxe"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_pxe/README.md
github_target_path: docs/reference/features/_pxe.md
---

## Feature: _pxe

### Description
<website-feature>
Creates artifacts for PXE network boot of Garden Linux.
</website-feature>

### Features
This feature creates PXE boot artifacts:
- `root.squashfs` — Compressed root filesystem
- `vmlinuz` — Linux kernel
- `initrd` — Initial ramdisk
- `cmdline` — Kernel command line parameters

When combined with `_trustedboot` or `_unsigned` (USI builds):
- `boot.efi` — Unified Kernel Image (UKI) for UEFI boot

### Boot Modes

**Traditional PXE Boot:**
- Uses separate kernel (`vmlinuz`) and initrd
- Fetches `root.squashfs` over HTTP at boot time
- Works with both BIOS and UEFI systems via iPXE

**UKI PXE Boot (with `_trustedboot`):**
- Uses single `boot.efi` (UKI) containing kernel, initrd, and cmdline
- Fetches `root.squashfs` over HTTP at boot time
- UEFI-only, supports Secure Boot when signed

Includes:
- [`_ignite`](/reference/features/_ignite) for Ignition-based first-boot configuration
- [`_install`](/reference/features/_install) for disk installation capability

For automatic installation on boot, combine with [`_autoinstall`](/reference/features/_autoinstall).

### Unit testing
This feature does not support unit tests.

### Meta
|||
|---|---|
|type|flag|
|artifact|`.pxe.tar.gz` (contains `vmlinuz`, `initrd`, `cmdline`, `root.squashfs`, and optionally `boot.efi` for USI builds)|
|included_features|[`_ignite`](/reference/features/_ignite), [`_install`](/reference/features/_install)|
|excluded_features|None|
