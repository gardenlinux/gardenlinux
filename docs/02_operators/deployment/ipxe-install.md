## Installing Garden Linux on metal with IPXE

## Idea
The installation procedure runs in a live version of Garden Linux. For this the kernel and initramfs image are booted through a network boot environment like iPXE. In the initramfs stage a dracut module (*98-gardenlinux-live*) will try to fetch, load and mount a squashfs image (which can be produced with the *_pxe* feature) as the root filesystem. This compressed image contains a 'unconfigured' root fs of Garden Linux. In the next step Ignition will configure the system by adding users, files (e.g. configuration files like /etc/network/hostname) and systemd services. One of them is the install script itself (*install.service*), which is executed once the initramfs stage is complete.

The installation procedure itself consists of copying the live instance to a specified disk while installing an appropriate bootloader. The system then switches directly into the installed OS. Here is an overview:

<img src="../.media/firstboot.svg">

The installation process is not invoked on every boot of the system but only on firstboot. Just before completing the installer disables the dracut module responsible for livebooting and removes the installer. On UEFI systems also the boot order is changed so that subsequent boots go straight to GardenLinux.

<img src="../.media/subsboots.svg">

#### disk layout & format
The targeted disk will have two partitions. The first partition is created to be *ESP (Efi System Partition)* compatible and serve the bootloaders (see *bootloader installation*). Garden Linux will install its rootfs to the second partition with ext4 format.

