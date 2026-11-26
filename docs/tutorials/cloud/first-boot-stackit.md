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
- [STACKIT CLI](https://github.com/stackitcloud/stackit-cli) installed — see [installation instructions](https://github.com/stackitcloud/stackit-cli/blob/main/INSTALLATION.md)
- STACKIT credentials configured — see [STACKIT CLI authentication](https://github.com/stackitcloud/stackit-cli/blob/main/AUTHENTICATION.md)
- Basic familiarity with STACKIT concepts:
  - [Getting Started](https://docs.stackit.cloud/platform/getting-started/) — projects, accounts, portal
  - [Products](https://docs.stackit.cloud/products/) — compute, networking, storage
  - [Linux Server](https://docs.stackit.cloud/products/compute-engine/linux-server/) — compute engine for Linux workloads
  - [STACKIT CLI Command Reference](https://github.com/stackitcloud/stackit-cli/tree/main/docs)
  - [Marketplace](https://docs.stackit.cloud/marketplace/) — available services
- An SSH client on your local machine

## What you'll build

You'll upload a Garden Linux image to STACKIT, deploy a server with a basic networking setup (network, security group, and public IP), configure SSH access, and verify the installation. The tutorial uses the `stackit-gardener_prod` [flavor](/explanation/flavors), which is optimized for production workloads on STACKIT.

## Steps

### Step 1: Set Your Project ID

All STACKIT CLI commands require a project ID. Set it once as an environment variable:

```bash
export STACKIT_PROJECT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # replace with your project ID
```

### Step 2: Upload a Garden Linux Image

Garden Linux provides pre-built images for STACKIT. Download and upload the image to your STACKIT project.

:::tip
For a complete overview of all image acquisition methods across platforms, see [Getting Images](/how-to/getting-images).
:::

:::info No pre-built STACKIT images yet
Pre-built STACKIT images are not yet published in the GitHub Releases "Published Images" section. Until they are available, use the **[Build Your Own Images](#build-your-own-images)** section below to build a local image first.
:::

In the "Published Images" section on the release page, find the image for your desired [flavor](/explanation/flavors) and [architecture](/reference/glossary#architecture). The default production flavor is `stackit-gardener_prod-amd64`. You can directly download it there.

To download and upload by script, find the `.tar.xz` archive in the "Assets" section, extract the `.raw` image, and upload it via the STACKIT CLI:

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

# Upload to STACKIT
IMAGE_ID=$(stackit image create \
  --project-id "${STACKIT_PROJECT_ID}" \
  --name gardenlinux-tutorial \
  --disk-format raw \
  --local-file-path "${GL_RAW}" \
  --output-format json | jq -r '.id')
echo "Uploaded image: ${IMAGE_ID}"
```

Expected output:

```text
Uploaded image: bbd1cc8f-29ca-47e6-ac01-628e1dddd0d6
```

:::tip
Set `GL_ARCH` to `arm64` to use the ARM variant instead.
:::

:::tip
For a complete list of maintained releases and their support lifecycle, see the [releases reference](/reference/releases/).
:::

#### Build your own images

You can [build your own Garden Linux images](/how-to/building-images) or even [create a custom feature](/how-to/custom-feature).

### Step 3: Get a Network ID

Get the ID of an existing network in your STACKIT project:

```bash
# List available networks and pick one
stackit network list \
  --project-id "${STACKIT_PROJECT_ID}" \
  --output-format json | \
  jq -r '.[] | "\(.id) \(.name)"'

NETWORK_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # replace with your network ID
echo "Network ID: ${NETWORK_ID}"
```

:::info Network creation not yet supported for VPC-enabled projects
As of CLI v0.77.2, `stackit network create` does not support VPC-enabled projects. New STACKIT projects are VPC-enabled by default, so reusing an existing network is currently the recommended approach.

Check with your STACKIT administrator if unsure which network to use.
:::

### Step 4: Create a Security Group

Create a security group that allows inbound SSH access from your current public IP:

```bash
SG_NAME="gardenlinux-sg"
MY_IP=$(curl -s -4 ifconfig.me)

stackit security-group create \
  --project-id "${STACKIT_PROJECT_ID}" \
  --name "${SG_NAME}"

SG_ID=$(stackit security-group list \
  --project-id "${STACKIT_PROJECT_ID}" \
  --output-format json | \
  jq -r ".[] | select(.name==\"${SG_NAME}\") | .id")

stackit security-group rule create \
  --project-id "${STACKIT_PROJECT_ID}" \
  --security-group-id "${SG_ID}" \
  --direction ingress \
  --protocol-name tcp \
  --port-range-min 22 \
  --port-range-max 22 \
  --ip-range "${MY_IP}/32"
```

### Step 5: Configure SSH Access

Generate an SSH key pair, register it with STACKIT, and prepare a cloud-init script to enable SSH on first boot:

:::warning Garden Linux SSH Default
Garden Linux disables SSH by default for security. You must explicitly enable it using cloud-init user-data when launching the server.
:::

```bash
KEY_NAME="gardenlinux-tutorial-key"
ssh-keygen -t ed25519 -f "${KEY_NAME}" -N ""

stackit key-pair create \
  --project-id "${STACKIT_PROJECT_ID}" \
  --name "${KEY_NAME}" \
  --public-key "@${KEY_NAME}.pub"

USER_DATA=user_data.sh
cat >"${USER_DATA}" <<'EOF'
#!/usr/bin/env bash
systemctl enable --now ssh
EOF
```

### Step 6: Launch the Server

Launch your Garden Linux server on STACKIT:

```bash
SERVER_NAME="gardenlinux-tutorial"
MACHINE_TYPE="g2i.2"   # adjust to an available type — see https://docs.stackit.cloud/products/compute-engine/server/basics/machine-types/

SERVER_ID=$(stackit server create \
  --project-id "${STACKIT_PROJECT_ID}" \
  --name "${SERVER_NAME}" \
  --machine-type "${MACHINE_TYPE}" \
  --boot-volume-source-id "${IMAGE_ID}" \
  --boot-volume-source-type image \
  --boot-volume-size 20 \
  --network-id "${NETWORK_ID}" \
  --security-groups "${SG_ID}" \
  --keypair-name "${KEY_NAME}" \
  --user-data "@${USER_DATA}" \
  --output-format json | jq -r '.id')
echo "Server ID: ${SERVER_ID}"
```

Expected output:

```text
Server ID: 43517fee-1234-5678-abcd-ef0123456789
```

### Step 7: Assign a Public IP

Allocate a public IP and associate it with your server's network interface:

```bash
# Get the network interface ID of the server
NIC_ID=$(stackit server list \
  --project-id "${STACKIT_PROJECT_ID}" \
  --output-format json | \
  jq -r ".[] | select(.id==\"${SERVER_ID}\") | .nics[0].nicId")

# Create and associate a public IP
PUBLIC_IP_ID=$(stackit public-ip create \
  --project-id "${STACKIT_PROJECT_ID}" \
  --associated-resource-id "${NIC_ID}" \
  --output-format json | jq -r '.id')

PUBLIC_IP=$(stackit public-ip list \
  --project-id "${STACKIT_PROJECT_ID}" \
  --output-format json | \
  jq -r ".[] | select(.id==\"${PUBLIC_IP_ID}\") | .ip")

echo "Server is reachable at: ${PUBLIC_IP}"
```

Expected output:

```text
Server is reachable at: 185.214.186.2
```

### Step 8: Connect to Your Instance

Wait for the server to complete its startup script (typically 3–5 minutes), then connect via SSH:

```bash
ssh -i "${KEY_NAME}" admin@"${PUBLIC_IP}"
```

:::tip
Garden Linux uses `admin` as the default SSH username on STACKIT, as configured by cloud-init. The `admin` user has passwordless `sudo` access via the `sudo` group.
:::

### Step 9: Verify the Installation

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

```text
ID=gardenlinux
NAME="Garden Linux"
VERSION="2150.0.0"
GARDENLINUX_PLATFORM_VARIANT=stackit
```

Expected output from `chronyc tracking` should show the KVM PTP clock as reference:

```text
Reference ID    : 50484330 (PHC0)
Stratum         : 1
...
System time     : 0.000000123 seconds fast of NTP time
```

`PHC0` (PTP Hardware Clock) confirms Garden Linux is using the KVM PTP clock for time synchronization on STACKIT.

## Success Criteria

This tutorial is complete when:

- Your Garden Linux server is running on STACKIT
- You can connect via SSH
- `cat /etc/os-release` shows `GARDENLINUX_PLATFORM_VARIANT=stackit`

## Cleanup Resources

When finished, remove all created resources:

```bash
# Disassociate and delete public IP
stackit public-ip disassociate "${PUBLIC_IP_ID}" \
  --project-id "${STACKIT_PROJECT_ID}"

stackit public-ip delete "${PUBLIC_IP_ID}" \
  --project-id "${STACKIT_PROJECT_ID}"

# Delete the server
stackit server delete "${SERVER_ID}" \
  --project-id "${STACKIT_PROJECT_ID}"

# Delete the security group
stackit security-group delete "${SG_ID}" \
  --project-id "${STACKIT_PROJECT_ID}"

# Delete the key pair
stackit key-pair delete "${KEY_NAME}" \
  --project-id "${STACKIT_PROJECT_ID}"

# Delete the image
stackit image delete "${IMAGE_ID}" \
  --project-id "${STACKIT_PROJECT_ID}"

# Remove local files
rm "${USER_DATA}" "${KEY_NAME}" "${KEY_NAME}.pub" "${GL_RAW}" "${GL_TAR_XZ}"
```

## Related topics

<RelatedTopics />
