---
title: "Container Virtual Machines"
description: "How to run Garden Linux AMD SEV-SNP and Intel TDX Confidential VMs"
related_topics:
  - /explanation/confidential-computing.md
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/confidential-computing/confidential-vms.md
github_target_path: docs/how-to/confidential-computing/confidential-vms.md
---

# Confidential VMs

Garden Linux can be run as a confidential virtual machine (CVM) on AMD SEV-SNP and Intel TDX
hosts.

## Prerequisites

The following prerequisites must be met for confidential guest support

### Intel
- Intel Xeon processor with TDX support (4th Gen Scalable or newer)
- QEMU 10.2.0 or higher
- OVMF / EDK2 edk2-stable202405 or higher
- Host Kernel 6.16 or higher
- Guest Linux Kernel 5.19 or higher
- [Intel TDX enabled](https://cc-enabling.trustedservices.intel.com/intel-tdx-enabling-guide/01/introduction/)
- Attestation:
  [Intel Quote Generation Service (QGS)](https://cc-enabling.trustedservices.intel.com/intel-tdx-enabling-guide/05/host_os_setup/)
  running on host

### AMD-only
- AMD EPYC processor with SNP support (Milan or newer)
- QEMU 9.1 or higher
- OVMF / EDK2 edk2-stable202405 or higher
- Host Kernel 6.11 or higher
- Guest Kernel 6.11 or higher
- Host BIOS: [AMD SEV-SNP enabled](https://github.com/AMDESE/AMDSEV/)

## Build

The Garden Linux default kernel build brings support for AMD SEV-SNP and Intel TDX, therefore any
KVM-flavor is suitable.

The following example uses a KVM development build:
```sh
./build kvm_dev-amd64
```

## Run

The built VM image can be run on any host fulfilling the
[prerequisites](./confidential-vms.md#prerequisites). As a PoC and for testing, you can run the CVM
via the [start-vm](../../../bin/start-vm) script:

Run PoC Garden Linux CVM with Intel TDX memory encryption:
```Sh
./bin/start-vm \
      --tdx \
      --cvm-fw /path/to/OVMF.fd \
      .build/kvm_dev-amd64-*.raw
```

You can check that memory encryption is active via:
```sh
dmesg | grep -i tdx
```
Expect a log like this:
```
[    0.382918] Memory Encryption Features active: Intel TDX
```

Run POC Garden Linux CVMs with AMD SEV-SNP memory encryption:
```sh
./bin/start-vm \
      --snp \
      --cvm-fw /path/to/OVMF.fd \
      .build/kvm_dev-amd64-*.raw
```

You can check that memory encryption is active via:
```sh
dmesg | grep -i snp
```
Expect a log like this:
```
[    0.574117] Memory Encryption Features active: AMD SEV SEV-ES SEV-SNP
```

There is also a convenience script for starting CVMs on any platform with the latest image.
[start-vm](../../../bin/start-vm) parameters are forwarded:
```sh
./hack/start-confidential-vm
```