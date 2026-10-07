---
title: "Feature: _tpm2"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
  - /explanation/secure-boot
  - /explanation/boot-modes
  - /how-to/secure-boot
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_tpm2/README.md
github_target_path: docs/reference/features/_tpm2.md
---

## Feature: _tpm2

### Description

A feature that encrypts the `/var` partition
using a key sealed to the [TPM 2.0](/reference/glossary#tpm2).
The key is bound to the system's measured boot
state via [Platform Configuration Registers (PCRs)](/reference/glossary#platform-configuration-registers-pcrs),
so `/var` can only be unlocked when the system boots into a known-good state.
For context on how `_tpm2` fits into the available `/var` storage modes, see
[Boot Modes: Mutable Data Modes](/explanation/boot-modes#mutable-data-modes).

### What it does

`systemd-repart` creates and formats the `VAR` partition with `Encrypt=tpm2` on
first boot — the LUKS2 encryption key is generated and enrolled into the TPM
automatically. The partition persists across reboots (unlike
[`_ephemeral`](/reference/features/_ephemeral), which discards the key on every
reboot). The key is sealed to PCR 7 (the Secure Boot certificate chain), so
decryption only succeeds if the Secure Boot state is unchanged.

Key configurations:

- **TPM presence check**: `check-tpm.service` verifies `/dev/tpmrm0` is present
  before `systemd-repart` runs. The system halts if no TPM 2.0 is found.
- **Partition unlock**: `systemd-cryptsetup-var.service` unseals the TPM key and
  opens the LUKS2 device as `/dev/mapper/var`.
- **Mount**: `sysroot-var.mount` mounts `/dev/mapper/var` onto `/sysroot/var`.
- **PCR extension**: `tpm2-measure.service` extends PCR 7 with `"switch-root"` via
  `systemd-pcrextend` just before `initrd-switch-root.target`, tying the TPM state to
  the completed boot sequence. On failure, the system enters `emergency.target`.
- **TPM requirement**: `requirements.mod` declares `requirements["tpm2"]=true`, so
  the build system enforces TPM 2.0 availability on the target platform.

Typical usage: combine with [`_trustedboot`](/reference/features/_trustedboot) for a
fully measured and attested boot chain where PCR-based key sealing is meaningful:

```bash
./build kvm_dev_trustedboot_tpm2
```

Use `_tpm2` instead of [`_ephemeral`](/reference/features/_ephemeral) in any
[`_trustedboot`](/reference/features/_trustedboot) flavor when persistent `/var`
state is required.

### How it works

All steps run inside the initrd, before the root filesystem is available:

1. **TPM presence check** (`check-tpm.service`, ordered before `systemd-repart.service`
   via `systemd-repart.service.requires/`):
   - [`check-tpm`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_tpm2/initrd.include/usr/bin/check-tpm)
     verifies that `/dev/tpmrm0` exists. If the TPM is absent, it logs an error to
     the kernel log and calls `halt -f`.

2. **Partition creation and key enrollment** (`systemd-repart` reads
   [`10-var.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_tpm2/initrd.include/etc/repart.d/10-var.conf)):
   - Specifies type `var`, label `VAR`, ext4 format, `Encrypt=tpm2`, 15% weight.
     `systemd-repart` generates the LUKS2 encryption key, enrolls it into the TPM
     bound to the current PCR state, and seeds the directory structure from
     `/sysroot/var`.

3. **Partition unlock** (`systemd-cryptsetup-var.service`, after `systemd-repart`):
   - Calls `systemd-cryptsetup attach var /dev/disk/by-partlabel/VAR`, which unseals
     the key from the TPM and opens the LUKS2 device as `/dev/mapper/var`.

4. **Mount** (`sysroot-var.mount`, after `systemd-cryptsetup-var.service`):
   - Mounts `/dev/mapper/var` onto `/sysroot/var` as ext4.

5. **PCR extension** (`tpm2-measure.service`, ordered before `initrd-switch-root.target`
   via `initrd-switch-root.target.requires/`):
   - [`measure-pcr7`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_tpm2/initrd.include/usr/bin/measure-pcr7)
     calls `systemd-pcrextend --pcr 7 "switch-root"`, extending PCR 7 with the
     boot-transition event. Any modification to the boot chain produces a different PCR
     value, preventing future key unsealing.
   - On failure, `tpm2-measure.service` triggers `emergency.target`.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_tpm2/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag`; excludes [`_ephemeral`](/reference/features/_ephemeral) and [`_nocrypt`](/reference/features/_nocrypt). |
| [`initrd.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_tpm2/initrd.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps initrd files to test-coverage marker IDs. |
| [`requirements.mod`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_tpm2/requirements.mod) | Declares `requirements["tpm2"]=true` so the build system enforces TPM 2.0 availability on the target platform. |
| [`initrd.include/etc/repart.d/10-var.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_tpm2/initrd.include/etc/repart.d/10-var.conf) (`initrd.include`) | `systemd-repart` partition definition: creates `VAR` (type `var`, 15% weight, ext4, `Encrypt=tpm2`), seeding directory structure from `/sysroot/var`. |
| [`initrd.include/etc/systemd/system/check-tpm.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_tpm2/initrd.include/etc/systemd/system/check-tpm.service) (`initrd.include`) | Initrd service ordered before `systemd-repart` (via `systemd-repart.service.requires/`): verifies `/dev/tpmrm0` is present; halts the system if no TPM 2.0 is found. |
| [`initrd.include/etc/systemd/system/sysroot-var.mount`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_tpm2/initrd.include/etc/systemd/system/sysroot-var.mount) (`initrd.include`) | Initrd mount unit that mounts `/dev/mapper/var` onto `/sysroot/var` after `systemd-cryptsetup-var.service`. |
| [`initrd.include/etc/systemd/system/systemd-cryptsetup-var.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_tpm2/initrd.include/etc/systemd/system/systemd-cryptsetup-var.service) (`initrd.include`) | Initrd service that unseals the TPM-bound LUKS2 key and opens the `VAR` partition as `/dev/mapper/var` via `systemd-cryptsetup attach`. |
| [`initrd.include/etc/systemd/system/tpm2-measure.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_tpm2/initrd.include/etc/systemd/system/tpm2-measure.service) (`initrd.include`) | Initrd service ordered before `initrd-switch-root.target` (via `initrd-switch-root.target.requires/`): extends PCR 7 with `"switch-root"` via `systemd-pcrextend`, binding the TPM state to the completed boot chain. Triggers `emergency.target` on failure. |
| [`initrd.include/etc/systemd/system/initrd-switch-root.target.requires/tpm2-measure.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_tpm2/initrd.include/etc/systemd/system/initrd-switch-root.target.requires/tpm2-measure.service) (`initrd.include`) | Symlink ordering `tpm2-measure.service` as a requirement of `initrd-switch-root.target`, ensuring PCR measurement runs before the root pivot. |
| [`initrd.include/etc/systemd/system/systemd-repart.service.requires/check-tpm.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_tpm2/initrd.include/etc/systemd/system/systemd-repart.service.requires/check-tpm.service) (`initrd.include`) | Symlink ordering `check-tpm.service` as a requirement of `systemd-repart.service`, ensuring TPM presence is verified before partition creation. |
| [`initrd.include/usr/bin/check-tpm`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_tpm2/initrd.include/usr/bin/check-tpm) (`initrd.include`) | Script invoked by `check-tpm.service`: exits zero if `/dev/tpmrm0` exists; otherwise logs an error to the kernel log and calls `halt -f`. |
| [`initrd.include/usr/bin/measure-pcr7`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_tpm2/initrd.include/usr/bin/measure-pcr7) (`initrd.include`) | Script invoked by `tpm2-measure.service`: calls `systemd-pcrextend --pcr 7 "switch-root"`; calls `halt -f` on failure. |

### Related features

**Excludes (incompatible with):**

- [`_ephemeral`](/reference/features/_ephemeral) — both features encrypt `/var`;
  [`_ephemeral`](/reference/features/_ephemeral) uses a per-boot random key (no TPM),
  which is incompatible with TPM-sealed key management.
- [`_nocrypt`](/reference/features/_nocrypt) — disables `/var` encryption entirely;
  incompatible with `_tpm2`'s encrypted-partition approach.

**Closely pairs with:**

- [`_trustedboot`](/reference/features/_trustedboot) — the primary use case for `_tpm2`;
  establishes a fully measured and attested boot chain where PCR-based key sealing is
  meaningful. Without [`_trustedboot`](/reference/features/_trustedboot), PCR values may
  not accurately reflect the true boot state.

### Further reading

- [Boot Modes: Mutable Data Modes](/explanation/boot-modes#mutable-data-modes) — comparison of [`_nocrypt`](/reference/features/_nocrypt), [`_ephemeral`](/reference/features/_ephemeral), and `_tpm2`
- [Secure Boot and Trusted Boot](/explanation/secure-boot) — trust model, PCR binding, build and deploy instructions
- [Building Images: Secureboot / Trustedboot / TPM2](/how-to/building-images#secureboot-trustedboot-tpm2) — build prerequisites and steps
- [systemd-pcrextend documentation](https://www.freedesktop.org/software/systemd/man/latest/systemd-pcrextend.html)

## Related topics

<RelatedTopics />
