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

### !!! IMPORTANT !!!
Please be aware of the fact that systemd-networkd-wait-online is configured to mark the system as online when at least one interface becomes online. 
This makes the boot process faster, but, on systems with multiple NICs on different network segments, that would mean that depending on the order in which the NICs get configured, the system will get marked as online but the squashfs fetching might still fail and the system will fail to boot.

### Installation Support

The `_pxe` feature provides ephemeral live boot by default. For disk installation capability, combine with:

- [`_install`](/reference/features/_install) — For interactive installation (prompts for disk and password)
- [`_autoinstall`](/reference/features/_autoinstall) — For automatic unattended installation (includes `_install`)

**Live Boot Only (no installation):**
```bash
./build.sh metal_pxe
```

**Live Boot + Interactive Installation:**
```bash
# Add _install feature for interactive disk installation
./build.sh metal_pxe_install
```

**Live Boot + Automatic Installation:**
```bash
# Add _autoinstall for unattended disk installation
./build.sh metal_pxe_autoinstall
```

Includes:
- [`_ignite`](/reference/features/_ignite) for Ignition-based first-boot configuration

### Unit testing
This feature does not support unit tests.

### Meta
|||
|---|---|
|type|flag|
|artifact|`.pxe.tar.gz` (contains `vmlinuz`, `initrd`, `cmdline`, `root.squashfs`, and optionally `boot.efi` for USI builds)|
|included_features|[`_ignite`](/reference/features/_ignite)|
|excluded_features|None|
