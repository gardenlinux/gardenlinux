---
title: "Feature: _tpm2"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_tpm2/README.md
github_target_path: docs/reference/features/_tpm2.md
---

# TPM2

The `_tpm2` feature enables a TPM 2.0-backed encrypted var partition. The var partition is encrypted with a key sealed to the TPM 2.0, tying it to the measured boot state of the system.

- Feature type: flag
- Excludes: `_ephemeral`, `_nocrypt`

## Overview

When the `_tpm2` feature is applied, the var partition uses TPM 2.0 for key management. The encryption key is sealed against the TPM's Platform Configuration Registers (PCRs), so the partition can only be unlocked when the system boots into a known-good state. This provides protection against offline attacks and unauthorized modifications to the boot chain.

The `_tpm2` feature is typically combined with the `_trustedboot` feature to establish a fully measured and attested boot chain:

```
./build kvm_dev_trustedboot_tpm2
```

## Related Features

- [\_trustedboot](/reference/features/_trustedboot.md) – Fully trusted bootchain; required for meaningful PCR-based key sealing. See that page for build and test instructions.
- [\_ephemeral](/reference/features/_ephemeral.md) – Alternative to `_tpm2`; provides an ephemeral encrypted var partition without TPM-backed key sealing. Mutually exclusive with `_tpm2`.
- [\_nocrypt](/reference/features/_nocrypt.md) – Disables encryption of the var partition entirely. Mutually exclusive with `_tpm2`.
