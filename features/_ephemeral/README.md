---
title: "Feature: _ephemeral"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_ephemeral/README.md
github_target_path: docs/reference/features/_ephemeral.md
---

## Feature: _ephemeral

### Description

A feature that provides an ephemeral encrypted
`/var` partition. The encryption key is generated fresh from `/dev/random` on every boot
and never persisted, so all data written to `/var` is lost when the system reboots.

### What it does

When `_ephemeral` is applied, the `/var` partition is encrypted on every boot using a
randomly generated key that is discarded when the system shuts down. This means:

- The `/var` partition contents do not survive a reboot.
- No persistent state is written to the encrypted `/var` partition across reboots.
- Encryption still protects data at rest during a running session, but provides no
  continuity between boots.

The typical use case is combining `_ephemeral` with [`_trustedboot`](/reference/features/_trustedboot)
to establish a fully attested boot chain where the ephemeral `/var` state is tied to
the measured boot:

```bash
./build kvm_dev_trustedboot_ephemeral
```

The alternative to `_ephemeral` is [`_tpm2`](/reference/features/_tpm2), which seals a
**persistent** encryption key to the TPM 2.0. Use `_ephemeral` when no `/var` state
should survive across reboots; use [`_tpm2`](/reference/features/_tpm2) when `/var` state
must persist but still be protected by hardware attestation.

### How it works

All steps run inside the initrd, before the root filesystem is available:

1. **Partition creation**: `systemd-repart` reads
   [`initrd.include/etc/repart.d/10-var.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_ephemeral/initrd.include/etc/repart.d/10-var.conf)
   and creates the `EPHEMERAL` partition (type `var`, GPT type code, 15% weight, label
   `EPHEMERAL`) on the disk.

2. **Encryption and format**: `ephemeral-cryptsetup.service` runs after
   `systemd-repart.service` and `sysroot.mount`:
   - Opens the `EPHEMERAL` partition with `cryptsetup` in plain mode
     (AES-XTS-512, key from `/dev/random`) — no LUKS header is written; the key
     is never stored anywhere.
   - Zeroes the first MiB of the opened device to clear any stale filesystem
     metadata.
   - Formats the device as ext4 without journalling (`-O '^has_journal'`),
     seeding the filesystem structure from `/sysroot/var` so that the directory
     hierarchy is preserved.

3. **Mount**: `sysroot-var.mount` mounts `/dev/mapper/ephemeral` onto `/sysroot/var`
   after `ephemeral-cryptsetup.service` completes. The system then pivots to
   `/sysroot` with an empty, freshly formatted `/var`.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_ephemeral/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag` and excluded features. |
| [`initrd.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_ephemeral/initrd.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps initrd files to test-coverage marker IDs. |
| [`initrd.include/etc/repart.d/10-var.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_ephemeral/initrd.include/etc/repart.d/10-var.conf) (`initrd.include`) | `systemd-repart` partition definition that creates the `EPHEMERAL` var partition (type `var`, 15% weight, label `EPHEMERAL`) in the initrd. |
| [`initrd.include/etc/systemd/system/ephemeral-cryptsetup.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_ephemeral/initrd.include/etc/systemd/system/ephemeral-cryptsetup.service) (`initrd.include`) | Initrd systemd service that opens the `EPHEMERAL` partition with `cryptsetup` plain mode (random key from `/dev/random`, AES-XTS-512), zeroes the first MiB, and formats the device as ext4. |
| [`initrd.include/etc/systemd/system/sysroot-var.mount`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_ephemeral/initrd.include/etc/systemd/system/sysroot-var.mount) (`initrd.include`) | Initrd mount unit that mounts `/dev/mapper/ephemeral` onto `/sysroot/var` after `ephemeral-cryptsetup.service` completes. |

### Related features

**Excludes (incompatible with):**

- [`_nocrypt`](/reference/features/_nocrypt) — both features control `/var` encryption; [`_nocrypt`](/reference/features/_nocrypt) disables encryption entirely, which is incompatible with `_ephemeral`'s encrypted-partition approach.

**Closely pairs with:**

- [`_trustedboot`](/reference/features/_trustedboot) — the primary use case for `_ephemeral`; establishes a fully attested boot chain where the ephemeral `/var` state is tied to the measured boot.
- [`_tpm2`](/reference/features/_tpm2) — the persistent-key alternative to `_ephemeral`; seals the encryption key to the TPM 2.0 instead of discarding it on each reboot. Mutually exclusive with `_ephemeral`.

### Further reading

- [Boot Modes](/explanation/boot-modes) — overview of Garden Linux boot modes including trusted boot
- [Secure Boot and Trusted Boot](/explanation/secure-boot)

## Related topics

<RelatedTopics />
