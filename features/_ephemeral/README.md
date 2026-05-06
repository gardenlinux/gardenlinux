---
title: "Feature: _ephemeral"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_ephemeral/README.md
github_target_path: docs/reference/features/_ephemeral.md
---

# Ephemeral

The `_ephemeral` feature provides an ephemeral encrypted var partition. The partition is encrypted with a key generated fresh on each boot, so all data written to the var partition is lost when the system reboots.

- Feature type: flag
- Excludes: `_nocrypt`

## Overview

When the `_ephemeral` feature is applied, the var partition is encrypted using a key that is generated at boot time and never persisted. This means:

- The var partition contents do not survive a reboot.
- No persistent state is written to the encrypted var partition across reboots.
- The encryption still protects data at rest during a running session, but provides no continuity between boots.

The `_ephemeral` feature is typically combined with `_trustedboot` to establish a fully attested boot chain where the ephemeral partition state is tied to the measured boot:

```
./build kvm_dev_trustedboot_ephemeral
```

## Related Features

- [\_trustedboot](/reference/features/_trustedboot.md) – Fully trusted bootchain. See that page for build and test instructions.
- [\_tpm2](/reference/features/_tpm2.md) – Alternative to `_ephemeral`; uses TPM 2.0 to seal a persistent encryption key to the boot state. Mutually exclusive with `_ephemeral`.
- [\_nocrypt](/reference/features/_nocrypt.md) – Disables encryption of the var partition entirely. Mutually exclusive with `_ephemeral`.
