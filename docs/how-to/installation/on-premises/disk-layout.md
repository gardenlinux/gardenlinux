---
title: "Disk Layout and Bootloader"
description: "Partition layout and bootloader configuration for Garden Linux on-premises installations"
order: 3
related_topics:
  - /how-to/installation/on-premises/iso.md
  - /how-to/installation/on-premises/pxe-boot.md
  - /explanation/boot-modes.md
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/installation/on-premises/disk-layout.md
github_target_path: docs/how-to/installation/on-premises/disk-layout.md
---

# Disk Layout and Bootloader

Garden Linux on-premises installations (ISO and PXE boot) use a standardized GPT partition layout with firmware-specific bootloader configuration. This page describes the partition scheme and bootloader installation for both Legacy BIOS and UEFI systems.

## Partition layout

The installation creates a GPT partition table with two partitions:

| Partition | Type | Size | Format | Purpose |
|-----------|------|------|--------|---------|
| **EFI** | `C12A7328-F81F-11D2-BA4B-00A0C93EC93B` (ESP) | 510 MiB | VFAT  | Bootloader storage (Legacy: syslinux stages, UEFI: systemd-boot + UKI) |
| **ROOT** | Architecture-specific (see below) | Remaining space | ext4 | Garden Linux root filesystem |

This layout supports both Legacy BIOS and UEFI firmware using the same partition structure. The EFI System Partition (ESP) is used by both firmware types:

- **Legacy BIOS** — Stores syslinux bootloader stages (stage 2 and higher)
- **UEFI** — Stores systemd-boot bootloader and kernel images

### Root partition type GUIDs

Garden Linux uses architecture-specific root partition GUIDs from the [Discoverable Partitions Specification](https://uapi-group.org/specifications/specs/discoverable_partitions_specification/). This enables automatic root partition discovery by systemd without requiring `root=` kernel parameters or `/etc/fstab` entries.

| Architecture | Root Partition GUID |
|--------------|---------------------|
| x86-64 (amd64) | `4f68bce3-e8cd-4db1-96e7-fbcaf984b709` |
| ARM64 (aarch64) | `b921b045-1df0-41c3-af44-4c6f280d3fae` |

:::warning
The generic Linux filesystem GUID (`0FC63DAF-8483-4772-8E79-3D69D8477DE4`) should not be used for root partitions as it disables automatic discovery features.
:::

## Bootloader installation

The installation script detects the firmware type and installs the appropriate bootloader automatically.

### Legacy BIOS — syslinux

For Legacy BIOS systems, the installer installs [syslinux](https://wiki.syslinux.org/):

1. Writes a new Master Boot Record (MBR) to the first sector of the disk
2. Installs syslinux stages 2+ to the EFI partition
3. Configures syslinux to boot the kernel from the ROOT partition

The syslinux bootloader configuration includes console output to both serial (`ttyS0`) and VGA (`tty0`).

### UEFI — systemd-boot

For UEFI systems, the installer installs [systemd-boot](https://www.freedesktop.org/software/systemd/man/latest/systemd-boot.html):

- **ISO installations** — Use Boot Loader Specification (BLS) entries in `/efi/loader/entries/`
- **PXE installations** — Use Unified Kernel Images (UKI) which combine the EFI stub loader, kernel image, initramfs, and kernel command line into a single EFI PE executable

UKI images can be signed for Secure Boot support.

The systemd-boot configuration includes console output to both serial (`ttyS0` for ISO, `ttyS1` for PXE) and VGA (`tty0`).

## Firmware migration

The identical disk layout for both firmware types allows migrating an installation between Legacy BIOS and UEFI systems by re-running the appropriate bootloader installation script on the target system.

## Related Topics

- [Boot Modes](/explanation/boot-modes.md) — Technical background on BIOS and UEFI boot processes
- [Install Using ISO](/how-to/installation/on-premises/iso.md) — ISO installation guide
- [Install Using PXE Boot](/how-to/installation/on-premises/pxe-boot.md) — PXE network boot installation guide
