---
title: "Feature: _kdump"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_kdump/README.md
github_target_path: docs/reference/features/_kdump.md
---

## Feature: _kdump

### Description

A feature that installs `kdump-tools` and
`makedumpfile` to capture a kernel crash dump whenever the kernel panics. The crash
dump is stored on disk for post-mortem analysis.

### What it does

Installs `kdump-tools`, `makedumpfile`, `binutils`, and `jq`. Adds
`crashkernel=512M` to the kernel command line so the running kernel reserves 512 MiB
of memory for the crash kernel.

The Debian-provided `kdump-tools` defaults are used without modification. No custom
crash kernel or crash initrd are shipped — the running kernel and its initrd are
reused as the crash kernel and crash initrd.

**[`_usi`](/reference/features/_usi) / in-place-update images**: because the rootfs
is an EROFS image embedded in the UKI, the size of the initrd varies with the feature
set, making a universal `crashkernel=` value impractical. Before `kdump-tools.service`
starts, the `kdump-tools.service` drop-in runs
[`prepare-initrd-kdump`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_kdump/file.include/usr/local/sbin/prepare-initrd-kdump)
to extract the initrd from the UKI and place it where `kdump-tools` expects it.

**Enabling kdump on a running system** is not officially supported; see
`### How it works` for experimental steps.

### How it works

#### Standard crash flow

1. The kernel boots with `crashkernel=512M` reserved in physical memory.
2. On kernel panic, `kexec` loads the crash kernel (the same kernel and initrd used
   for normal boot) into the reserved memory region.
3. The crash kernel boots into a minimal environment and saves the vmcore dump to
   `/var/crash/`.
4. `makedumpfile` processes the dump to filter out zero pages and reduce its size.

#### `_usi` initrd preparation

On [`_usi`](/reference/features/_usi) images, the standard initrd at
`/boot/initrd.img-$(uname -r)` does not exist because the initrd is embedded in the
Unified Kernel Image (UKI). `prepare-initrd-kdump` handles this before
`kdump-tools.service` activates:

1. Reads `GARDENLINUX_FEATURES_FLAGS` from `/etc/os-release` to detect the `_usi` flag.
2. Queries `bootctl list --json=short` for the path of the currently selected UKI.
3. Extracts the embedded initrd section using `objcopy --dump-section .initrd` and saves
   it as `/var/lib/kdump/initrd.img-$(uname -r)`.

On non-`_usi` images, `prepare-initrd-kdump` creates a symlink from
`/var/lib/kdump/initrd.img-$(uname -r)` to the standard `/boot/initrd.img-$(uname -r)`.

#### Enabling kdump on a running system (experimental)

1. Install `kdump-tools` and `makedumpfile`.
2. Copy the initrd to `/var/lib/kdump/` using the name `initrd.img-$(uname -r)`.
3. Add `crashkernel=XXXM` to `/etc/kernel/cmdline` or a drop-in file in
   `/etc/kernel/cmdline.d/`.
4. Regenerate the bootloader entries.
5. Reboot.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_kdump/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_kdump/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag`; no include/exclude relationships. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_kdump/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `kdump-tools`, `makedumpfile`, `binutils`, and `jq`. |
| [`file.include/etc/kernel/cmdline.d/90-crashkernel.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_kdump/file.include/etc/kernel/cmdline.d/90-crashkernel.cfg) ([`file.include`](/reference/features/#file-include)) | Adds `crashkernel=512M` to the kernel command line to reserve memory for the crash kernel. |
| [`file.include/etc/systemd/system/kdump-tools.service.d/override.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_kdump/file.include/etc/systemd/system/kdump-tools.service.d/override.conf) ([`file.include`](/reference/features/#file-include)) | Systemd drop-in that runs `prepare-initrd-kdump` as `ExecStartPre` before `kdump-tools.service` activates, ensuring the correct initrd is in place for the crash kernel. |
| [`file.include/usr/local/sbin/prepare-initrd-kdump`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_kdump/file.include/usr/local/sbin/prepare-initrd-kdump) ([`file.include`](/reference/features/#file-include)) | Prepares the crash initrd: on `_usi` images, extracts the embedded initrd from the selected UKI via `objcopy`; on standard images, creates a symlink in `/var/lib/kdump/` pointing to `/boot/initrd.img-$(uname -r)`. |

### Related features

`_kdump` has no include or exclude relationships.

**Closely pairs with:**

- [`_usi`](/reference/features/_usi) — when `_usi` is active, the crash initrd must be
  extracted from the UKI before kdump can operate;
  [`prepare-initrd-kdump`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_kdump/file.include/usr/local/sbin/prepare-initrd-kdump)
  handles this automatically.

### Further reading

- [Linux kernel kdump documentation](https://docs.kernel.org/admin-guide/kdump/kdump.html)
- [EROFS filesystem documentation](https://docs.kernel.org/filesystems/erofs.html)

## Related topics

<RelatedTopics />
