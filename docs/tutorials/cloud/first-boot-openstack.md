---
title: "First Boot on OpenStack"
description: "Step-by-step guide to deploying Garden Linux on OpenStack"
category: "tutorials"
tags: ["tutorial", "openstack", "cloud", "beginner"]
migration_status: "new"
migration_source: ""
migration_issue: ""
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/tutorials/cloud/first-boot-openstack.md
github_target_path: "docs/tutorials/cloud/first-boot-openstack.md"
---

# First Boot on OpenStack

Garden Linux is a minimal, security-hardened Linux distribution designed for cloud and container environments. This tutorial guides you through deploying your first Garden Linux instance on [OpenStack](https://www.openstack.org/), from uploading an image to connecting via SSH.

**Difficulty:** Beginner | **Time:** ~15 minutes

**Learning Objective:** By the end of this tutorial, you'll have a running Garden Linux instance on OpenStack and understand the basic deployment process.

## Prerequisites

Before starting, you'll need:

- An OpenStack environment with appropriate permissions to create instances, networks, and security groups
- [OpenStack CLI](https://docs.openstack.org/python-openstackclient/latest/) installed (`python-openstackclient`)
- OpenStack credentials configured (sourced `openrc` file or `clouds.yaml` with `OS_CLOUD` environment variable set)
- Knowledge of your OpenStack environment's external/public network name and available flavors
- An SSH client on your local machine

## What You'll Build

You'll upload a Garden Linux image to your OpenStack Glance service, deploy an instance with a basic networking setup (network, subnet, router, security group, and floating IP), configure SSH access, and verify the installation. The tutorial uses the `gardener_prod` [flavor](../../explanation/flavors-and-features.md), which is optimized for production workloads.

## Steps

### Step 1: Choose an Image

Garden Linux provides pre-built images for OpenStack. Start by downloading and uploading an appropriate image to your OpenStack environment.

#### Official Images

Choose a release from the [GitHub Releases page](https://github.com/gardenlinux/gardenlinux/releases). For this tutorial, we'll use [release 2150.0.0](https://github.com/gardenlinux/gardenlinux/releases/tag/2150.0.0).

In the "Published Images" section on the release page, find the image for your desired [flavor](../../explanation/flavors-and-features.md) and [architecture](../../reference/glossary.md#architecture). The default production flavor is `openstack-gardener_prod-amd64`. You can directly download it there.

To download it by script, look in the "Assets" section on the release page, and find the `.tar.xz` archive for the `openstack-gardener_prod-amd64` [flavor](../../explanation/flavors-and-features.md). Download and extract the `.qcow2` image, then upload it to your OpenStack Glance service:

```bash
GL_VERSION="2150.0.0"
GL_COMMIT="eb8696b9"
GL_ARCH="amd64"
GL_ASSET="openstack-gardener_prod-${GL_ARCH}-${GL_VERSION}-${GL_COMMIT}"
GL_QCOW2="${GL_ASSET}.qcow2"
GL_TAR_XZ="${GL_ASSET}.tar.xz"

# Download and extract the image
curl -L -o "${GL_TAR_XZ}" \
  "https://github.com/gardenlinux/gardenlinux/releases/download/${GL_VERSION}/${GL_TAR_XZ}"

tar -xf "${GL_TAR_XZ}" "${GL_QCOW2}"

# Upload to Glance
IMAGE_ID=$(openstack image create gardenlinux-tutorial \
    --disk-format qcow2 \
    --container-format bare \
    --file ${GL_QCOW2} \
    -f value -c id)
```

:::tip
Set `GL_ARCH` to `arm64` if you would like to download/upload the arm version.

```bash
GL_ARCH="arm64"
```

:::

:::tip
For a complete list of maintained releases and their support lifecycle, see the [releases reference](../../reference/releases/index.md).
:::

#### Build Your Own Images

To create custom Garden Linux images with additional features or configurations, see the [Building Flavors guide](../../how-to/customization/building-flavors.md).

### Step 2: Prepare Your OpenStack Environment

Before launching your Garden Linux instance, set up the necessary OpenStack networking infrastructure. This step creates a network, subnet, router, security group, and floating IP.

:::warning Environment-Specific Values
The `PUBLIC_NETWORK` name must match your OpenStack environment's external network. Common names include `public`, `external`, or `ext-net`. Check with your OpenStack administrator if unsure.
:::

#### Create a Virtual Network and Subnet

Create a Virtual Network and Subnet to isolate your Garden Linux instance in a dedicated network environment:

```bash
NETWORK_NAME="gardenlinux-network"
SUBNET_NAME="gardenlinux-subnet"
SUBNET_CIDR="10.1.0.0/24"

openstack network create ${NETWORK_NAME}

openstack subnet create ${SUBNET_NAME} \
    --network ${NETWORK_NAME} \
    --subnet-range ${SUBNET_CIDR}
```

#### Create router and connect to external network

Create a router and connect to external network to enable external access to your instance.

```bash
ROUTER_NAME="gardenlinux-router"
PUBLIC_NETWORK="public"  # Adjust to your OpenStack external network name

openstack router create ${ROUTER_NAME}

openstack router set ${ROUTER_NAME} \
    --external-gateway ${PUBLIC_NETWORK}

openstack router add subnet ${ROUTER_NAME} ${SUBNET_NAME}
```

#### Create a Network Security Group

Create a network security group to control network access to your instance. This configuration allows SSH access from your current public IP:

```bash
SG_NAME="gardenlinux-sg"

openstack security group create ${SG_NAME}

openstack security group rule create ${SG_NAME} \
 --protocol tcp \
 --dst-port 22 \
 --remote-ip $(curl -s ifconfig.me)/32
```

#### Create a Floating IP Address

Create a floating IP address to enable external access for your instance:

```bash
FLOATING_IP=$(openstack floating ip create ${PUBLIC_NETWORK} \
 -f value -c floating_ip_address)
```

### Step 3: Configure SSH Access

Generate an SSH key pair, register it with OpenStack, and create a cloud-init script to enable SSH on first boot.

:::warning Garden Linux SSH Default
Garden Linux disables SSH by default for security. You must explicitly enable it using cloud-init user-data when launching the instance.
:::

```bash
KEY_NAME="gardenlinux-tutorial-key"
ssh-keygen -t ed25519 -f ${KEY_NAME} -N ""

openstack keypair create ${KEY_NAME} \
    --public-key ${KEY_NAME}.pub

USER_DATA=user_data.sh
cat >${USER_DATA} <<EOF
#!/usr/bin/env bash

# Enable SSH service on first boot
systemctl enable --now ssh
EOF
```

### Step 4: Launch the Instance

Launch your Garden Linux OpenStack instance with the prepared configuration:

:::warning Environment-Specific Values
The `FLAVOR_NAME` must match an available flavor in your OpenStack environment. Common names include `m1.small`, `m1.medium`, or custom flavors. Use `openstack flavor list` to see available options.
:::

```bash
INSTANCE_NAME="gardenlinux-tutorial"
FLAVOR_NAME="m1.small"  # Adjust to an available flavor in your environment

openstack server create ${INSTANCE_NAME} \
    --image gardenlinux-tutorial \
    --flavor ${FLAVOR_NAME} \
    --network ${NETWORK_NAME} \
    --security-group ${SG_NAME} \
    --key-name ${KEY_NAME} \
    --user-data ${USER_DATA} \
    --config-drive true \
    --wait

# Associate the floating IP
openstack server add floating ip ${INSTANCE_NAME} ${FLOATING_IP}
```

:::tip ConfigDrive
The `--config-drive true` option ensures cloud-init data is available to the instance via ConfigDrive, which is the preferred datasource for Garden Linux on OpenStack.
:::

### Step 5: Connect to Your Instance

Wait a few moments for the instance to complete its startup script, then connect via SSH:

```bash
ssh -i ${KEY_NAME} admin@${FLOATING_IP}
```

:::tip
Garden Linux uses `admin` as the default SSH username on OpenStack, as configured by cloud-init.
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

- Your Garden Linux instance is running on OpenStack
- You can connect via SSH
- You can verify the Garden Linux version using `cat /etc/os-release`

## Cleanup Resources

When you're finished with the tutorial, remove all created resources. The cleanup process must follow a specific order due to dependencies between resources:

```bash
# Remove floating IP from server
openstack server remove floating ip ${INSTANCE_NAME} ${FLOATING_IP}

# Delete the server
openstack server delete ${INSTANCE_NAME} --wait

# Delete the floating IP
openstack floating ip delete ${FLOATING_IP}

# Delete the security group
openstack security group delete ${SG_NAME}

# Remove router interface, then delete router
openstack router remove subnet ${ROUTER_NAME} ${SUBNET_NAME}
openstack router delete ${ROUTER_NAME}

# Delete subnet and network
openstack subnet delete ${SUBNET_NAME}
openstack network delete ${NETWORK_NAME}

# Delete the keypair
openstack keypair delete ${KEY_NAME}

# Delete the image
openstack image delete gardenlinux-tutorial

# Remove local files
rm ${USER_DATA} ${KEY_NAME} ${KEY_NAME}.pub ${GL_QCOW2} ${GL_TAR_XZ}
```

## Next Steps

Now that you have a running Garden Linux instance on OpenStack, you can:

- Explore [OpenStack platform-specific features and configurations](../../how-to/platform-specific/openstack.md)
- Discover how to [build custom Garden Linux images](../../how-to/customization/building-flavors.md) with additional features
