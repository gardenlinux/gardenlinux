---
title: "Feature: _trustedboot"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
  - /explanation/secure-boot
  - /explanation/boot-modes
  - /how-to/secure-boot
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_trustedboot/README.md
github_target_path: docs/reference/features/_trustedboot.md
---

## Feature: _trustedboot

### Description

A feature that establishes a fully trusted
boot chain: UEFI [Secure Boot](/reference/glossary#secure-boot) verifies the
bootloader and Unified Kernel Image (UKI) and the root filesystem
(embedded as EROFS in the UKI) is covered by the same signature.
At runtime, the system halts if Secure Boot is not active, closing all
emergency escape paths. For the full trust model and security guarantees, see
[Secure Boot and Trusted Boot](/explanation/secure-boot).

### What it does

`_trustedboot` composes several layers of boot-chain integrity:

- **Includes [`_usi`](/reference/features/_usi)** — switches the image to UKI boot
  mode, embedding the EROFS root filesystem in a single signed EFI binary.
- **Includes [`_ephemeral`](/reference/features/_ephemeral)** — sets the default
  `/var` storage to a per-boot randomly-keyed encrypted partition (no state persists
  across reboots). Replace with [`_tpm2`](/reference/features/_tpm2) if persistent
  `/var` is needed.
- **Signs the UKI** — `usi.config` runs at build time to sign the systemd-boot EFI
  binary and the UKI with `sbsign`, using either a local key or an AWS KMS PKCS#11
  key. Secure Boot auth files (PK, KEK, db) are copied to the ESP and `loader.conf`
  is configured for automatic key enrollment.
- **Verifies Secure Boot at runtime** — `check-secureboot.service` reads the
  `SecureBoot` EFI variable in the initrd and halts the system if Secure Boot is not
  active, before any local filesystem is mounted.
- **Removes all emergency escape paths** — `emergency.service` is overridden to call
  `halt -f` immediately, and `99-no-rd-shell.cfg` strips `rd.shell` and `rd.emergency`
  from the kernel command line, appending `rd.shell=0 rd.emergency=poweroff`.
- **Enforces Secure Boot capability** — `requirements.mod` declares
  `requirements["secureboot"]=true`, so the build system rejects targets that do not
  support Secure Boot.

For a detailed breakdown of security guarantees, the feature dependency table, and
mutable data mode comparison, see [Secure Boot and Trusted Boot](/explanation/secure-boot).

### How it works

#### Boot-time verification (initrd)

All verification steps run inside the initrd, before any local filesystem is mounted:

1. **Secure Boot check** (`check-secureboot.service`, ordered before `local-fs.target`
   via `local-fs.target.requires/`):
   - `check-secureboot` reads
     `/sys/firmware/efi/efivars/SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c` and
     checks whether the last byte is `1`.
   - If Secure Boot is not active, it logs an error to the kernel log and exits
     non-zero, triggering `emergency.target`.

2. **Emergency halt override** (`emergency.service`):
   - The standard `emergency.service` (which drops to a root shell) is replaced with
     a one-shot unit that calls `halt -f` immediately. Combined with the kernel command
     line changes, there is no way to reach a shell on boot failure.

3. **Kernel command line hardening** (`99-no-rd-shell.cfg`):
   - Strips any existing `rd.shell` and `rd.emergency` parameters using `sed`, then
     appends `rd.shell=0 rd.emergency=poweroff systemd.gpt_auto=0`. This prevents the
     kernel or dracut from offering an emergency shell regardless of how the system
     was invoked.

#### Image signing (`usi.config`, build-time)

`usi.config` is called by the `_usi` image builder with the UKI path, ESP directory,
and rootfs path as arguments:

1. Signs the systemd-boot EFI binary (`EFI/BOOT/BOOT{X64,AA64}.EFI`) with `sbsign`
   using either a local PEM key (`cert/secureboot.db.key`) or an AWS KMS PKCS#11
   engine key identified by ARN (`cert/secureboot.db.arn`).
2. Writes `loader/loader.conf` with `secure-boot-enroll force` so that systemd-boot
   auto-enrolls the Garden Linux Secure Boot certificates on first boot.
3. Copies the Garden Linux Secure Boot auth files (PK, KEK, db) from
   `/etc/gardenlinux/` in the rootfs to `EFI/loader/keys/auto/` in the ESP.
4. Signs the UKI with `sbsign` and places the signed binary at
   `EFI/Linux/$BUILDER_CNAME.efi` in the ESP.

For certificate generation and build instructions, see
[Building Images: Secureboot / Trustedboot / TPM2](/how-to/building-images#secureboot-trustedboot-tpm2).

#### Testing on macOS

1. Generate the Secure Boot certificate chain:
   ```bash
   ./cert/build
   ```
2. Build an image with the `_trustedboot` flag, optionally combined with
   [`_tpm2`](/reference/features/_tpm2):
   ```bash
   ./build kvm_dev_trustedboot_tpm2
   ```
3. Obtain an edk2 build with Secure Boot support:
   ```bash
   mkdir edk2
   podman run --rm -v "$PWD/edk2:/mnt" debian:testing bash -c \
     'apt update && apt install -y qemu-efi-aarch64 && \
      cp /usr/share/AAVMF/AAVMF_CODE.secboot.fd /usr/share/AAVMF/AAVMF_VARS.fd /mnt/'
   ```
4. Boot the image with `start-vm` (the `,qcow=4G` suffix is required to make the disk
   large enough for `systemd-repart` to create the `/var` partition):
   ```bash
   ./bin/start-vm \
     --ueficode edk2/AAVMF_CODE.secboot.fd \
     --uefivars edk2/AAVMF_VARS.fd \
     --tpm2 disk.qcow2,qcow=4G
   ```

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_trustedboot/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps `file.include` files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_trustedboot/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag`; includes [`_usi`](/reference/features/_usi) and [`_ephemeral`](/reference/features/_ephemeral); excludes [`_nocrypt`](/reference/features/_nocrypt) and [`_unsigned`](/reference/features/_unsigned). |
| [`initrd.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_trustedboot/initrd.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps initrd files to test-coverage marker IDs. |
| [`requirements.mod`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_trustedboot/requirements.mod) | Declares `requirements["secureboot"]=true`, enforcing that the build target supports Secure Boot. |
| [`usi.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_trustedboot/usi.config) | Build-time signing script called by the `_usi` image builder: signs the systemd-boot EFI binary and the UKI with `sbsign` (local PEM key or AWS KMS PKCS#11); configures auto-enrollment; copies Garden Linux Secure Boot auth files to the ESP. |
| [`file.include/etc/kernel/cmdline.d/99-no-rd-shell.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_trustedboot/file.include/etc/kernel/cmdline.d/99-no-rd-shell.cfg) ([`file.include`](/reference/features/#file-include)) | Strips `rd.shell` and `rd.emergency` kernel parameters and appends `rd.shell=0 rd.emergency=poweroff systemd.gpt_auto=0`, closing all emergency escape hatches in the initrd. |
| [`initrd.include/etc/systemd/system/check-secureboot.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_trustedboot/initrd.include/etc/systemd/system/check-secureboot.service) (`initrd.include`) | Initrd service ordered before `local-fs.target` (via `local-fs.target.requires/`) that runs `check-secureboot` and triggers `emergency.target` (immediate halt) if Secure Boot is not active. |
| [`initrd.include/etc/systemd/system/emergency.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_trustedboot/initrd.include/etc/systemd/system/emergency.service) (`initrd.include`) | Overrides the standard emergency shell: replaces `ExecStart` with `halt -f`, preventing any interactive access if the system enters emergency mode. |
| [`initrd.include/etc/systemd/system/local-fs.target.requires/check-secureboot.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_trustedboot/initrd.include/etc/systemd/system/local-fs.target.requires/check-secureboot.service) (`initrd.include`) | Symlink ordering `check-secureboot.service` as a requirement of `local-fs.target`, ensuring the Secure Boot check runs before any local filesystem is mounted. |
| [`initrd.include/usr/bin/check-secureboot`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_trustedboot/initrd.include/usr/bin/check-secureboot) (`initrd.include`) | Script invoked by `check-secureboot.service`: reads the `SecureBoot` EFI variable from `/sys/firmware/efi/efivars/`; logs an error and exits non-zero if Secure Boot is not active (`1`). |

### Related features

**Includes:**

- [`_usi`](/reference/features/_usi) — provides the UKI boot mode (embedded EROFS root in
  a signed EFI binary) that Trusted Boot depends on. Signing the UKI implicitly signs the
  root filesystem.
- [`_ephemeral`](/reference/features/_ephemeral) — the default `/var` storage mode for
  Trusted Boot: a fresh randomly-keyed encrypted partition on every boot. No data persists
  across reboots, providing the strongest protection against offline attacks.

**Excludes (incompatible with):**

- [`_nocrypt`](/reference/features/_nocrypt) — a plaintext `/var` partition is incompatible
  with the integrity guarantees of Trusted Boot.
- [`_unsigned`](/reference/features/_unsigned) — unsigned EFI binaries bypass Secure Boot
  entirely; incompatible with a signed and verified boot chain.

**Closely pairs with:**

- [`_tpm2`](/reference/features/_tpm2) — optional replacement for [`_ephemeral`](/reference/features/_ephemeral)
  when persistent `/var` state is needed. Seals the `/var` encryption key to TPM 2.0 PCR 7,
  so the key is only released when the Secure Boot state is unchanged. Use
  [`_tpm2`](/reference/features/_tpm2) instead of (not in addition to)
  [`_ephemeral`](/reference/features/_ephemeral).

### Further reading

- [Secure Boot and Trusted Boot](/explanation/secure-boot) — trust model, security guarantees,
  feature dependency table, mutable data modes, build and deploy instructions
- [Boot Modes](/explanation/boot-modes) — USI vs. Legacy comparison, mutable data mode overview
- [Building Images: Secureboot / Trustedboot / TPM2](/how-to/building-images#secureboot-trustedboot-tpm2) — certificate generation and build steps
- [Deploying Secure Boot Images](/how-to/secure-boot) — cloud-provider enrollment steps
- [Unified Kernel Image specification](https://uapi-group.org/specifications/specs/unified_kernel_image/)
- [Lennart Poettering: Fitting Everything Together](https://web.archive.org/web/20260714124711/https://0pointer.net/blog/fitting-everything-together.html) — design background for UKI-based OS images

## Related topics

<RelatedTopics />
