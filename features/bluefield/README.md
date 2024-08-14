## WARNING! This is at the moment still just a POC and therefore experimental

This guide / readme is providing information on how to get a bare minimum GardenLinux setup running on a bluefield smartnic.
It covers nothing on how to actually "use" it, like setting up VFs, offloading, etc. 

### Prerequisites
- access to an ARM64 machine in order to build this
- access to a server with a bluefield 2 smartnic
- ability to PXE boot said bluefield smartnic (setting up PXE booting is not covered by this readme)

### Build packages and build GardenLinux
```
git clone https://github.com/gardenlinux/gardenlinux.git
cd gardenlinux
# needed till this gets merged to main
git checkout feat/bluefield
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
# copy/move packages in order to be installed when building
cp packages/* ../file.include/opt/
./build bluefield
```
From the _.build_ directory, untar the file with the name similar to _bluefield_bfpxe-arm64-today-local.pxe.tar.gz_
The archive contains the kernel, initrd and squashfs used to PXE boot the smartnic.

### Smartnic setup
Secureboot must be disabled. The oob network port on the smartnic should be connected to a network where pxe booting is possible.
To "manually" pxe boot, one should install _rshim_ on the host system and attach to the console. One easy way of doing that is 
```
screen /dev/rshim0/console
```
In the special case that the console is blank, nothing responds anymore and seems stuck, the smartnic can be reset from the host by doing
```
echo "SW_RESET 1" > /dev/rshim0/misc
```
Once connected to the smartnic via the console, reset the card and wait to be prompted to enter UEFI/Setup and pressing ESC/Delete - usually delete
On a bluefield-2 card it looks similar to:
```
Press ESC/F2/DEL twice    to enter UEFI Menu.
Press ENTER               to skip countdown.

3  seconds remain...
2  seconds remain...
1  seconds remain...
```
From the setup, navigate to the device boot manager and pxe boot from the oob port.

### PXE boot 
Example kea dhcp server config to PXE boot
```
      { "name": "XClient_iPXE", "test": "substring(option[77].hex,0,4) == 'iPXE'", "boot-file-name": "http://192.168.23.1/ipxe/bootbf" },
      { "name": "UEFI-64-11",    "test": "substring(option[60].hex,0,13) == 'NVIDIA/BF/PXE'", "boot-file-name": "ipxe/snponly.arm.efi", "next-server": "192.168.0.1" },
```
The following ipxe script is recommended to be used when booting. It sets the kernel, initrd, gl.ovl for a root overlay filesystem (tmpfs), gl.url specifies where the squashfs should be fetched from, ip=dhcp configures systemd-networkd to use dhcp, console settings specific for the smartnic and the rest are self explanatory. 
```
#!ipxe

set base-url http://192.168.0.1/ipxe/bf
kernel ${base-url}/vmlinuz gl.ovl=/:tmpfs gl.url=${base-url}/root.squashfs gl.live=1 ip=dhcp console=hvc0 console=ttyAMA0 earlyprintk=hvc0 consoleblank=0
initrd ${base-url}/initrd
boot
```
By using these configs, you end up with a "classic" live booted GardenLinux system, with root user autologin and an overlay for / 

### Persist / install on smartnic

- similar to a regular server - partition mmcblk0, fortmat the partitions, copy everything from the squashfs, install the bootloader and reboot
- install the mellanox way via BFB (this is not available, yet)

Installing the _classical_ way (on the live booted smartnic):
!! WARNING !! This is going to remove all boot loader entries and format the mmcblk device !! 
```
cd /opt/persist
# modify install.part and install.fstab if needed
./install.sh # and follow the instructions (provide the "disk" - /dev/mmcblk0, confirm twice, provide when asked for a root password and done, safe to reboot at the end)
```

### FAQ and known issues
Errors regarding eswitch and mlx5_core are normal if HIDE_PORT2_PF firmware config is set to true.

### Bluefield drivers
According to Nvidia, these are the drivers needed to run a Bluefield smartnic card.

| Driver           | Description | GL Kernel | Kernel config         | GL Package          | BF2 | BF3 | Comment                                                               |
|------------------|-------------|-----------|-----------------------|---------------------|-----|-----|-----------------------------------------------------------------------|
| bluefield-edac   |             | m         | EDAC_BLUEFIELD        |                     |     |     |                                                                       |
| dw_mmc_bluefield |             | m         | MMC_DW_BLUEFIELD      |                     |     |     |                                                                       |
| sdhci-of-dwcmshc |             | m         | MMC_SDHCI_OF_DWCMSHC  |                     |     |     |                                                                       |
| gpio-mlxbf2      |             | m         | GPIO_MLXBF2           |                     |     |     |                                                                       |
| gpio-mlxbf3      |             | m         | GPIO_MLXBF3           |                     |     |     |                                                                       |
| i2c-mlx          |             | m         | I2C_MLXBF             |                     |     |     |                                                                       |
| ipmb-dev-int     |             | m         | IPMB_DEVICE_INTERFACE |                     |     |     |                                                                       |
| ipmb-host        |             |           |                       |                     |     |     | Nothing provided yet as we don't really need this for our BF2 usecase | 
| mlxbf-gige       |             | m         | MLXBF_GIGE            |                     |     |     |                                                                       |
| mlxbf-livefish   |             |           |                       | hack/mlxbf-livefish |     |     |                                                                       |
| mlxbf-pka        |             |           |                       | hack/mlxbf-pka      |     |     |                                                                       | 
| mlxbf-pmc        |             | m         | MLXBF_PMC             |                     |     |     |                                                                       |
| mlxbf-ptm        |             |           |                       | hack/mlxbf-ptm      |     |     |                                                                       |
| mlxbf-tmfifo     |             | m         | MLXBF_TMFIFO          |                     |     |     |                                                                       |
| mlx-bootctl      |             | m         | MLXBF_BOOTCTL         |                     |     |     |                                                                       |
| mlx-trio         |             |           |                       | hack/mlx-trio       |     |     |                                                                       |
| pwr-mlxbf        |             |           |                       | hack/pwr-mlxbf      |     |     |                                                                       |

The drivers marked with an _m_ in the _GL Kernel_ are drivers we are now enabling by default, as modules, in the GardenLinux kernel.
For the rest of the drivers, we are providing scripts that would help the user build debian packages that are going to provide
the rest of the needed kernel modules. These cannot be provided as debian packages via our GardenLinux repositories because of licensing issues.
