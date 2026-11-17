---
title: "Feature: _nvidia"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/_nvidia/README.md
github_target_path: docs/reference/features/_nvidia.md
---

## Feature: _nvidia

### Description

Configures kernel command line parameters required for NVIDIA GPU workloads, optimizing the system for GPU performance by disabling power-saving features and tuning PCIe and CPU governor settings.

### What it does

`_nvidia` adds a set of kernel parameters via `/etc/kernel/cmdline.d/50-nvidia.cfg` that are required for reliable and performant NVIDIA GPU operation, particularly in bare-metal OpenStack environments:

| Parameter | Purpose |
|---|---|
| `iommu=pt` | Enables IOMMU passthrough mode for direct device memory access |
| `idle=poll` | Disables CPU idle states to minimize GPU-related latency spikes |
| `nvidia.NVreg_DynamicPowerManagement=0x00` | Disables NVIDIA dynamic power management |
| `usbcore.autosuspend=-1` | Disables USB autosuspend |
| `nvme_core.default_ps_max_latency_us=0` | Disables NVMe power state transitions |
| `pcie_port_pm=off` | Disables PCIe port power management |
| `pcie_aspm.policy=performance` | Sets PCIe Active State Power Management to performance mode |
| `cpufreq.default_governor=performance` | Sets the CPU frequency governor to performance mode |

### Files

| File | Purpose |
|---|---|
| [`file.include/etc/kernel/cmdline.d/50-nvidia.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_nvidia/file.include/etc/kernel/cmdline.d/50-nvidia.cfg) ([`file.include`](/reference/features/#file-include)) | Adds NVIDIA GPU performance tuning parameters to the kernel command line. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_nvidia/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files in this feature to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/_nvidia/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: flag`. |
