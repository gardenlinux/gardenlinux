---
title: "Post Installation Steps"
description: "Suggested First Steps after Installation"
category: "ho-to"
tags: ["how-to"]
migration_status: "new"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4623"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/installation/post-install.md
github_target_path: docs/how-to/installation/post-install.md
related_topics:
    - /how-to/installation/index.md
    - /tutorials/on-premises/first-boot-bare-metal.md
    - /tutorials/local/first-boot-kvm.md
    - /tutorials/local/first-boot-lima.md
    - /tutorials/cloud/first-boot-aws.md
    - /tutorials/cloud/first-boot-azure.md
    - /tutorials/cloud/first-boot-gcp.md
    - /tutorials/cloud/first-boot-openstack.md
---

## Creating A User

Garden Linux installations, do not create a default user on installation. This
is due to the specific use cases it was designed for not requiring a user.

If you would still like to create a new user account for you to use, follow the
instructions below.

### When Is Manual User Creation Required?

Manual user creation can be necessary, if:

- Deploying on **bare metal** without PXE/Ignition support
- Running on **KVM/QEMU** without cloud-init (e.g for testing)
- Any environment where cloud-init or similar provisioning is unavailable

For cloud deployments, users are automatically provisioned via cloud-init. See
the platform specific tutorials:

- [First Boot on AWS](/docs/tutorials/cloud/first-boot-aws.md)
- [First Boot on Azure](/docs/tutorials/cloud/first-boot-azure.md)
- [First Boot on GCP](/docs/tutorials/cloud/first-boot-gcp.md)
- [First Boot on OpenStack](/docs/tutorials/cloud/first-boot-openstack.md)

### Method 1: `chroot` (For Bare Metal / Offline Deployments)

Use this method when you have **direct access** to the disk (e.g., from a live
system before first boot).

#### Step 1: Mount the Root Partition

```bash
# Identify and mount the root partition
TARGET_DISK="/dev/sda" # Or your desired target drive
ROOT_PART="${TARGET_DISK}3" # Partition 3 on gardener builds
USR_PART="${TARGET_DISK}1"  # Partition 1 contains usr/

mount ${ROOT_PART} /mnt
mount -o ro ${USR_PART} /mnt/usr
```

#### Step 2: Create the User

```bash
USERNAME="gardenlinux"
chroot /mnt /bin/bash -c "useradd -m -G wheel -s /bin/bash ${USERNAME}"
```

#### Step 3: Unmount and Reboot

Finally, you need to unmount the image and reboot the system without any live
media present.

```bash
umount /mnt/usr
umount /mnt
reboot
```

For a complete walkthrough and to learn what else you can do with a local
installation, see the
[First Boot on Bare Metal](/docs/tutorials/on-premises/first-boot-bare-metal.md)
guide.

### Method 2: `fw_cfg` script (KVM/QEMU)

Use this method when launching Garden Linux in QEMU/KVM. This script executes
automatically on first boot.

```bash
USERNAME="gardenlinux"
SSH_PUBLIC_KEY="ssh-ed25519 AAAA... user@host"

cat > fw_cfg-script.sh <<EOF
#!/usr/bin/env bash
set -eufo pipefail
# Create user with sudo access
useradd -U -m -G wheel -s /bin/bash ${USERNAME}
# Configure SSH
mkdir -p /home/${USERNAME}/.ssh
chmod 700 /home/${USERNAME}/.ssh
echo "${SSH_PUBLIC_KEY}" >> /home/${USERNAME}/.ssh/authorized_keys
chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}/.ssh
chmod 600 /home/${USERNAME}/.ssh/authorized_keys
# Enable SSH service
systemctl enable --now ssh
EOF
```

Pass this script to QEMU using:

```bash
qemu-system-x86_64 ... \
    -fw_cfg name=opt/gardenlinux/config_script,file=fw_cfg-script.sh
```

For a complete walkthrough and more information about setting up Garden Linux on
KVM see [First Boot on KVM](/docs/tutorials/local/first-boot-kvm.md).

### Method 3: cloud-init user-data (Cloud Platforms)

On cloud platforms with cloud-init support, users are typically pre-configured.
You only need to enable SSH to access them:

```bash
cat > user_data.sh <<EOF
#!/usr/bin/env bash
systemctl enable --now ssh
EOF
```

#### Default Usernames per Platform

The default usernames vary by platform:

| Platform  | DefaultUsername |
| --------- | --------------- |
| AWS       | ec2-user        |
| Azure     | azureuser       |
| GCP       | gardenlinux     |
| OpenStack | admin           |

### The Wheel Group

Garden Linux uses the `wheel` group for passwordless `sudo` access. Users in
this group have full administrative access without requiring a password for
`sudo` commands.

You can verify if the user is correctly added to this group by running:

```bash
groups ${USERNAME}
```

Which should produce this output:

```
$USERNAME : wheel
```

### Setting a Password (optional)

Garden Linux is configured for SSH key-based authentication by default. If you
need password authentication (which is **not** recommended for any production
environment) you can do so:

```bash
# Set a password for the user account
chroot /mnt /bin/bash -c "passwd ${USERNAME}"

# Or on a running system
sudo passwd ${USERNAME}
```

:::warning Security Warning Password authentication is disabled by default in
Garden Linux' SSH configuration for security reasons. We **strongly recommend**
key-based authentication on any networked system, even in a testing context. :::
