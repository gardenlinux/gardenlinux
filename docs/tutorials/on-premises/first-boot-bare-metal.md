---
title: "First Boot on Bare Metal"
description: "Step-by-step guide to deploying Garden Linux on bare metal servers using dd"
category: "tutorials"
tags: ["tutorial", "bare-metal", "on-premises", "beginner"]
migration_status: "done"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4595"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/tutorials/on-premises/first-boot-bare-metal.md
github_target_path: "docs/tutorials/on-premises/first-boot-bare-metal.md"
---

# First Boot on Bare Metal

Garden Linux is a minimal, security-hardened Linux distribution designed for cloud and container environments. This tutorial guides you through deploying Garden Linux on a bare metal server by writing a disk image directly to the target drive using `dd`.

:::tip No ISO Installer
Garden Linux does not currently provide an ISO installer image for bare-metal deployment. Instead, pre-built `.raw` disk images are written directly to the target disk using the `dd` command from a live system.
:::

**Difficulty:** Beginner | **Time:** ~20 minutes

**Learning Objective:** By the end of this tutorial, you'll have Garden Linux running on a bare metal server and understand the basic deployment process.

## Prerequisites

Before starting, you'll need:

- A bare metal server with UEFI or legacy BIOS firmware
- A booted live system on the target machine (to run `dd`)
- Network connectivity from the live system (to download the image)
- Physical or remote console access (for initial setup)
- An SSH client on another machine

:::tip Live System Options
Recommended live systems include:

