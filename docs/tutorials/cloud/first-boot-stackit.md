---
title: "First Boot on STACKIT"
description: "Step-by-step guide to deploying Garden Linux on STACKIT"
category: "tutorials"
tags: ["tutorial", "stackit", "cloud", "beginner"]
related_topics:
  - /how-to/installation/cloud/stackit.md
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/tutorials/cloud/first-boot-stackit.md
github_target_path: "docs/tutorials/cloud/first-boot-stackit.md"
---

# First Boot on STACKIT

Garden Linux is a minimal, security-hardened Linux distribution designed for cloud and container environments. This tutorial guides you through deploying your first Garden Linux instance on [STACKIT](https://www.stackit.de/), from uploading an image to connecting via SSH.

**Difficulty:** Beginner | **Time:** ~15 minutes

**Learning Objective:** By the end of this tutorial, you'll have a running Garden Linux instance on STACKIT and understand the basic deployment process.

## Prerequisites

Before starting, you'll need:

- A [STACKIT account](https://portal.stackit.cloud/) with a project and appropriate permissions to create servers, networks, and security groups
- [STACKIT CLI](https://github.com/stackitcloud/stackit-cli) installed (`brew install stackitcloud/tap/stackit` or from the [releases page](https://github.com/stackitcloud/stackit-cli/releases))
- [OpenStack CLI](https://docs.openstack.org/python-openstackclient/latest/) installed (`python-openstackclient`) — STACKIT exposes a standard OpenStack API
- STACKIT credentials configured — see [STACKIT CLI authentication](https://github.com/stackitcloud/stackit-cli/blob/main/AUTHENTICATION.md)
- An SSH client on your local machine

## What you'll build

You'll upload a Garden Linux image to STACKIT, deploy a server with a basic networking setup (network, subnet, security group, and floating IP), configure SSH access, and verify the installation. The tutorial uses the `stackit-gardener_prod` [flavor](/explanation/flavors), which is optimized for production workloads on STACKIT.

## Steps

### Step 1: Choose an Image

Garden Linux provides pre-built images for STACKIT. Start by downloading the image and uploading it to your STACKIT project.

:::tip
For a complete overview of all image acquisition methods across platforms, see [Getting Images](/how-to/getting-images).
:::

#### Official Images

Choose a release from the [GitHub Releases page](https://github.com/gardenlinux/gardenlinux/releases). For this tutorial, we'll use [release 2150.0.0](https://github.com/gardenlinux/gardenlinux/releases/tag/2150.0.0).

In the "Published Images" section on the release page, find the image for your desired [flavor](/explanation/flavors) and [architecture](/reference/glossary#architecture). The default production flavor is `stackit-gardener_prod-amd64`. You can directly download it there.

To download it by script, find the `.tar.xz` archive in the "Assets" section and extract the `.raw` image, then upload it to STACKIT via the OpenStack Glance API:

```bash
GL_VERSION="2150.0.0"
GL_COMMIT="eb8696b9"
GL_ARCH="amd64"
GL_ASSET="stackit-gardener_prod-${GL_ARCH}-${GL_VERSION}-${GL_COMMIT}"
GL_RAW="${GL_ASSET}.raw"
GL_TAR_XZ="${GL_ASSET}.tar.xz"

# Download and extract the image
curl -L -o "${GL_TAR_XZ}" \
  "https://github.com/gardenlinux/gardenlinux/releases/download/${GL_VERSION}/${GL_TAR_XZ}"

tar -xf "${GL_TAR_XZ}" "${GL_RAW}"

# Upload to STACKIT image service (OpenStack Glance)
export OS_CLOUD=stackit   # adjust to your clouds.yaml entry
IMAGE_ID=$(openstack image create gardenlinux-tutorial \
    --disk-format raw \
    --container-format bare \
    --file "${GL_RAW}" \
    -f value -c id)
echo "Uploaded image: ${IMAGE_ID}"
```

:::tip
Set `GL_ARCH` to `arm64` to use the ARM variant instead.
:::

:::tip
For a complete list of maintained releases and their support lifecycle, see the [releases reference](/reference/releases/).
:::

#### Build your own images

You can [build your own Garden Linux images](/how-to/building-images) or even [create a custom feature](/how-to/custom-feature).

### Step 2: Prepare Your Network

Before launching a server, set up the necessary networking infrastructure.

:::tip
If you already have a STACKIT network and subnet you'd like to reuse, you can skip directly to creating the security group.
:::

```bash
STACKIT_PROJECT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # replace with your project ID
NETWORK_NAME="gardenlinux-network"

# Create a network
stackit beta network create \
  --project-id "${STACKIT_PROJECT_ID}" \
  --name "${NETWORK_NAME}"

NETWORK_ID=$(stackit beta network list \
  --project-id "${STACKIT_PROJECT_ID}" \
  --output-format json | \
  jq -r ".[] | select(.name==\"${NETWORK_NAME}\") | .id")
```

### Step 3: Create a Security Group

Create a security group that allows SSH access from your current public IP:

```bash
SG_NAME="gardenlinux-sg"
MY_IP=$(curl -s ifconfig.me)

openstack security group create "${SG_NAME}"

openstack security group rule create "${SG_NAME}" \
  --protocol tcp \
  --dst-port 22 \
  --remote-ip "${MY_IP}/32"
```

### Step 4: Configure SSH Access

Generate an SSH key pair and register it with STACKIT:

:::warning Garden Linux SSH Default
Garden Linux disables SSH by default for security. You must explicitly enable it using cloud-init user-data when launching the server.
:::

```bash
KEY_NAME="gardenlinux-tutorial-key"
ssh-keygen -t ed25519 -f "${KEY_NAME}" -N ""

stackit beta key-pair create \
  --project-id "${STACKIT_PROJECT_ID}" \
  --name "${KEY_NAME}" \
  --public-key "$(cat ${KEY_NAME}.pub)"

USER_DATA=user_data.sh
cat >"${USER_DATA}" <<EOF
#!/usr/bin/env bash

# Enable SSH service on first boot
systemctl enable --now ssh
EOF
```

### Step 5: Launch the Server

Launch your Garden Linux server on STACKIT:

```bash
SERVER_NAME="gardenlinux-tutorial"
MACHINE_TYPE="c1.2"   # adjust to an available type in your project

stackit beta server create \
  --project-id "${STACKIT_PROJECT_ID}" \
  --name "${SERVER_NAME}" \
  --machine-type "${MACHINE_TYPE}" \
  --image-id "${IMAGE_ID}" \
  --network-id "${NETWORK_ID}" \
  --keypair-name "${KEY_NAME}" \
  --user-data "@${USER_DATA}"

SERVER_ID=$(stackit beta server list \
  --project-id "${STACKIT_PROJECT_ID}" \
  --output-format json | \
  jq -r ".[] | select(.name==\"${SERVER_NAME}\") | .id")
```

### Step 6: Assign a Public IP

Allocate a floating IP and associate it with your server:

```bash
FLOATING_IP=$(openstack floating ip create public \
  -f value -c floating_ip_address)

openstack server add floating ip "${SERVER_NAME}" "${FLOATING_IP}"

echo "Server is reachable at: ${FLOATING_IP}"
```

### Step 7: Connect to Your Instance

Wait a few moments for the server to complete its startup script, then connect via SSH:

```bash
ssh -i "${KEY_NAME}" admin@"${FLOATING_IP}"
```

:::tip
Garden Linux uses `admin` as the default SSH username on STACKIT, as configured by cloud-init.
:::

### Step 8: Verify the Installation

Once connected, verify your Garden Linux installation:

```bash
# Check OS information
cat /etc/os-release

# Verify kernel version
uname -a

# Check system status
systemctl status

# Check time synchronization (chrony backed by KVM PTP clock)
chronyc tracking
```

Expected output from `/etc/os-release` should include:

```
ID=gardenlinux
NAME="Garden Linux"
VERSION="2150.0.0"
GARDENLINUX_PLATFORM_VARIANT=stackit
```

## Success Criteria

This tutorial is complete when:

- Your Garden Linux server is running on STACKIT
- You can connect via SSH
- `cat /etc/os-release` shows `GARDENLINUX_PLATFORM_VARIANT=stackit`

## Cleanup Resources

When finished, remove all created resources:

```bash
# Remove floating IP from server
openstack server remove floating ip "${SERVER_NAME}" "${FLOATING_IP}"

# Delete the server
stackit beta server delete \
  --project-id "${STACKIT_PROJECT_ID}" \
  --server-id "${SERVER_ID}"

# Delete the floating IP
openstack floating ip delete "${FLOATING_IP}"

# Delete the security group
openstack security group delete "${SG_NAME}"

# Delete the keypair
stackit beta key-pair delete \
  --project-id "${STACKIT_PROJECT_ID}" \
  --name "${KEY_NAME}"

# Delete the image
openstack image delete gardenlinux-tutorial

# Delete the network
stackit beta network delete \
  --project-id "${STACKIT_PROJECT_ID}" \
  --network-id "${NETWORK_ID}"

# Remove local files
rm "${USER_DATA}" "${KEY_NAME}" "${KEY_NAME}.pub" "${GL_RAW}" "${GL_TAR_XZ}"
```

## Related topics

<RelatedTopics />
