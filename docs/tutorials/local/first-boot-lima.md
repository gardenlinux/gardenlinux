---
title: "First Boot on Lima"
description: "Step-by-step guide to deploying Garden Linux on Lima"
category: "tutorials"
tags: ["tutorial", "lima", "virtualization", "beginner"]
migration_status: "done"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4595"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/tutorials/local/first-boot-lima.md
github_target_path: "docs/tutorials/local/first-boot-lima.md"
---

# First Boot on Lima

Garden Linux is a minimal, security-hardened Linux distribution designed for cloud and container environments. [Lima (Linux Machines)](https://lima-vm.io) is a virtual machine lifecycle management tool that makes it straightforward to run virtual machines on your local workstation. Lima takes care of configuration details such as creating a user, setting up SSH access, and mounting directories into the VM.

This tutorial guides you through deploying your first Garden Linux instance using Lima, from launching the VM to verifying the installation.

**Difficulty:** Beginner | **Time:** ~5 minutes

**Learning Objective:** By the end of this tutorial, you'll have a running Garden Linux virtual machine under Lima and understand the basic deployment workflow.

## Prerequisites

Before starting, you'll need:

- A macOS or Linux host with virtualization support
- [Lima](https://lima-vm.io/) installed
- [Podman](https://podman.io/) installed (for generating the Lima YAML manifest)

:::tip
Install Lima and Podman on Debian/Ubuntu-based systems:

```bash
# Install Lima
sudo apt install lima

# Install Podman
sudo apt install podman
```

On macOS, use [Homebrew](https://brew.sh/):

```bash
brew install lima podman
```

:::

## What You'll Build

You'll launch a Garden Linux virtual machine using Lima with a single command, open a shell into the VM, and verify the installation. Lima handles all QEMU configuration, SSH setup, and user provisioning automatically — no manual configuration scripts are needed.

## Steps

### Step 1: Create and Start the VM

#### Pre-built Images (Recommended)

Garden Linux provides pre-built images suitable for use with Lima. A containerized YAML generator (`ghcr.io/gardenlinux/gardenlinux/lima:latest`) produces the correct Lima manifest automatically, so you don't need to construct image URLs manually.

The pre-built images are intentionally minimal and do not include much of the additional software available in Garden Linux. You can use `apt` to search and install additional packages that are available for Garden Linux.

```bash
# For a release version:
GL_VERSION="2150.0.0"
podman run --rm ghcr.io/gardenlinux/gardenlinux/lima:latest --version "${GL_VERSION}" | limactl start --name gardenlinux -

# For the latest nightly build:
podman run --rm ghcr.io/gardenlinux/gardenlinux/lima:latest | limactl start --name gardenlinux -

# For a specific nightly build:
GL_VERSION="2198.0.0"
podman run --rm ghcr.io/gardenlinux/gardenlinux/lima:latest --version "${GL_VERSION}" --allow-nightly | limactl start --name gardenlinux -

```

:::tip
The container generates a Lima YAML manifest with the correct image URL and all required configuration. You can redirect the output to a file for review or modification:

```bash
podman run --rm ghcr.io/gardenlinux/gardenlinux/lima:latest > gardenlinux-manifest.yaml
cat gardenlinux-manifest.yaml | limactl start --name gardenlinux -
```

:::

:::tip
For a complete list of maintained releases and their support lifecycle, see the [releases reference](../../reference/releases/index.md).
:::

#### Build Your Own Images

You can [Build your own Garden Linux Images](/how-to/building-images) or even [Create a custom Feature](/how-to/custom-feature).

### Step 2: Connect to Your Instance

Once the VM has started, open a shell:

```bash
limactl shell gardenlinux
```

Lima automatically provisions a user with sudo access and configures SSH for you. No manual SSH key setup or firmware configuration scripts are needed.

### Step 3: Verify the Installation

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

- Your Garden Linux virtual machine is running under Lima
- You can open a shell via `limactl shell gardenlinux`
- You can verify the Garden Linux version using `cat /etc/os-release`

## Cleanup

When you're finished with the tutorial, stop and remove the VM:

```bash
limactl stop gardenlinux
limactl delete gardenlinux
```

## Next Steps

Now that you have a running Garden Linux instance on Lima, you can:

- Explore [Lima platform-specific features and configurations](../../how-to/installation/local/lima.md)
- Browse [sample Lima manifests](https://github.com/gardenlinux/gardenlinux/tree/main/features/lima/samples) for provisioning scripts (rootless Podman, containerd)
