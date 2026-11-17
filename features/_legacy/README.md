---
title: "Feature: _legacy"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_legacy/README.md
github_target_path: docs/reference/features/_legacy.md
---

## Feature: _legacy

### Description

Installs and configures both a UEFI (systemd-boot) and a legacy BIOS (syslinux) bootloader, enabling the image to boot on systems without UEFI firmware.

### What it does

`_legacy` installs `dracut`, `systemd-boot`, and (on `amd64`) `syslinux`, then runs `exec.late` to configure both bootloaders. Three helper scripts are placed in `/usr/local/sbin/`:

- `update-bootloaders` — Updates both the UEFI and legacy BIOS bootloaders to reflect the current kernel.
- `update-kernel-cmdline` — Regenerates kernel command line configuration for both bootloaders.
- `update-syslinux` — Specifically updates the syslinux legacy BIOS configuration.

A random seed file (`/efi/loader/random-seed`) is excluded from the image to prevent entropy pool reuse across cloned images.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.late`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_legacy/exec.late) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Installs and configures the bootloaders and updates bootloader entries during image build. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_legacy/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes `/efi/loader/random-seed` from the image to avoid entropy reuse on cloned instances. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_legacy/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files in this feature to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_legacy/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_legacy/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `dracut`, `systemd-boot`, and conditionally `syslinux` on `amd64`. |
| [`file.include/usr/local/sbin/update-bootloaders`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_legacy/file.include/usr/local/sbin/update-bootloaders) ([`file.include`](/reference/features/#file-include)) | Updates both UEFI and BIOS bootloader entries when the kernel or command line changes. |
| [`file.include/usr/local/sbin/update-kernel-cmdline`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_legacy/file.include/usr/local/sbin/update-kernel-cmdline) ([`file.include`](/reference/features/#file-include)) | Regenerates the kernel command line configuration files used by both bootloaders. |
| [`file.include/usr/local/sbin/update-syslinux`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_legacy/file.include/usr/local/sbin/update-syslinux) ([`file.include`](/reference/features/#file-include)) | Updates the syslinux configuration for legacy BIOS boot. |

### Related features

`_legacy` has no include or exclude relationships in its own configuration.
It is excluded by [`_usi`](/reference/features/_usi), which represents the
UEFI-only UKI boot path:

**Mutually exclusive with:**

- [`_usi`](/reference/features/_usi) — the Unified System Image (UKI) boot approach
  requires UEFI exclusively and is incompatible with the BIOS/syslinux boot path
  that `_legacy` adds.

### Further reading

- [Feature file reference](/reference/features/) — file-type semantics
- [Features explanation](/explanation/features) — types, DAG, composition rules
- [systemd-boot documentation](https://www.freedesktop.org/software/systemd/man/latest/systemd-boot.html)
- [syslinux documentation](https://wiki.syslinux.org/)

## Related topics

<RelatedTopics />

