---
title: "First Boot on Azure"
description: "Step-by-step guide to deploying Garden Linux on Microsoft Azure"
category: "tutorials"
tags: ["tutorial", "azure", "cloud", "beginner"]
related_topics:
  - /how-to/installation/cloud/azure.md
migration_status: "adapt"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4595"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/tutorials/cloud/first-boot-azure.md
github_target_path: "docs/tutorials/cloud/first-boot-azure.md"
---

# First Boot on Azure

Garden Linux is a minimal, security-hardened Linux distribution designed for cloud and container environments. This tutorial guides you through deploying your first Garden Linux instance on [Azure](https://azure.microsoft.com/) Virtual Machines, from selecting an image to connecting via SSH.

**Difficulty:** Beginner | **Time:** ~15 minutes

**Learning Objective:** By the end of this tutorial, you'll have a running Garden Linux instance on Azure and understand the basic deployment process.

## Prerequisites

Before starting, you'll need:

- An Azure account with appropriate permissions to create resources
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed and authenticated with `az login`
- Basic familiarity with Azure concepts
- An SSH client on your local machine

## What You'll Build

You'll deploy a Garden Linux instance on Azure with a basic networking setup (resource group, virtual network, subnet, and network security group), configure SSH access, and verify the installation. The tutorial uses the `azure-gardener_prod` [flavor](../../explanation/flavors-and-features.md), which is optimized for gardener production workloads on Azure.

## Steps

### Step 1: Choose an Image

Garden Linux provides pre-built images for Azure via an Azure Community Gallery. Start by selecting an appropriate image for your deployment.

#### Official Images

Choose a release from the [GitHub Releases page](https://github.com/gardenlinux/gardenlinux/releases). For this tutorial, we'll use [release 2150.0.0](https://github.com/gardenlinux/gardenlinux/releases/tag/2150.0.0).

In the "Published Images" section on the release page, find the Community Gallery image ID for your desired [flavor](../../explanation/flavors-and-features.md), [architecture](../../reference/glossary.md), and Azure region. The default production flavor is `azure-gardener_prod-amd64`.

The Azure Community Gallery image ID follows this format:

```bash
GL_VERSION="2150.0.0"
GL_AZ_PROJECT="gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620"
IMAGE_URN="/CommunityGalleries/${GL_AZ_PROJECT}/Images/gardenlinux-nvme-gardener_prod-amd64/Versions/${GL_VERSION}"
```

:::tip
For a complete list of maintained releases and their support lifecycle, see the [releases reference](../../reference/releases/index.md).
:::

#### Build Your Own Images

You can [Build your own Garden Linux Images](/how-to/building-images) or even [Create a custom Feature](/how-to/custom-feature).

### Step 2: Prepare Your Azure Environment

Before launching your Garden Linux instance, set up the necessary Azure infrastructure. This step creates a resource group, virtual network, subnet, and security group.

#### Create a Resource Group

Create a Resource Group to bundle your resources together:

```bash
AZURE_LOCATION="westeurope"
RESOURCE_GROUP="gardenlinux-tutorial"
```

```bash
az group create \
    --name ${RESOURCE_GROUP} \
    --location ${AZURE_LOCATION}
```

#### Create a Virtual Network and Subnet

Create a Virtual Network and Subnet to isolate your Garden Linux instance in a dedicated network environment:

```bash
VNET_NAME="gardenlinux-vnet"
VNET_CIDR="10.1.0.0/16"
SUBNET_NAME="gardenlinux-subnet"
SUBNET_CIDR="10.1.0.0/24"

az network vnet create \
    --resource-group ${RESOURCE_GROUP} \
    --name ${VNET_NAME} \
    --address-prefix ${VNET_CIDR} \
    --subnet-name ${SUBNET_NAME} \
    --subnet-prefix ${SUBNET_CIDR}
```

#### Create a Network Security Group

Create a network security group to control network access to your instance. This configuration allows all traffic between instances in the same security group and SSH access from your current public IP:

```bash
NSG_NAME="gardenlinux-nsg"

az network nsg create \
 --resource-group ${RESOURCE_GROUP} \
 --name ${NSG_NAME}

# Allow SSH from your current public IP
az network nsg rule create \
 --resource-group ${RESOURCE_GROUP} \
 --nsg-name ${NSG_NAME} \
 --name allow-ssh \
 --priority 1000 \
 --access Allow \
 --direction Inbound \
 --protocol Tcp \
 --destination-port-range 22 \
 --source-address-prefix $(curl -s ifconfig.me)/32

# Allow all traffic within the virtual network
az network nsg rule create \
 --resource-group ${RESOURCE_GROUP} \
 --nsg-name ${NSG_NAME} \
 --name allow-internal \
 --priority 1100 \
 --access Allow \
 --direction Inbound \
 --protocol '\*' \
 --source-address-prefix ${VNET_CIDR} \
 --destination-address-prefix ${VNET_CIDR}
```

#### Create a Public IP Address

Create a public IP address to enable public internet access for your instance:

```bash
PUBLIC_IP_NAME="gardenlinux-pip"

az network public-ip create \
 --resource-group ${RESOURCE_GROUP} \
 --name ${PUBLIC_IP_NAME} \
 --allocation-method Static \
 --sku Standard
```

#### Create a Network Interface

Create a Network Interface (NIC) with the public IP (Azure requires explicit NIC creation).

```bash
NIC_NAME="gardenlinux-nic"

az network nic create \
 --resource-group ${RESOURCE_GROUP} \
 --name ${NIC_NAME} \
 --vnet-name ${VNET_NAME} \
 --subnet ${SUBNET_NAME} \
 --network-security-group ${NSG_NAME} \
 --public-ip-address ${PUBLIC_IP_NAME}
```

### Step 3: Configure SSH Access

Generate an SSH key pair and create a cloud-init script to enable SSH on first boot.

:::warning Garden Linux SSH Default
Garden Linux disables SSH by default for security. You must explicitly enable it using cloud-init user-data when launching the instance.
:::

```bash
KEY_NAME="gardenlinux-tutorial-key"
ssh-keygen -t ed25519 -f ${KEY_NAME} -N ""

USER_DATA=user_data.sh
cat >${USER_DATA} <<EOF
#cloud-config

# Enable SSH service on first boot
runcmd:
  - systemctl enable --now ssh
EOF
```

### Step 4: Launch the Instance

Launch your Garden Linux Azure VM with the prepared configuration:

```bash
VM_NAME="gardenlinux-tutorial"
VM_SIZE="Standard_B2s"

az vm create \
    --name ${VM_NAME} \
    --resource-group ${RESOURCE_GROUP} \
    --image ${IMAGE_URN} \
    --size ${VM_SIZE} \
    --admin-username azureuser \
    --ssh-key-values ${KEY_NAME}.pub \
    --custom-data ${USER_DATA} \
    --nics ${NIC_NAME} \
    --accept-term
```

### Step 5: Connect to Your Instance

Wait a few moments for the instance to boot, then retrieve its public IP address and connect via SSH:

```bash
PUBLIC_IP=$(az network public-ip show \
    --resource-group ${RESOURCE_GROUP} \
    --name ${PUBLIC_IP_NAME} \
    --query 'ipAddress' \
    --output tsv)

ssh -i ${KEY_NAME} azureuser@${PUBLIC_IP}
```

:::tip
Garden Linux uses `azureuser` as the default SSH username on Azure, consistent with Azure cloud-init conventions.
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

- Your Garden Linux instance is running on Azure
- You can connect via SSH
- You can verify the Garden Linux version using `cat /etc/os-release`

## Cleanup Resources

When you're finished with the tutorial, remove all created resources to avoid ongoing costs. Deleting the resource group removes all associated resources:

```bash
# Delete the resource group (cascades to VNet, subnet, NSG, VM, public IP)
az group delete \
    --name ${RESOURCE_GROUP} \
    --yes

# Remove local files
rm ${USER_DATA} ${KEY_NAME} ${KEY_NAME}.pub
```

## Related Topics

<RelatedTopics />
