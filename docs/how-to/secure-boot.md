---
title: "Deploying Secure Boot Images"
description: "How to deploy Garden Linux images with Secure Boot and Trusted Boot on cloud providers"
related_topics:
  - /explanation/boot-modes
  - /explanation/secure-boot
  - /how-to/building-images
  - /reference/adr/0005-secure-boot-keys-glci
migration_status: "done"
migration_source: "docs/legacy/02_operators/deployment/aws-secureboot.md, docs/legacy/02_operators/deployment/gcp-secureboot.md"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4630"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/secure-boot.md
github_target_path: docs/how-to/secure-boot.md
---

# Deploying Secure Boot Images

This guide explains how to build and deploy Garden Linux images with
[Secure Boot](/explanation/secure-boot#secure-boot) or
[Trusted Boot](/explanation/secure-boot#trusted-boot) on cloud providers. For
conceptual background, see
[Boot Modes](/explanation/boot-modes) and
[Secure Boot and Trusted Boot](/explanation/secure-boot).

## Prerequisites

Before deploying a Secure Boot or Trusted Boot image:

1. **Build the image** with [`_trustedboot`](/reference/features/_trustedboot)
   or [`_secureboot`](/reference/features/_secureboot) enabled.
2. **Generate the signing certificates** by running `./cert/build` before the
   build. See
   [Building Images: Secureboot / Trustedboot / TPM2](/how-to/building-images#secureboot-trustedboot-tpm2)
   for full build instructions including local and AWS KMS key storage.

## Key Handling

After running `./cert/build`, the `cert/` directory contains the signing
certificates in two formats needed for different cloud providers:

| File                 | Format | Purpose                                     |
| -------------------- | ------ | ------------------------------------------- |
| `secureboot.pk.esl`  | ESL    | AWS external enrollment, platform key       |
| `secureboot.kek.esl` | ESL    | AWS external enrollment, key exchange key   |
| `secureboot.db.esl`  | ESL    | AWS external enrollment, signature database |
| `secureboot.pk.der`  | DER    | GCP, Azure — platform key                   |
| `secureboot.kek.der` | DER    | GCP, Azure — key exchange key               |
| `secureboot.db.der`  | DER    | GCP, Azure — signature database             |
| `secureboot.db.crt`  | PEM    | Used for image signing during build         |

For [`_trustedboot`](/reference/features/_trustedboot) images, the `.auth`
format keys are embedded into the ESP during build
(`ESP/loader/keys/auto/{PK,KEK,db}.auth`), enabling auto-enrollment at first
boot (see [Auto-Key-Enrollment](#auto-key-enrollment)).

:::tip
The handling of Secure Boot signing keys in the release pipeline is described
in [ADR 0005](/reference/adr/0005-secure-boot-keys-glci). Official Garden Linux
release images use published `gardenlinux-secureboot.*.der` keys; locally built
images use the `secureboot.*.der` keys from your own `./cert/build` run.
:::

## Auto-Key-Enrollment

[`_trustedboot`](/reference/features/_trustedboot) images use
[systemd-boot](https://systemd.io/BOOT_LOADER_SPECIFICATION/)'s built-in
automatic key enrollment mechanism. No manual enrollment step is required on
platforms that support UEFI setup mode.

**How it works:**

1. During the build, `usi.config` places the signing keys in
   `ESP/loader/keys/auto/{PK,KEK,db}.auth` and writes `secure-boot-enroll
force` into `ESP/loader/loader.conf`.
2. On first boot, systemd-boot detects that UEFI is in setup mode (no keys
   enrolled yet) and automatically enrolls the keys from
   `ESP/loader/keys/auto/` into the UEFI variable store.
3. After enrollment, Secure Boot transitions from setup mode to user mode.
4. On all subsequent boots, UEFI validates the systemd-boot EFI binary and the
   signed UKI against the enrolled keys before executing them.
5. The `check-secureboot` initrd service verifies that Secure Boot is active
   after the kernel starts; if it is not, the system halts immediately.

:::info
The `secure-boot-enroll force` setting instructs systemd-boot to enroll
keys and immediately reboot after enrollment — the system boots correctly
into Garden Linux on the second boot. See the
[systemd-boot documentation](https://www.freedesktop.org/software/systemd/man/latest/loader.conf.html)
for further details on this directive.
:::

Auto-enrollment works out of the box on KVM/QEMU (with a Secure Boot-capable
OVMF firmware) and on cloud providers that launch instances in UEFI setup mode.
Where setup mode is not available (e.g. some cloud providers require keys at
instance creation time), use external enrollment as described in the
provider-specific sections below.

## Verifying Secure Boot status

On any running Garden Linux instance, verify that Secure Boot is active:

```bash
# Show Secure Boot status, TPM2 support and firmware information
sudo bootctl

# Check kernel messages for Secure Boot confirmation
journalctl | grep -i "secure boot"
```

Expected `bootctl` output when Secure Boot is active:

```
Secure Boot: enabled (user)
TPM2 Support: yes
```

Expected kernel log lines:

```
kernel: Kernel is locked down from EFI Secure Boot; see man kernel_lockdown.7
kernel: secureboot: Secure boot enabled
```

For [`_trustedboot`](/reference/features/_trustedboot) images, the
`check-secureboot` initrd service enforces this: if Secure Boot is not active,
the system halts before reaching userspace.

## Building Secure Boot images

Generate the signing certificates before building:

```bash
./cert/build
```

This builds the full certificate chain (PK, KEK, db) in a container. By
default, private keys are stored in `cert/` as local files. Use `--kms` to
store private keys in AWS Key Management Service instead.

Example build commands:

```bash
# KVM image with Trusted Boot and ephemeral /var (default)
./build kvm-trustedboot

# KVM image with Trusted Boot and persistent TPM 2.0 encrypted /var
./build kvm-trustedboot_tpm2

# AWS image with Trusted Boot
./build aws-trustedboot

# AWS image with Trusted Boot and TPM 2.0 encryption
./build aws-trustedboot_tpm2
```

:::tip
To test Trusted Boot locally on Linux or macOS with QEMU, use the `./test` script as described in [QEMU Testing](/how-to/testing/run-tests#qemu-testing) and [Debugging QEMU Environment](/how-to/testing/debug-tests#qemu-environment):

```bash
# Start VM with ssh and do not run tests
./test \
  --ssh \
  --skip-cleanup \
  --skip-tests \
  .build/kvm_tpm2_trustedboot-amd64-today-local.raw

# Connect to VM (from a second shell session)
tests/util/login_qemu.sh

# Check for enabled Secure Boot
gardenlinux@localhost:~$ dmesg | grep -i secureboot
[    0.000000] secureboot: Secure boot enabled
[    3.371648] integrity: Loaded X.509 cert 'SAP SE: Garden Linux dev secureboot db certificate: d322b116bab35b429565c61c8f636f2c5db55762'
[    3.923970] systemd[1]: Starting check-secureboot.service...
[    4.037614] systemd[1]: Finished check-secureboot.service.
[   10.311831] systemd[1]: Created symlink '/etc/systemd/system/sysinit.target.wants/systemd-pcrlock-secureboot-authority.service' → '/usr/lib/systemd/system/systemd-pcrlock-secureboot-authority.service'.
[   10.315374] systemd[1]: Created symlink '/etc/systemd/system/sysinit.target.wants/systemd-pcrlock-secureboot-policy.service' → '/usr/lib/systemd/system/systemd-pcrlock-secureboot-policy.service'.
```

:::

## Deploying on AWS

AWS supports UEFI Secure Boot for EC2 instances. See the
[AWS Secure Boot documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/uefi-secure-boot.html)
for the full reference.

For [`_trustedboot`](/reference/features/_trustedboot) images, auto-enrollment
works by default: AWS launches instances in UEFI setup mode, and systemd-boot
automatically enrolls the embedded keys on first boot. No manual step is
required.

To activate Secure Boot from the very first boot instead, provide a pre-filled
UEFI variable store blob at instance creation time. A blob is automatically created at `cert/secureboot.aws-efivars` and
can be provided as-is to the AWS tooling. See the
[AWS documentation for creating AMIs with a pre-filled UEFI variable store](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/create-ami-with-uefi-secure-boot.html#uefi-secure-boot-optionB)
for the full procedure.

## Deploying on Azure

Azure supports Secure Boot via
[Trusted Launch](https://learn.microsoft.com/en-us/azure/virtual-machines/trusted-launch),
which enables UEFI Secure Boot, vTPM, and integrity monitoring for supported VM
generations (Gen 2).

For deploying Garden Linux images with custom Secure Boot keys on Azure, see
[Azure Trusted Launch with custom UEFI keys](https://learn.microsoft.com/en-us/azure/virtual-machines/trusted-launch-secure-boot-custom-uefi).

The Garden Linux signing certificates in DER format (`cert/secureboot.*.der`)
must be uploaded to Azure alongside the image. The exact upload mechanism
depends on your Azure tooling (Azure CLI, ARM templates, or the Azure portal).

## Deploying on GCP

GCP supports Secure Boot via
[Shielded VM](https://docs.cloud.google.com/compute/shielded-vm/docs/shielded-vm),
which includes UEFI Secure Boot, vTPM, and integrity monitoring.

For creating Shielded VM images with Garden Linux signing keys, see the
[GCP documentation for creating shielded images](https://docs.cloud.google.com/compute/shielded-vm/docs/creating-shielded-images#adding-shielded-image).

Key enrollment is performed at image creation time by providing the DER-format
certificates as image metadata. The Garden Linux certificates from `cert/`
(`secureboot.pk.der`, `secureboot.kek.der`, `secureboot.db.der`) can be
provided as-is to the GCP tooling — no conversion is needed.

## Deploying on OpenStack

OpenStack Nova supports UEFI Secure Boot for instances. See the
[OpenStack Nova Secure Boot documentation](https://docs.openstack.org/nova/2026.1/admin/secure-boot.html)
for the full operator reference.

To use Secure Boot with a Garden Linux image on OpenStack, set the
`os_secure_boot` image property when uploading to Glance:

```bash
openstack image set --property os_secure_boot=required <image-id>
```

The exact Secure Boot enforcement depends on your OpenStack deployment and
the hypervisor configuration. Consult your OpenStack administrator for the
supported Secure Boot modes and UEFI variable handling in your environment.

## Related topics

<RelatedTopics />
