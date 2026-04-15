---
First Boot on Lima](./local/first-boot-lima.md)itle: "First Boot on KVM"
description: "Step-by-step guide to deploying Garden Linux on QEMU/KVM"
category: "tutorials"
tags: ["tutorial", "kvm", "qemu", "virtualization", "beginner"]
migration_status: "done"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4595"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/tutorials/local/first-boot-kvm.md
github_target_path: "docs/tutorials/local/first-boot-kvm.md"
---

# First Boot on KVM

Garden Linux is a minimal, security-hardened Linux distribution designed for cloud and container environments. This tutorial guides you through deploying your first Garden Linux instance using [QEMU](https://www.qemu.org/) with [KVM](https://www.linux-kvm.org/) acceleration, from downloading a disk image to connecting via SSH.

**Difficulty:** Beginner | **Time:** ~10 minutes

**Learning Objective:** By the end of this tutorial, you'll have a running Garden Linux virtual machine and understand the basic deployment process using plain QEMU commands.

## Prerequisites

Before starting, you'll need:

- A Linux host with KVM support (`/dev/kvm` must exist and be accessible)
- [QEMU](https://www.qemu.org/download/) installed (`qemu-system-x86_64` for amd64, `qemu-system-aarch64` for arm64)
- [OVMF](https://github.com/tianocore/tianocore.github.io/wiki/How-to-run-OVMF) firmware installed (UEFI boot support)
- An SSH client on your local machine
- `sudo` or appropriate permissions to access `/dev/kvm`

:::tip
Install QEMU and OVMF on Debian/Ubuntu-based systems:

```bash
# For amd64 hosts
sudo apt install qemu-system-x86 ovmf

# For arm64 hosts
sudo apt install qemu-system-arm qemu-efi-aarch64
```

:::

## What You'll Build

You'll launch a Garden Linux virtual machine using plain QEMU commands with environment variables for configuration. The tutorial covers downloading a disk image for your architecture (amd64 or arm64), creating a configuration script for first-boot setup (including SSH access), and verifying the installation.

## Steps

### Step 1: Choose an Image

Garden Linux provides pre-built disk images for KVM. Start by selecting an appropriate image for your deployment.

#### Official Images

Choose a release from the [GitHub Releases page](https://github.com/gardenlinux/gardenlinux/releases). For this tutorial, we'll use [release 2150.0.0](https://github.com/gardenlinux/gardenlinux/releases/tag/2150.0.0).

In the **Assets** section at the bottom of the release page, find the `kvm-gardener_prod` archive matching your workstation architecture. Garden Linux provides images for both `amd64` and `arm64`. You will also need the `commit` of the build to download the correct image.

Either download and extract the image by hand or use this script to detect your workstation architecture and download the correct image:

```bash
GL_VERSION="2150.0.0"
GL_COMMIT="eb8696b9"

# Auto-detect host architecture
GL_ARCH="$(uname -m)"
case "$GL_ARCH" in
  x86_64)  GL_ARCH="amd64" ;;
  aarch64) GL_ARCH="arm64" ;;
  *)       echo "Unsupported architecture: $GL_ARCH"; exit 1 ;;
esac

GL_ASSET="kvm-gardener_prod-${GL_ARCH}-${GL_VERSION}-${GL_COMMIT}"
GL_TAR_XZ="${GL_ASSET}.tar.xz"
GL_IMAGE="${GL_ASSET}.raw"

curl -L -o "${GL_TAR_XZ}" \
  "https://github.com/gardenlinux/gardenlinux/releases/download/${GL_VERSION}/${GL_TAR_XZ}"

# Extract raw image
tar -xf "${GL_TAR_XZ}" "${GL_IMAGE}"
# Delete downloaded tar file
rm "${GL_TAR_XZ}"
```

:::tip
To use a specific architecture instead of auto-detecting, set `GL_ARCH` before running the download commands:

```bash
GL_ARCH="arm64"
```

:::

:::tip
For a complete list of maintained releases and their support lifecycle, see the [releases reference](../../reference/releases/index.md).
:::

#### Build Your Own Images

You can [Build your own Garden Linux Images](/how-to/building-images) or even [Create a custom Feature](/how-to/custom-feature).

### Step 2: Verify KVM Support

Ensure your system supports KVM hardware acceleration for optimal performance:

```bash
# Check if /dev/kvm exists and is accessible
if [ -w /dev/kvm ]; then
    echo "KVM acceleration is available"
else
    echo "KVM acceleration is not available or /dev/kvm is not accessible"
    echo "Falling back to TCG emulation (significantly slower)"
fi
```

:::warning
Without KVM acceleration, QEMU will use TCG software emulation, which is substantially slower. Ensure your BIOS/UEFI has virtualization enabled (Intel VT-x or AMD-V) and that your user has access to `/dev/kvm`.
:::

### Step 3: Configure SSH Access

Garden Linux disables SSH by default for security. You must explicitly enable it and create a user on first boot using a firmware configuration script.

```bash
# Generate an SSH key pair
SSH_KEY_DIR="${HOME}/.ssh/gardenlinux-kvm"
mkdir -p "$SSH_KEY_DIR"
ssh-keygen -t ed25519 -f "$SSH_KEY_DIR/id_ed25519" -N ""

# Read the public key
SSH_PUBLIC_KEY=$(cat "$SSH_KEY_DIR/id_ed25519.pub")

# Define the SSH user
SSH_USER="gardenlinux"

# Create the fw_cfg configuration script
FW_CFG_SCRIPT="fw_cfg-script.sh"

# Determine console device based on architecture
GL_ARCH_TMP="${GL_ARCH:-$(uname -m)}"
case "$GL_ARCH_TMP" in
  x86_64|amd64)  CONSOLE="/dev/ttyS0" ;;
  aarch64|arm64) CONSOLE="/dev/ttyAMA0" ;;
  *)             CONSOLE="/dev/ttyS0" ;;
esac

cat >"$FW_CFG_SCRIPT" <<EOF
#!/usr/bin/env bash
set -eufo pipefail

# Send all output to the serial console
exec >${CONSOLE}
exec 2>&1

# Enable SSH service
systemctl enable --now ssh

# Create the user and configure SSH access
useradd -U -m -G wheel -s /bin/bash ${SSH_USER}
mkdir -p /home/${SSH_USER}/.ssh
chmod 700 /home/${SSH_USER}/.ssh
echo "${SSH_PUBLIC_KEY}" >> /home/${SSH_USER}/.ssh/authorized_keys
chown -R ${SSH_USER}:${SSH_USER} /home/${SSH_USER}/.ssh
chmod 600 /home/${SSH_USER}/.ssh/authorized_keys
EOF
```

:::tip
The [`fw_cfg` script mechanism](https://wiki.osdev.org/QEMU_fw_cfg) passes a shell script to the VM via QEMU's firmware configuration interface. Garden Linux executes scripts found at `opt/gardenlinux/config_script` during early boot. The script output is redirected to the serial console (`/dev/ttyS0` on amd64, `/dev/ttyAMA0` on arm64) for debugging.
:::

### Step 4: Launch the VM

Set environment variables and launch the virtual machine. The command adapts automatically based on your host architecture:

```bash
# Configuration variables
GL_ARCH="${GL_ARCH:-$(uname -m)}"
case "$GL_ARCH" in
  x86_64)  GL_ARCH="amd64" ;;
  aarch64) GL_ARCH="arm64" ;;
esac
GL_CPU="${GL_CPU:-2}"
GL_MEM="${GL_MEM:-2048}"
GL_SSH_PORT="${GL_SSH_PORT:-2222}"
GL_IMAGE="${GL_IMAGE:-kvm-gardener_prod-amd64-2150.0.0-eb8696b9.raw}"

if [ "$GL_ARCH" = "amd64" ]; then
  QEMU_BIN="${QEMU_BIN:-qemu-system-x86_64}"
  QEMU_MACHINE="q35"
  QEMU_CPU="${QEMU_CPU:-host}"
  UEFI_CODE="${UEFI_CODE:-/usr/share/OVMF/OVMF_CODE.fd}"
  UEFI_VARS="${UEFI_VARS:-/usr/share/OVMF/OVMF_VARS.fd}"
elif [ "$GL_ARCH" = "arm64" ]; then
  QEMU_BIN="${QEMU_BIN:-qemu-system-aarch64}"
  QEMU_MACHINE="virt"
  QEMU_CPU="${QEMU_CPU:-max}"
  UEFI_CODE="${UEFI_CODE:-/usr/share/AAVMF/AAVMF_CODE.fd}"
  UEFI_VARS="${UEFI_VARS:-/usr/share/AAVMF/AAVMF_VARS.fd}"
fi

# Create a writable copy of UEFI vars
UEFI_VARS_TMP="ovmf-vars.fd"
cp "$UEFI_VARS" "$UEFI_VARS_TMP"

# Launch QEMU
$QEMU_BIN \
    -machine "${QEMU_MACHINE}" \
    -cpu "${QEMU_CPU}" \
    -enable-kvm \
    -smp "${GL_CPU}" \
    -m "${GL_MEM}" \
    -drive if=virtio,format=raw,file="${GL_IMAGE}" \
    -drive if=pflash,format=raw,unit=0,file="${UEFI_CODE}",readonly=on \
    -drive if=pflash,format=raw,unit=1,file="${UEFI_VARS_TMP}" \
    -fw_cfg name=opt/gardenlinux/config_script,file="${FW_CFG_SCRIPT}" \
    -netdev user,id=net0,hostfwd=tcp::${GL_SSH_PORT}-:22 \
    -device virtio-net-pci,netdev=net0 \
    -device virtio-rng-pci \
    -serial mon:stdio \
    -nographic \
    -no-reboot
```

#### Configuration Variables

| Variable       | Default (amd64)                                          | Default (arm64)                                          | Description                                |
| -------------- | -------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------ |
| `GL_IMAGE`     | `kvm-gardener_prod-amd64-${GL_VERSION}-${GL_COMMIT}.raw` | `kvm-gardener_prod-amd64-${GL_VERSION}-${GL_COMMIT}.raw` | Path to the `.raw` disk image              |
| `GL_ARCH`      | `amd64`                                                  | `arm64`                                                  | Architecture (auto-detected)               |
| `GL_CPU`       | `2`                                                      | `2`                                                      | Number of virtual CPUs                     |
| `GL_MEM`       | `2048`                                                   | `2048`                                                   | Memory in MiB                              |
| `GL_SSH_PORT`  | `2222`                                                   | `2222`                                                   | Host port forwarded to guest SSH (port 22) |
| `QEMU_BIN`     | `qemu-system-x86_64`                                     | `qemu-system-aarch64`                                    | QEMU binary to use                         |
| `QEMU_MACHINE` | `q35`                                                    | `virt`                                                   | QEMU machine type                          |
| `QEMU_CPU`     | `host`                                                   | `max`                                                    | QEMU CPU model                             |
| `UEFI_CODE`    | `/usr/share/OVMF/OVMF_CODE.fd`                           | `/usr/share/AAVMF/AAVMF_CODE.fd`                         | Path to UEFI firmware code                 |
| `UEFI_VARS`    | `/usr/share/OVMF/OVMF_VARS.fd`                           | `/usr/share/AAVMF/AAVMF_VARS.fd`                         | Path to UEFI firmware variables            |

### Step 5: Connect to Your Instance

Wait for the VM to boot and the configuration script to complete (typically 30-60 seconds). Then connect via SSH using the forwarded port:

```bash
ssh -i "${SSH_KEY_DIR}/id_ed25519" -p "${GL_SSH_PORT}" "${SSH_USER}"@localhost
```

:::tip
Garden Linux uses `gardenlinux` as the default SSH username for local and KVM deployments. This differs from cloud platforms like AWS, which use `ec2-user`.
:::

### Step 6: Verify the Installation

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

- Your Garden Linux virtual machine is running
- You can connect via SSH on the forwarded port
- You can verify the Garden Linux version using `cat /etc/os-release`

## Cleanup

When you're finished with the tutorial, clean up the resources:

```bash
# Stop the VM by pressing Ctrl+A, then X in the QEMU console
# or send the poweroff command from within the VM

# Remove temporary files
rm -f "$FW_CFG_SCRIPT" "$UEFI_VARS_TMP" "$GL_IMAGE"
rm -rf "$SSH_KEY_DIR"
```

## Next Steps

Now that you have a running Garden Linux instance on KVM, you can:

- Explore [KVM platform-specific features and configurations](../../how-to/installation/local/kvm.md)
