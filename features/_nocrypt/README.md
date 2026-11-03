---
title: "Feature: _nocrypt"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_nocrypt/README.md
github_target_path: docs/reference/features/_nocrypt.md
---

## Feature: _nocrypt

### Description

Configures the `/var` partition as a plain ext4 filesystem without disk encryption.

### What it does

By default, Garden Linux images encrypt the `/var` partition. `_nocrypt` overrides this behavior by providing an unencrypted ext4 partition definition and a matching `sysroot-var.mount` unit in the initrd. This places the `/var` data on disk in plaintext, which is suitable for environments where encryption is managed at a different layer (for example, by the hypervisor or storage backend) or where the overhead of dm-crypt is undesirable.

The initrd files (`initrd.include`) are used instead of regular `file.include` entries because the partition setup and mounting of `/var` must occur during the early boot phase, before the rootfs is fully available.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_nocrypt/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and included/excluded features. |
| [`initrd.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_nocrypt/initrd.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps initrd files to test-coverage marker IDs. |
| [`initrd.include/etc/repart.d/10-var.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_nocrypt/initrd.include/etc/repart.d/10-var.conf) (`initrd.include`) | `systemd-repart` partition definition that creates a plain ext4 `/var` partition without encryption. |
| [`initrd.include/etc/systemd/system/sysroot-var.mount`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_nocrypt/initrd.include/etc/systemd/system/sysroot-var.mount) (`initrd.include`) | systemd mount unit included in the initrd that mounts the unencrypted `/var` partition into the sysroot early in boot. |

### Related features

`_nocrypt` has no include or exclude relationships in its own configuration.
It is excluded by the following features, which provide alternative `/var`
encryption strategies:

**Mutually exclusive with:**

- [`_ephemeral`](/reference/features/_ephemeral) — provides an ephemeral encrypted
  `/var` using a per-boot random key; incompatible with plaintext `/var`.
- [`_tpm2`](/reference/features/_tpm2) — seals a persistent `/var` encryption key
  to the TPM 2.0; incompatible with plaintext `/var`.

## Related topics

<RelatedTopics />