- [Debian netboot](https://www.debian.org/distro/netinst) — minimal, includes `dd` and networking

Both include the required tools and network support.
:::

## What You'll Build

You'll write a Garden Linux `.raw` disk image to your server's boot drive using `dd` from a live system, configure SSH access for remote administration, and boot into the installed system. The tutorial uses the `baremetal-gardener_prod` [flavor](../../explanation/flavors-and-features.md), which includes the standard kernel and physical hardware support required for bare metal deployment.

## Steps

### Step 1: Choose an Image

Garden Linux provides pre-built disk images for bare metal deployment. Start by selecting an appropriate image for your server.

#### Official Images

Choose a release from the [GitHub Releases page](https://github.com/gardenlinux/gardenlinux/releases). For this tutorial, we'll use [release 2150.0.0](https://github.com/gardenlinux/gardenlinux/releases/tag/2150.0.0).

In the **Assets** section at the bottom of the release page, find the `baremetal-gardener_prod-amd64` archive. Download and extract the `.raw` disk image:

```bash
GL_VERSION="2150.0.0"
GL_COMMIT="eb8696b9"
GL_ASSET="baremetal-gardener_prod-amd64-${GL_VERSION}-${GL_COMMIT}"
GL_RAW="${GL_ASSET}.raw"
GL_TAR_XZ="${GL_ASSET}.tar.xz"

# Download the image archive
curl -L -o "${GL_TAR_XZ}" \
  "https://github.com/gardenlinux/gardenlinux/releases/download/${GL_VERSION}/${GL_TAR_XZ}"

# Extract the raw disk image
tar -xf "${GL_TAR_XZ}" "${GL_RAW}"
```

:::tip
For a complete list of maintained releases and their support lifecycle, see the [releases reference](../../reference/releases/index.md).
:::

#### Build Your Own Images

You can [Build your own Garden Linux Images](/how-to/building-images) or even [Create a custom Feature](/how-to/custom-feature).

### Step 2: Boot the Live System

Boot your target server using a live system (Debian netboot, SystemRescue, or similar) that includes:

- The `dd` command
- Network connectivity (DHCP or static IP configuration)
- Access to download or transfer the Garden Linux image

:::tip Network Configuration
If your live system doesn't have DHCP, configure a static IP:

```bash
ip addr add 192.168.1.100/24 dev eth0
ip route add default via 192.168.1.1
echo "nameserver 9.9.9.9" > /etc/resolv.conf
```

:::

Ensure the live system can reach the internet or has the image available locally.

### Step 3: Write the Image to Disk

Download the image to the live system (if not already available), then write it directly to the target disk.

```bash
# Identify the target disk
lsblk -dp
```

:::warning Destructive Operation
The following command will erase ALL data on the target disk. Ensure you have selected the correct disk device.
:::

```bash
# Replace /dev/sda with your target disk device
TARGET_DISK="/dev/sda"
dd if=${GL_RAW} of=${TARGET_DISK} bs=4M status=progress
sync
```

Garden Linux includes a partition layout that auto-grows on first boot and supports both UEFI and legacy BIOS boot. No manual partitioning is required.

### Step 4: Configure SSH Access

The `baremetal-gardener_prod` flavor does not include cloud-init, which means there are no pre-configured user accounts. SSH is configured for public-key authentication only, so you must create a user and inject an SSH key before rebooting.

:::warning Garden Linux SSH Default
Garden Linux disables SSH by default for security. You must create a user and inject an SSH public key before accessing the system remotely.
:::

:::tip Generating SSH Keys
On your local machine, generate an SSH key pair:

```bash
KEY_NAME="gardenlinux-tutorial-key"
ssh-keygen -t ed25519 -f ${KEY_NAME} -N ""
```

Copy the contents of `gardenlinux-tutorial-key.pub` to use in the commands below.
:::

Mount the root partition and configure a user with SSH access:

```bash
# Re-read the partition table after writing
partprobe ${TARGET_DISK}

# Mount the root partition (partition 3 on gardener builds; labelled "ROOT")
ROOT_PART="${TARGET_DISK}3"
mount ${ROOT_PART} /mnt

# Mount the usr partition read-only (partition 1 on gardener builds)
USR_PART="${TARGET_DISK}1"
mount -o ro ${USR_PART} /mnt/usr

# Create the user with home directory in the chroot environment
SSH_USER="gardenlinux"
chroot /mnt /bin/bash -c "useradd -m -G wheel -s /bin/bash ${SSH_USER}"

# Create .ssh directory and inject your public key
mkdir -p /mnt/home/${SSH_USER}/.ssh

# Replace this with your actual local SSH public key
cat ${KEY_NAME}.pub >>/mnt/home/${SSH_USER}/.ssh/authorized_keys

chmod 700 /mnt/home/${SSH_USER}/.ssh
chmod 600 /mnt/home/${SSH_USER}/.ssh/authorized_keys

# Set ownership (user needs to own the .ssh directory)
chroot /mnt /bin/bash -c "chown -R ${SSH_USER}:${SSH_USER} /home/${SSH_USER}/.ssh"

# Enable SSH service to start on boot
chroot /mnt /bin/bash -c "systemctl enable ssh.service"

# Unmount in reverse order
umount /mnt/usr
umount /mnt
```

### Step 5: Boot into Garden Linux

Remove any live system media (USB stick, PXE boot configuration) and reboot the server:

```bash
reboot
```

On first boot, Garden Linux will:

- Auto-grow partitions to fill the available disk space
- Generate SSH host keys
- Start the SSH service

:::tip UEFI Boot Order
If the server doesn't boot into Garden Linux automatically, you may need to select the disk as the boot device in the UEFI/BIOS boot menu.
:::

### Step 6: Connect to Your Server

Once the server has booted, connect via SSH using the key you injected:

```bash
ssh -i ${KEY_NAME} gardenlinux@${SERVER_IP}
```

:::tip
Garden Linux uses the `wheel` group for passwordless sudo access. Your user has full administrative privileges.
:::

### Step 7: Verify the Installation

Once connected, verify your Garden Linux installation with the following commands:

```bash
# Check OS information
cat /etc/os-release

# Verify kernel version
uname -a

# Check system status
systemctl status

# View network configuration
ip addr show
```

Expected output from `/etc/os-release` should show:

```bash
ID=gardenlinux
NAME="Garden Linux"
VERSION="${GL_VERSION}"
...
```

## Success Criteria

You have successfully completed this tutorial when:

- Garden Linux is running on your bare metal server
- You can connect via SSH
- You can verify the Garden Linux version using `cat /etc/os-release`

## Advanced Provisioning Methods

Beyond the `dd`-based installation shown in this tutorial, Garden Linux supports more advanced bare-metal provisioning workflows:

### PXE Boot with Ignition

For automated fleet provisioning, Garden Linux supports network boot using iPXE with Ignition-based configuration. The `_pxe` flavor generates a compressed root squashfs image and supports first-boot configuration via Ignition. This approach enables:

- Automated disk partitioning and formatting
- User and SSH key injection
- Network configuration
- Custom service deployment

See the [PXE Boot guide](../../how-to/installation/on-premises/pxe-boot.md) and [bare-metal platform-specific configuration](../../how-to/installation/on-premises/bare-metal.md) for details.

### ironcore.dev — NeoNephos Projects

For large-scale bare-metal lifecycle management, consider the [IronCore Project](https://ironcore.dev/) from the [NeoNephos Projects](https://neonephos.org). Ironcore provides Kubernetes-native bare-metal management, including:

- Automated provisioning of Garden Linux and other operating systems
- Integrated BMC/IPMI support
- Hardware inventory and monitoring
- Fleet-wide orchestration

## Next Steps

Now that you have Garden Linux running on bare metal, you can:

- Explore [bare-metal platform-specific features and configurations](../../how-to/installation/on-premises/bare-metal.md)
