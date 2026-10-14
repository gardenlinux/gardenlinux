---
title: "Feature: _usi"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_usi/README.md
github_target_path: docs/reference/features/_usi.md
---

## Feature: _usi

### Description

A feature that boots Garden Linux using a
[Unified System Image (USI)](/reference/glossary#usi-unified-system-image): a [Unified Kernel Image (UKI)](/reference/glossary#uki-unified-kernel-image) with an embedded [EROFS](/reference/glossary#erofs-enahnced-read-only-file-system)
read-only root disk stored on the [EFI System Partition (ESP)](/reference/glossary#efi-system-partition-esp).

### What it does

Builds a Garden Linux image where the entire root filesystem is stored as an
EROFS image embedded in the EFI System Partition, and booted via a Unified
Kernel Image (UKI). This approach eliminates a separate root partition: the
bootloader, kernel, initrd, and root filesystem are all contained in the ESP.

Key capabilities added by this feature:

- **Image build**: `image.esp.tar` constructs the EROFS root disk and embeds it
  into the ESP alongside the UKI.
- **Conversion**: `convert.raw~esp.tar` produces a raw disk image from the ESP
  tarball; `convert.uki~esp.tar` extracts the standalone UKI EFI binary.
- **Initrd**: mounts the EROFS root from the ESP in the initramfs using systemd
  `.mount` units and `systemd-repart` to locate and mount the EFI partition.
- **`/etc` overlay**: the initrd sets up a writable overlay on `/etc` so that
  runtime configuration can be written without modifying the read-only root.
- **Secure Boot key enrollment**: installs Garden Linux Secure Boot keys and
  an OCI signing key into `/etc/gardenlinux/`.
- **Persistent `/home` and `/opt`**: moves these directories under `/var` so
  they survive across image updates.
- **Kernel command line**: manages the kernel command line via
  `update-kernel-cmdline` and drops an `etc-setup-hooks` service for
  first-boot configuration.

### How it works

At build time, `image.esp.tar` packs the rootfs into an EROFS image, wraps it
with a UKI, and produces an ESP tarball. `convert.raw~esp.tar` then formats a
FAT32 EFI partition from the ESP tarball and wraps it in a raw GPT disk image.

At boot, the UKI is loaded by the UEFI firmware. The embedded initrd (populated
from `initrd.include/`) mounts the EFI partition, finds the EROFS image, mounts
it as the root filesystem, and sets up the `/etc` overlay before pivoting to the
real root.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`convert.raw~esp.tar`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/convert.raw~esp.tar) ([ref](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Converts the ESP tarball into a bootable raw disk image with a FAT32 EFI partition. |
| [`convert.uki~esp.tar`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/convert.uki~esp.tar) ([ref](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Extracts the standalone UKI EFI binary from the ESP tarball. |
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Enables `systemd-bless-boot` and `gardenlinux-etc-setup-hooks` services, runs `update-kernel-cmdline`, creates `/efi`, and patches the `systemd-pcrphase` symlink if missing. |
| [`exec.post`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/exec.post) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Installs Garden Linux Secure Boot auth files and the OCI signing public key; moves `/home` and `/opt` under `/var` for persistence across updates. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes Ignition-related configs and services, `/root/` contents, and the `image-dissect` udev rule from the rootfs. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`image.esp.tar`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/image.esp.tar) ([ref](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Creates the EROFS root disk image, embeds it in a UKI, and packages the result as an ESP tarball. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`initrd.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/initrd.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps initrd files to test-coverage marker IDs. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `dracut`, `systemd-ukify`, `systemd-boot-efi`, `systemd-tpm`, `efitools`, `tpm2-tools`, `cryptsetup`, `gardenlinux-update`, and `resizefat32`. |
| [`requirements.mod`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/requirements.mod) | Declares that the UEFI requirement must be satisfied (`requirements["uefi"]=true`). |
| [`file.include/etc/kernel/cmdline.d/99-no-gpt-auto.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/file.include/etc/kernel/cmdline.d/99-no-gpt-auto.cfg) ([`file.include`](/reference/features/#file-include)) | Disables GPT auto-discovery in the kernel command line so that only the ESP is auto-mounted. |
| [`file.include/etc/systemd/system/gardenlinux-etc-setup-hooks.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/file.include/etc/systemd/system/gardenlinux-etc-setup-hooks.service) ([`file.include`](/reference/features/#file-include)) | Systemd service that runs first-boot `/etc` setup hooks after the overlay is ready. |
| [`file.include/etc/update-motd.d/25-secureboot`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/file.include/etc/update-motd.d/25-secureboot) ([`file.include`](/reference/features/#file-include)) | MOTD script that displays the current Secure Boot enrollment status. |
| [`file.include/usr/local/sbin/update-kernel-cmdline`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/file.include/usr/local/sbin/update-kernel-cmdline) ([`file.include`](/reference/features/#file-include)) | Rebuilds the kernel command line file from fragments in `/etc/kernel/cmdline.d/`. |
| [`file.include/usr/sbin/enroll-gardenlinux-secureboot-keys`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/file.include/usr/sbin/enroll-gardenlinux-secureboot-keys) ([`file.include`](/reference/features/#file-include)) | Enrolls the Garden Linux Secure Boot keys into the UEFI firmware key databases. |
| [`file.include/usr/sbin/run-etc-setup-hooks`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/file.include/usr/sbin/run-etc-setup-hooks) ([`file.include`](/reference/features/#file-include)) | Runs executable scripts from a hooks directory to apply first-boot `/etc` configuration. |
| [`initrd.include/etc/repart.d/00-efi.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/initrd.include/etc/repart.d/00-efi.conf) (`initrd.include`) | `systemd-repart` partition definition used in the initrd to locate and grow the EFI partition. |
| [`initrd.include/etc/systemd/system/setup-etc-overlay.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/initrd.include/etc/systemd/system/setup-etc-overlay.service) (`initrd.include`) | Initrd systemd service that creates and mounts the writable `/etc` overlay before pivot. |
| [`initrd.include/etc/systemd/system/sysroot-etc.mount`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/initrd.include/etc/systemd/system/sysroot-etc.mount) (`initrd.include`) | Mounts the `/etc` overlay onto `/sysroot/etc` in the initrd. |
| [`initrd.include/etc/systemd/system/sysroot-home.mount`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/initrd.include/etc/systemd/system/sysroot-home.mount) (`initrd.include`) | Mounts `/var/home` onto `/sysroot/home` for user data persistence. |
| [`initrd.include/etc/systemd/system/sysroot-opt.mount`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/initrd.include/etc/systemd/system/sysroot-opt.mount) (`initrd.include`) | Mounts `/var/opt` onto `/sysroot/opt` for optional software persistence. |
| [`initrd.include/etc/systemd/system/sysroot-root.mount`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/initrd.include/etc/systemd/system/sysroot-root.mount) (`initrd.include`) | Mounts `/var/root` onto `/sysroot/root` for root home persistence. |
| [`initrd.include/etc/systemd/system/sysroot.mount`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/initrd.include/etc/systemd/system/sysroot.mount) (`initrd.include`) | Mounts the EROFS root image onto `/sysroot` in the initrd. |
| [`initrd.include/etc/systemd/system/sysroot-opt.mount`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/initrd.include/etc/systemd/system/sysroot-opt.mount) (`initrd.include`) | Mounts `/var/opt` onto `/sysroot/opt`. |
| [`initrd.include/etc/systemd/system/initrd-root-fs.target.requires/`](https://github.com/gardenlinux/gardenlinux/tree/main/features/_usi/initrd.include/etc/systemd/system/initrd-root-fs.target.requires/) (`initrd.include`) | Systemd `.requires` symlinks ensuring all sysroot mount units are ordered before `initrd-root-fs.target`. |
| [`initrd.include/etc/systemd/system-generators/detect-disk-by-efivars`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/initrd.include/etc/systemd/system-generators/detect-disk-by-efivars) (`initrd.include`) | Systemd generator that identifies the boot disk by reading EFI variables, used to locate the ESP. |
| [`initrd.include/etc/systemd/system-generators/dracut-crypt-generator`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/initrd.include/etc/systemd/system-generators/dracut-crypt-generator) (`initrd.include`) | Dracut-compatible generator for cryptsetup integration in the initrd. |
| [`initrd.include/usr/bin/repart-esp-disk`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/initrd.include/usr/bin/repart-esp-disk) (`initrd.include`) | Helper script that invokes `systemd-repart` to locate and optionally grow the EFI partition. |
| [`initrd.include/usr/bin/setup-etc-overlay`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_usi/initrd.include/usr/bin/setup-etc-overlay) (`initrd.include`) | Script invoked by `setup-etc-overlay.service` to create the tmpfs-based `/etc` overlay. |

### Related features

**Includes:**

- [`_nocrypt`](/reference/features/_nocrypt) — disables disk encryption, which is incompatible with embedding the root filesystem in the ESP.
- [`_unsigned`](/reference/features/_unsigned) — skips signing the UKI during local/development builds; replace with a signing feature for production.

**Excludes (incompatible with):**

- [`_legacy`](/reference/features/_legacy) — BIOS/legacy boot is incompatible with the UEFI-only UKI boot approach.

### Further reading

- [systemd-ukify documentation](https://www.freedesktop.org/software/systemd/man/latest/ukify.html)
- [EROFS documentation](https://erofs.docs.kernel.org/)

## Related topics

<RelatedTopics />

