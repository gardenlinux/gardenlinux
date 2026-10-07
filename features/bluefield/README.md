---
title: "Feature: bluefield"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/bluefield/README.md
github_target_path: docs/reference/features/bluefield.md
---

:::warning
This feature is experimental and is not production-ready. It is not built or
tested in the nightly CI pipeline. Expect rough edges and incomplete documentation.
:::

## Feature: bluefield

### Description

A [platform](/reference/glossary.html#platform) feature that builds a Garden Linux
image for the [NVIDIA BlueField](https://www.nvidia.com/en-us/networking/products/data-processing-unit/)
Data Processing Unit (DPU) SmartNIC. The image is PXE-booted from an ARM64 host and
optionally installed onto the BlueField eMMC.

### What it does

Configures Garden Linux for the BlueField DPU hardware platform:

- **Kernel modules in initramfs**: the
  [`dracut`](https://github.com/dracutdevtools/dracut) configuration adds BlueField-specific
  modules to the initramfs — virtio console (`mlxbf_tmfifo`, `virtio_console`), eMMC storage
  (`dw_mmc-bluefield`, `dw_mmc`, `sdhci`, `sdhci-of-dwcmshc`, `mmc_block`), NVMe and RDMA
  (`nvme`, `nvme-rdma`, `nvme-tcp`, `ib_umad`, `ib_ipoib`, `ib_iser`), and firmware flashing
  (`mlxfw`).
- **Console**: kernel command line sets `hvc0` (BlueField virtual console via `rshim`) and
  `ttyAMA0` (ARM serial) as boot consoles.
- **Autologin**: root autologin enabled on both `tty1` and the serial console, suitable for
  the PXE live environment where no user accounts are configured.
- **PCI/USB IDs**: monthly cron jobs and a helper script keep the PCI and USB device ID
  databases current.
- **Persist scripts**: an interactive installer (`install.sh`) with a partition layout
  (`install.part`) and fstab template (`install.fstab`) for writing the live system to the
  BlueField eMMC.
- **Proprietary driver packages**: the `hack/` directory contains scripts to build
  out-of-tree Mellanox kernel module packages (`mlx-trio`, `mlxbf-livefish`, `mlxbf-pka`,
  `mlxbf-ptm`, `pwr-mlxbf`) that cannot be distributed in the Garden Linux repository due
  to licensing restrictions. These must be built before the image and copied into
  `file.include/opt/` before running the build.
- **`exec.config`**: installs the pre-built `.deb` packages from `/opt/` into the rootfs
  at build time.

#### Required BlueField drivers

According to NVIDIA, the following drivers are needed to run a BlueField SmartNIC.

| Driver | GL Kernel | Kernel config | GL Package | BF2 | BF3 | Comment |
|---|---|---|---|---|---|---|
| `bluefield-edac` | `m` | `EDAC_BLUEFIELD` | | ✓ | | |
| `dw_mmc_bluefield` | `m` | `MMC_DW_BLUEFIELD` | | ✓ | | |
| `sdhci-of-dwcmshc` | `m` | `MMC_SDHCI_OF_DWCMSHC` | | ✓ | | |
| `gpio-mlxbf2` | `m` | `GPIO_MLXBF2` | | ✓ | | |
| `gpio-mlxbf3` | `m` | `GPIO_MLXBF3` | | | ✓ | |
| `i2c-mlx` | `m` | `I2C_MLXBF` | | ✓ | | |
| `ipmb-dev-int` | `m` | `IPMB_DEVICE_INTERFACE` | | ✓ | | |
| `ipmb-host` | | | | | | Not needed for the BF2 use case |
| `mlxbf-gige` | `m` | `MLXBF_GIGE` | | ✓ | | |
| `mlxbf-livefish` | | | `hack/mlxbf-livefish` | ✓ | | Licensing: build locally |
| `mlxbf-pka` | | | `hack/mlxbf-pka` | ✓ | | Licensing: build locally |
| `mlxbf-pmc` | `m` | `MLXBF_PMC` | | ✓ | | |
| `mlxbf-ptm` | | | `hack/mlxbf-ptm` | ✓ | | Licensing: build locally |
| `mlxbf-tmfifo` | `m` | `MLXBF_TMFIFO` | | ✓ | | |
| `mlx-bootctl` | `m` | `MLXBF_BOOTCTL` | | ✓ | | |
| `mlx-trio` | | | `hack/mlx-trio` | ✓ | | Licensing: build locally |
| `pwr-mlxbf` | | | `hack/pwr-mlxbf` | ✓ | | Licensing: build locally |

Drivers marked `m` in the GL Kernel column are enabled as modules in the Garden Linux
kernel. Drivers with a `hack/` entry in GL Package cannot be distributed as Debian
packages and must be built from source before building the image.

### How it works

#### Prerequisites

- An ARM64 build machine (the BlueField itself is ARM64).
- A server with a BlueField 2 SmartNIC.
- A network where PXE booting is possible on the SmartNIC out-of-band port.
- Setting up PXE boot infrastructure (DHCP server, TFTP/HTTP server) is outside the scope
  of this document.

#### Building the packages and the image

Build the proprietary driver packages first, then build the Garden Linux image:

```bash
git clone https://github.com/gardenlinux/gardenlinux.git
cd gardenlinux
cd features/bluefield/hack
./mlx-trio
chown $(id -un) packages/*
./mlxbf-livefish
chown $(id -un) packages/*
./mlxbf-pka
chown $(id -un) packages/*
./mlxbf-ptm
chown $(id -un) packages/*
./pwr-mlxbf
chown $(id -un) packages/*
# Copy built packages into the file.include tree so they are installed in the image
cp packages/* ../file.include/opt/
cd ../../..
./build bluefield
```

From the `.build/` directory, untar the archive with a name similar to
`bluefield_bfpxe-arm64-today-local.pxe.tar.gz`. The archive contains the kernel,
initrd, and SquashFS root used to PXE-boot the SmartNIC.

#### Smartnic console setup

Secure Boot must be disabled on the SmartNIC. Connect the out-of-band network port to a
network where PXE booting is possible.

To access the SmartNIC console from the host, install `rshim` and attach to the console:

```bash
screen /dev/rshim0/console
```

If the console is blank and unresponsive, reset the SmartNIC from the host:

```bash
echo "SW_RESET 1" > /dev/rshim0/misc
```

Once connected via the console, reset the card and wait for the UEFI/Setup prompt.
On a BlueField-2 card the prompt looks similar to:

```
Press ESC/F2/DEL twice    to enter UEFI Menu.
Press ENTER               to skip countdown.

3  seconds remain...
2  seconds remain...
1  seconds remain...
```

From the UEFI setup menu, navigate to the device boot manager and PXE-boot from the
out-of-band port.

#### PXE boot

Example [Kea](https://www.isc.org/kea/) DHCP server configuration to PXE-boot a
BlueField SmartNIC:

```json
{ "name": "XClient_iPXE", "test": "substring(option[77].hex,0,4) == 'iPXE'", "boot-file-name": "http://192.168.23.1/ipxe/bootbf" },
{ "name": "UEFI-64-11",    "test": "substring(option[60].hex,0,13) == 'NVIDIA/BF/PXE'", "boot-file-name": "ipxe/snponly.arm.efi", "next-server": "192.168.0.1" },
```

Recommended [iPXE](https://ipxe.org/) boot script:

```
#!ipxe

set base-url http://192.168.0.1/ipxe/bf
kernel ${base-url}/vmlinuz gl.ovl=/:tmpfs gl.url=${base-url}/root.squashfs gl.live=1 ip=dhcp console=hvc0 console=ttyAMA0 earlyprintk=hvc0 consoleblank=0
initrd ${base-url}/initrd
boot
```

This gives a live-booted Garden Linux system with root autologin and a tmpfs overlay on `/`.

#### Persistent installation

:::warning
The installer will destroy all data on the target device and remove all existing
bootloader entries.
:::

To install permanently onto the SmartNIC eMMC from the running live system:

```bash
cd /opt/persist
# Edit install.part and install.fstab if the default layout needs adjustment
./install.sh
# Follow the prompts: provide the target disk (/dev/mmcblk0), confirm twice,
# set a root password, then reboot.
```

Alternatively, the Mellanox BFB (BlueField Boot Image) install method is not yet
implemented.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Installs pre-built proprietary driver `.deb` packages from `/opt/` into the rootfs at build time. |
| [`file.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.exclude) ([ref](/reference/features/#file-exclude)) | Removes legacy networking init.d scripts and other files superseded by systemd-networkd. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: platform` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `ethtool`, `fdisk`, `dosfstools`, `efibootmgr`, `efitools`, `pciutils`, and the standard kernel (`linux-image-$arch`). |
| [`file.include/etc/cron.monthly/update-pciids`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/etc/cron.monthly/update-pciids) ([`file.include`](/reference/features/#file-include)) | Monthly cron job to refresh the PCI device IDs database. |
| [`file.include/etc/cron.monthly/update-usbids`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/etc/cron.monthly/update-usbids) ([`file.include`](/reference/features/#file-include)) | Monthly cron job to refresh the USB device IDs database. |
| [`file.include/etc/dracut.conf.d/90-virtio-console.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/etc/dracut.conf.d/90-virtio-console.conf) ([`file.include`](/reference/features/#file-include)) | Adds BlueField-specific kernel modules to the initramfs: virtio console, eMMC storage, NVMe/RDMA, firmware flashing, and related subsystems. |
| [`file.include/etc/kernel/cmdline.d/00-default.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/etc/kernel/cmdline.d/00-default.cfg) ([`file.include`](/reference/features/#file-include)) | Sets default kernel command line parameters including early console and root device label. |
| [`file.include/etc/kernel/cmdline.d/10-console.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/etc/kernel/cmdline.d/10-console.cfg) ([`file.include`](/reference/features/#file-include)) | Configures `hvc0` (BlueField virtual console) and `ttyAMA0` (ARM serial) as kernel boot consoles. |
| [`file.include/etc/kernel/entry-token`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/etc/kernel/entry-token) ([`file.include`](/reference/features/#file-include)) | Sets the boot entry token used by the bootloader. |
| [`file.include/etc/kernel/postinst.d/00-kernel-cmdline`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/etc/kernel/postinst.d/00-kernel-cmdline) ([`file.include`](/reference/features/#file-include)) | Regenerates the kernel command line after kernel package updates. |
| [`file.include/etc/kernel/postinst.d/00-ucode`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/etc/kernel/postinst.d/00-ucode) ([`file.include`](/reference/features/#file-include)) | Installs CPU microcode updates after kernel package installs. |
| [`file.include/etc/systemd/system/getty@tty1.service.d/autologin.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/etc/systemd/system/getty@tty1.service.d/autologin.conf) ([`file.include`](/reference/features/#file-include)) | Systemd drop-in enabling root autologin on `tty1` for the PXE live environment. |
| [`file.include/etc/systemd/system/serial-getty@.service.d/autologin.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/etc/systemd/system/serial-getty@.service.d/autologin.conf) ([`file.include`](/reference/features/#file-include)) | Systemd drop-in enabling root autologin on the serial console for the PXE live environment. |
| [`file.include/etc/udev/rules.d/69-nostbyrot.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/etc/udev/rules.d/69-nostbyrot.rules) ([`file.include`](/reference/features/#file-include)) | udev rules for storage device naming. |
| [`file.include/etc/udev/rules.d/71-intellldp.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/etc/udev/rules.d/71-intellldp.rules) ([`file.include`](/reference/features/#file-include)) | udev rules for Intel LLDP agent. |
| [`file.include/opt/persist/install.fstab`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/opt/persist/install.fstab) ([`file.include`](/reference/features/#file-include)) | fstab template used by `install.sh` for the persistent installation on BlueField eMMC (ROOT on ext4, EFI on vfat). |
| [`file.include/opt/persist/install.part`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/opt/persist/install.part) ([`file.include`](/reference/features/#file-include)) | GPT partition layout definition (510 MiB EFI + 4 GiB ROOT) for `install.sh`. |
| [`file.include/opt/persist/install.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/opt/persist/install.sh) ([`file.include`](/reference/features/#file-include)) | Interactive script that partitions the BlueField eMMC (`/dev/mmcblk0`), copies the live system, and installs the bootloader. |
| [`file.include/usr/sbin/update-usbids`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/file.include/usr/sbin/update-usbids) ([`file.include`](/reference/features/#file-include)) | Script invoked by the `update-usbids` cron job to download the latest USB device IDs. |
| [`hack/Dockerfile`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/hack/Dockerfile) | Container image definition for the package build environment (based on Garden Linux nightly). |
| [`hack/defaults`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/hack/defaults) | Shared build variables (`BUILDIMAGE`, `BUILDTARGET`) and `docker_run` helper function used by all `hack/` build scripts. |
| [`hack/mlx-trio`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/hack/mlx-trio) | Builds the `mlx-trio` out-of-tree Mellanox driver as a Debian package. Cannot be distributed due to licensing. |
| [`hack/mlxbf-livefish`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/hack/mlxbf-livefish) | Builds the `mlxbf-livefish` out-of-tree driver as a Debian package. Cannot be distributed due to licensing. |
| [`hack/mlxbf-pka`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/hack/mlxbf-pka) | Builds the `mlxbf-pka` out-of-tree driver as a Debian package, applying `mlxbf-pka.d/class_create.patch` for kernel API compatibility. Cannot be distributed due to licensing. |
| [`hack/mlxbf-pka.d/class_create.patch`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/hack/mlxbf-pka.d/class_create.patch) | Patch applied during the `mlxbf-pka` build to fix a kernel API compatibility issue. |
| [`hack/mlxbf-ptm`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/hack/mlxbf-ptm) | Builds the `mlxbf-ptm` out-of-tree driver as a Debian package. Cannot be distributed due to licensing. |
| [`hack/pwr-mlxbf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/bluefield/hack/pwr-mlxbf) | Builds the `pwr-mlxbf` out-of-tree driver as a Debian package. Cannot be distributed due to licensing. |

### Related features

**Includes:**

- [`server`](/reference/features/server) — provides the base server layer (networking, SSH, SELinux, audit) required for a bare-metal server platform.
- [`_legacy`](/reference/features/_legacy) — adds BIOS/legacy boot support; required for the BlueField UEFI + syslinux dual-boot setup.
- [`_bfpxe`](/reference/features/_bfpxe) — produces the PXE tarball (kernel, initrd, SquashFS) used to network-boot the BlueField SmartNIC.

**Excludes (incompatible with):**

- [`_selinux`](/reference/features/_selinux) — SELinux is not supported in the BlueField live-boot environment.
- [`firewall`](/reference/features/firewall) — the nftables firewall conflicts with the SmartNIC networking requirements in the live environment.

### Further reading

- [NVIDIA BlueField documentation](https://docs.nvidia.com/networking/category/bluefielddpu)
- [rshim documentation](https://github.com/Mellanox/rshim)
- [iPXE documentation](https://ipxe.org/docs)

## Related topics

<RelatedTopics />
