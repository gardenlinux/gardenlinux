---
title: "Confidential Computing"
description: How Confidential Computing can be used to protect Garden Linux boot VMs from the hypervisor
related_topics:
  - /how-to/confidential-computing/confidential-computing.md
github_target_path: "docs/explanation/confidential-computing.md"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/explanation/confidential-computing.md
---

# Confidential Computing

Confidential Computing technologies protect data in use through performing computations within
hardware-based Trusted Execution Environments (TEEs). Current Confidential Computing technologies,
such as AMD SEV-SNP and Intel TDX, provide the protection through confidential and integrity
protected virtual machines (VMs), called confidential VMs (CVMs). The memory of a CVM is protected
against the untrusted rest of the system including privileged components, such as the hypervisor.

Combined with protection of data at rest (e.g., Full Disk Encryption (FDE)) and protection of data in
transit (e.g., TLS), this aims to enable processing and storage of data in untrusted clouds with
protection from the Cloud Service Provider (CSP).

To verify that the Confidential Computing protections are actually enforced without physical access
to the cloud infrastructure, Confidential Computing technologies require a mechanism to remoty
attest to its correct state, as well as the integrity of the code running within the TEE. Usually,
this is realized similar to Trusted Platform Module (TPM)-based attestation: the hardware records
measurements (hashes) of software before it is being run. Upon request, the hardware produces a
signed data structure that contains these hashes or a summary of these hashes, as well as user
supplied data for freshness (nonce). A remote verifier can verify this data structure including the
hashes and determine the security state of the platform.

## AMD SEV-SNP

[AMD SEV-SNP](https://www.amd.com/system/files/TechDocs/SEV-SNP-strengthening-vm-isolation-with-integrity-protection-and-more.pdf)
enables encryption of memory and CPU register state using and provides integrity protection. AMD
SEV-SNP is implemented utilizing the AMD Secure Processor, an ARM-based co-processor that is
integrated into AMD EPYC CPUs. It exposes an API to the guest VM for attestation and key derivation,
as well as an API to the hypervisor for CVM life-cycle management. Attestation reports are signed
with a key (Versioned Chip Endorsement Key (VCEK)) that is derived from the unique chip ID as well
as the software versions of the AMD TCB. The key's corresponding certificate is embedded into a
certificate chain that routes back to the AMD CA.

Attestation reports contain a single SHA-384 measurement representing the
launch digest of the \gls{CVM}. Runtime measurements require addtional mechanisms, such as vTPMs,
which are embedded into the VM, but separated from virtual firmware and kernel.

## Intel TDX

[Intel TDX](ttps://software.intel.com/content/dam/develop/external/us/en/documents/tdx-whitepaper-final9-17.pdf)
CVMs (also called Trust Domains (TD)) provide similar protection compared to AMD SEV-SNP. However,
Intel uses a multi-component architecture comprising Virtual Machine Extensions (VMX), Instruction
Set Architecture (ISA) extensions, the Intel TDX-module, as well as Intel SGX enclaves for
attestation.

The Intel TDX module acts as an intermediary between CVM and Virtual Machine Monitor (VMM) /
hypervisor. Compared to the single AMD SEV-SNP measurement register, Intel TDX provides a set of
registers: The TDX module is measured into a special register, the MRSEAM register.
The launch state of the CVM is measured into the MRTD register, which is similar to AMD's
measurement register. Runtime measurements are measured into 4 RTMR registers via the extend
operation, that allows recording multiple measurements into one register. Intel TDX writes event
logs (CCEL) to reconstruct the value of an RTMR register, similar to TPM event logs.

## Garden Linux CVMs

The Garden Linux kernel config supports running Garden Linux VMs as confidential VMs on all AMD
SEV-SNP-capable servers (AMD EPYC server generation Milan and onwards), as well ss Intel TDX-capable
servers (Intel Xeon 4th Gen Scalable or newer).

How to setup Garden Linux Confidential VMs is explained in the following
[how-to article](../how-to/confidential-computing/confidential-vms.md).