#### bootloader installation
During the installation the firmware type is detected and a corresponding bootloader is automatically installed. 
- For Legacy systems this is *syslinux*. A new MBR is written to the first sector of the disk and stages 2+ of the syslinux bootloader are installed to the first partition. 
- For UEFI systems *systemd-boot* is used to boot a unified kernel image (*UKI*) created by *dracut*. A *UKI* is "a single EFI PE executable combining an EFI stub loader, a kernel image, an initramfs image, and the kernel command line" [[src](https://systemd.io/BOOT_LOADER_SPECIFICATION/#type-2-efi-unified-kernel-images)]. This standalone EFI binary can be signed to be used in Secure Booting.

Thus GardenLinux will install on both Legacy and UEFI systems with identical disk layout. One advantage of this setup is that changing systems is easy: To migrate an existing installation from one system to another it suffices to invoke the appropriate firmware specific part of the installation script.

## Setup
### Prerequisites

- Target clients with BIOS or UEFI firmware

- Garden Linux build with *_pxe*, *metal* , *server* features. This generates a compressed root squashfs image (root.squashfs) and the associated functionality for live booting Garden Linux over a network.

- A TFTP server to provide the binaries for iPXE for Legacy and UEFI (see https://boot.ipxe.org)

- A DHCP server to provide access to a boot file. If the client's current net booting environment is iPXE then DHCP offers a HTTP URL locating the iPXE  configuration script. Otherwise the TFTP server's IP address and the filename of the appropriate iPXE image is offered (see https://ipxe.org/howto/dhcpd#pxe_chainloading).

- A web server to provide the Garden Linux build images (rootfs.vmlinuz, rootfs.initrd, root.squashfs), iPXE and Ignition configuration files.

### How it works
```
┌────────────┐
│  Power on  ├──────┐
└────────────┘      │
                    ▼
             ┌─────────────┐
             │  firmware   │
             │ UEFI / BIOS ├──────┐
             └─────────────┘      │
                                  ▼
                           ┌─────────────┐
                           │   netboot   │         ┌────────┐   ┌────────┐
                           │ environment │         │  DHCP  │   │  TFTP  │
                           └──────┬──────┘         └───┬────┘   └───┬────┘
                                  │                    │            │
                                  │   IP allocation,...│            │
                                  │   TFTP address     │            │
                                  │◄──────────────────►│            │
                                  │   filename iPXE    │            │
                                  │                    │            │
                                  │    UEFI: ipxe.efi  │            │
                                  │    BIOS: undionly.kpxe          │
                                  │                    │            │
                                  │                    │            │
                                  │                    │            │
                                  │   get iPXE         │            │
                                  │◄───────────────────┼──────────► │
                                  │                    │            │
                                  │                    │            │
                                  │                    │            ┊
                                  │                    │
                                  ▼                    │
                           ┌─────────────┐             │
                           │    IPXE     │             │        ┌────────┐
                           │ environment │             │        │  HTTP  │
                           └──────┬──────┘             │        └───┬────┘
                                  │  IP allocation,... │            │
                                  ├────────────────────┤            │
                                  │  filename: URL to  │            │
                                  │      boot.ipxe     ┊            │
                                  │                                 │
                                  │                                 │
                                  │          GET boot.ipxe          │
                                  ├─────────────────────────────────┤
                                  │                                 │
                                  │          GET rootfs.vmlinuz     │
                                  │              rootfs.initrd      │
                                  ├─────────────────────────────────┤
                                  │                                 │
                                  │                                 │
                                  │                                 │
                                  │                                 │
                                  ▼                                 │
                              ┌────────┐                            │
                              │  boot  │                            │
                              └───┬────┘                            │
                                  │                                 │
                                ┌─┴─┐                               │
                                │   │      GET ignition.json        │
                                │   │◄─────────────────────────────►│
                                |   |                               |
             Ignition (fetch)   │   │      GET install.json         │
                                │   │◄─────────────────────────────►│
                                │   │                               │
                                ┊   ┊                               │
                                .   .                               │
                                 ┌ ┐                                │
                                 │ │      GET root.squashfs         │
            live-get-squashfs    │ │◄──────────────────────────────►│
                                 │ │                                │
                                 └ ┘                                │
                                .   .                               ┊
                                ┊   ┊ 
                                │   │
                                │   │
             Ignition (files)   │   │ 
                                │   │
                                │   │
                                └─┬─┘
                                  │
                     initramfs ───┼─── complete
                                  │
                                  │
                                 ┌┴┐
                                 │ │
                                 │ │
                        install  │ │
                                 │ │
                                 │ │
                                 └─┘
```
Three configuration files are needed (see *examples/ipxe-install*):

### iPXE - boot.ipxe
This is the configuration file used by iPXE to boot Garden Linux:
`boot.ipxe`
```bash
#!ipxe

set base-url #URL_TO_HTTP_SERVER 
kernel ${base-url}/rootfs.vmlinuz initrd=rootfs.initrd gl.ovl=/:tmpfs gl.url=${base-url}/root.squashfs gl.live=1 ip=dhcp console=ttyS1,115200n8 console=tty0 earlyprintk=ttyS1,115200n8 consoleblank=0 ignition.firstboot=1 ignition.config.url=${base-url}/ignition.json ignition.platform.id=metal
initrd ${base-url}/rootfs.initrd
boot
```

`gl.ovl=/:tmpfs`, `gl.url=${base-url}/root.squashfs`, `gl.live=1`

This tells GardenLinux to run live. The rootfs is going to be an OverlayFS with root.squashfs (downloaded from *gl.url*) as lower and a tmpfs as an upper dir.

`ip=dhcp`

Configure network devices via DHCP

`ignition.config.url=${base-url}/ignition.json`

URL to Ignition configuration file.

`ignition.firstboot=1`

Tells Ignition that this is a firstboot. Ignition applies instructions only on firstboot.

`ignition.platform.id=metal`

Tells Ignition the platform that is run. See [[link](https://docs.fedoraproject.org/en-US/fedora-coreos/platforms/)] for well known platforms.

### Ignition - ignition.json + install.json

[Ignition](https://github.com/coreos/ignition) configures the system prior to installation. It is mainly used here to write files (regular and systemd units) as instructed by the configuration file from the URL specified in boot.ipxe. Ignition only executes on firstboots.
To improve human readability configs can also be written in *yaml* and translated to *json* by [Butane](https://github.com/coreos/butane).

The main installation procedure is supplied through a seperate ignition configuration file: `install.yaml` (see *examples/ipxe-install*) and must be loaded by `ignition.json`.

This is a minimal `ignition.yaml`:

```yaml
variant: fcos
version: 1.3.0
ignition:
  config:
    merge:
      - source: #URL to install.json
storage:
  files:
  - path: /opt/onmetal-install/partitions
      overwrite: yes
      mode: 0755
      contents:
        inline: |
          label: gpt
          type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, name="EFI", size=510MiB
          type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, name="ROOT"
    - path: /opt/onmetal-install/target
      overwrite: yes
      mode: 0755
      contents:
        inline: |
          disk=/dev/sda
```
Here the partition layout [ */opt/onmetal-install/partitions* ] and target disk [ */opt/onmetal-install/target* ] can be specified. 
> Attention: The first two partitions must be specified as above. Partitions may be appended when sufficient size for *ROOT* partition is ensured.
 
Additional Ignition instruction may be placed here. For e.g. configuring the hostname the following can be appended under `files:` in the above file:
```yaml
- path: /etc/hostname
      overwrite: yes
      mode: 0644
      contents:
        inline: |
          >HOSTNAME<
```
Further Ignition capabilities can be found here: [link](https://coreos.github.io/ignition/examples/).
