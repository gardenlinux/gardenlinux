---
title: "Feature: _signed"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
  - /explanation/secure-boot
  - /explanation/boot-modes
  - /how-to/secure-boot
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_signed/README.md
github_target_path: docs/reference/features/_signed.md
---

## Feature: _signed

### Description

Signs the systemd-boot EFI binary and the Unified Kernel Image (UKI) during the
image build, for use with UEFI [Secure Boot](/reference/glossary#secure-boot).

:::warning This does not protect you from manipulations of the unencrypted `/var` filesystem, by adding files there or the `/var/etc.overlay` directory code still can be injected into the system.

If you are looking to protect yourself from that then you should concider using [`_trustedboot`](/reference/features/_trustedboot) and/or [`_tpm2`](/reference/features/_tpm2). :::

### What it does

`_signed` includes [`_usi`](/reference/features/_usi) and excludes
[`_unsigned`](/reference/features/_unsigned). During the USI build, `usi.post`
uses `sbsign` to sign both the systemd-boot EFI binary and the UKI. It accepts a
local private key or an AWS KMS PKCS#11 key, along with the Secure Boot signing
certificate.

This feature signs the image .efi files. It does not add runtime Secure Boot
verification or emergency-shell restrictions. Those are separate Trusted Boot
behaviors.

`_usi` includes [`_nocrypt`](/reference/features/_nocrypt), so `/var` is a
persistent, unencrypted ext4 partition.

### How it works

`_signed` runs `usi.post` after the `_usi` image builder creates the UKI and ESP:

1. Selects a signing key from `/builder/cert/secureboot.db.key` or, when using
   AWS KMS, the ARN in `/builder/cert/secureboot.db.arn`. The matching
   certificate is `/builder/cert/secureboot.db.crt`.
2. Signs the architecture-specific systemd-boot EFI binary and writes it to
   `EFI/BOOT/BOOTX64.EFI` or `EFI/BOOT/BOOTAA64.EFI` in the ESP.
3. Copies the Secure Boot `PK`, `KEK`, and `db` authorization files into
   `EFI/loader/keys/auto/` and writes `loader/loader.conf`. The
   `secure-boot-enroll force` setting is commented out, so this script does not
   enable automatic key enrollment.
4. Signs the UKI and places it at
   `EFI/Linux/$BUILDER_VERSIONED_FLAVOR.efi` in the ESP.

Generate the Secure Boot certificates and prepare signing keys as described in
[Building Images: Secureboot, Trustedboot and TPM2](/how-to/building-images#build-secureboot-trustedboot-and-tpm2-images).

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_signed/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `_signed` as a flag that includes [`_usi`](/reference/features/_usi) and excludes [`_unsigned`](/reference/features/_unsigned). |
| [`requirements.mod`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_signed/requirements.mod) | Requires the build target to support Secure Boot (`requirements["secureboot"]=true`). |
| [`usi.post`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_signed/usi.post) | Selects a local or AWS KMS signing key, signs systemd-boot and the UKI, copies Secure Boot authorization files into the ESP, and writes the boot loader configuration. |

### Related features

**Includes:**

- [`_usi`](/reference/features/_usi) — provides the UKI and embedded EROFS root image. `_usi`
  includes [`_nocrypt`](/reference/features/_nocrypt), which provides persistent plain ext4
  storage for `/var`.

**Excludes (incompatible with):**

- [`_unsigned`](/reference/features/_unsigned) — builds unsigned EFI binaries instead.

### Further reading

- [Secure Boot and Trusted Boot](/explanation/secure-boot) — trust model, security guarantees,
  feature dependency table, mutable data modes, build and deploy instructions
- [Boot Modes](/explanation/boot-modes) — USI vs. Legacy comparison, mutable data mode overview
- [Building Images: Secureboot, Trustedboot and TPM2](/how-to/building-images#build-secureboot-trustedboot-and-tpm2-images) — certificate generation and build steps
- [Deploying Secure Boot Images](/how-to/secure-boot) — cloud-provider enrollment steps
- [Unified Kernel Image specification](https://uapi-group.org/specifications/specs/unified_kernel_image/)
- [Lennart Poettering: Fitting Everything Together](https://web.archive.org/web/20260714124711/https://0pointer.net/blog/fitting-everything-together.html) — design background for UKI-based OS images

## Related topics

<RelatedTopics />
