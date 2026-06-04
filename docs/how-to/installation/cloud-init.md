---
title: "Provision with cloud-init"
description: "First-boot provisioning for cloud deployments using cloud-init"
order: 5
related_topics:
  - /how-to/installation/cloud/aws.md
  - /how-to/installation/cloud/azure.md
  - /how-to/installation/cloud/gcp.md
  - /how-to/installation/cloud/openstack.md
  - /how-to/installation/post-install.md
  - /how-to/installation/ignition.md
migration_status: "done"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4623"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/installation/cloud-init.md
github_target_path: docs/how-to/installation/cloud-init.md
---

# Provision with cloud-init

cloud-init is the industry-standard multi-distribution method for cross-platform cloud instance initialization. Garden Linux uses cloud-init on all major cloud platforms (AWS, Azure, GCP, OpenStack) for first-boot provisioning and configuration.

## What is cloud-init?

[cloud-init](https://cloud-init.io/) is a widely-adopted provisioning tool that automates the initialization of cloud instances. It runs on every boot (not just first boot) and performs tasks including:

- Creating users and groups
- Adding SSH authorized keys
- Configuring networking (DHCP, static IPs)
- Writing files to disk
- Running custom shell scripts
- Installing packages
- Configuring system services

cloud-init fetches its configuration from the cloud platform's metadata service or via user-data mechanisms specific to each platform.

## When to Use cloud-init

Use cloud-init for cloud platform deployments (AWS, Azure, GCP, OpenStack, VMware). All Garden Linux cloud platform images include cloud-init by default.

For bare-metal and PXE deployments, use [Ignition](/how-to/installation/ignition.md) instead, as Ignition is designed for first-boot-only metal provisioning.

## Prerequisites

- Garden Linux cloud platform image (aws, azure, gcp, openstack, vmware flavors automatically include cloud-init)
- Access to the cloud platform's user-data mechanism (varies by platform)

## Configuration Format and Basic Structure

cloud-init supports two user-data formats: cloud-config (YAML) and shell scripts.

### cloud-config (YAML Format)

Start with `#cloud-config`. Provides declarative configuration:

```yaml
#cloud-config
users: []
write_files: []
runcmd: []
```

### Shell Scripts (Shebang Format)

Start with a shebang (`#!/usr/bin/env bash`). cloud-init executes the script directly:

```bash
#!/usr/bin/env bash
systemctl enable --now ssh
echo "Hello from Garden Linux" > /etc/motd
```

Use shell scripts for simple tasks and procedural logic. Use cloud-config for declarative user and file management.

## Common Provisioning Tasks

### Create Users

Add a new user with passwordless sudo access:

```yaml
#cloud-config
users:
  - name: gardenlinux
    groups: wheel
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
```

The `wheel` group provides passwordless sudo access in Garden Linux.

### Add SSH Authorized Keys

Add SSH public keys for user authentication:

```yaml
#cloud-config
users:
  - name: gardenlinux
    groups: wheel
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys:
      - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExamplePublicKeyHere user@host
```

### Configure Networking

Configure a static IP address using systemd-networkd:

```yaml
#cloud-config
write_files:
  - path: /etc/systemd/network/10-eth0.network
    content: |
      [Match]
      Name=eth0

      [Network]
      Address=192.168.1.100/24
      Gateway=192.168.1.1
      DNS=9.9.9.9
    owner: root:root
    permissions: '0644'
runcmd:
  - systemctl restart systemd-networkd
```

Most cloud platforms handle networking automatically via DHCP and metadata services. Use custom network configuration only when required.

### Install Packages

Install additional software packages on first boot:

```yaml
#cloud-config
runcmd:
  - mount -o remount,rw /usr
  - apt-get update
  - apt-get install -y htop vim curl
  - mount -o remount,ro /usr
```

Garden Linux mounts `/usr` read-only by default. Remount it read-write before installing packages, then remount read-only afterward.

Alternatively, use a shell script for package installation:

```bash
#!/usr/bin/env bash
# Install additional packages
mount -o remount,rw /usr
apt-get update
apt-get install -y htop vim curl
mount -o remount,ro /usr
```

### Enable and Start Services

Enable and start systemd units:

```yaml
#cloud-config
runcmd:
  - systemctl enable --now ssh
  - systemctl enable --now my-app
```

For custom service definitions, write the unit file and enable it:

```yaml
#cloud-config
write_files:
  - path: /etc/systemd/system/my-app.service
    content: |
      [Unit]
      Description=My Application Service
      After=network-online.target
      Wants=network-online.target

      [Service]
      Type=simple
      ExecStart=/usr/local/bin/my-app
      Restart=on-failure

      [Install]
      WantedBy=multi-user.target
    owner: root:root
    permissions: '0644'
runcmd:
  - systemctl daemon-reload
  - systemctl enable --now my-app
```

### Write Configuration Files

Write custom configuration files to disk:

```yaml
#cloud-config
write_files:
  - path: /etc/hostname
    content: |
      my-server.example.com
    owner: root:root
    permissions: '0644'
  - path: /opt/myapp/config.yaml
    content: |
      database:
        host: db.example.com
        port: 5432
    owner: root:root
    permissions: '0600'
```

### Run Custom Scripts

Execute custom shell scripts during instance initialization:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Enable SSH
systemctl enable --now ssh

# Create application directory
mkdir -p /opt/myapp/data

# Write configuration
cat > /opt/myapp/config.yaml <<EOF
database:
  host: db.example.com
  port: 5432
EOF

echo "Setup completed"
```

Or use cloud-config to write and execute a script:

```yaml
#cloud-config
write_files:
  - path: /usr/local/bin/setup.sh
    content: |
      #!/usr/bin/env bash
      set -euo pipefail

      # Create application directory
      mkdir -p /opt/myapp/data

      # Write configuration
      cat > /opt/myapp/config.yaml <<EOF
      database:
        host: db.example.com
        port: 5432
      EOF

      echo "Setup completed"
    owner: root:root
    permissions: '0755'
runcmd:
  - /usr/local/bin/setup.sh
```

## Deliver the Configuration

How you deliver cloud-init configuration depends on the cloud platform. Each platform provides its own mechanism for attaching user-data to instances:

| Platform | Delivery Mechanism | Official Documentation | Garden Linux Guide |
|----------|-------------------|----------------------|-------------------|
| **AWS** | EC2 user-data | [EC2 User Data](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html#userdata-linux) | [Install on AWS](/how-to/installation/cloud/aws.md) |
| **Azure** | Custom data | [Azure Custom Data](https://learn.microsoft.com/en-us/azure/virtual-machines/custom-data) | [Install on Azure](/how-to/installation/cloud/azure.md) |
| **GCP** | Metadata | [GCP cloud-init](https://cloud.google.com/container-optimized-os/docs/how-to/create-configure-instance#use-cloud-init) | [Install on GCP](/how-to/installation/cloud/gcp.md) |
| **OpenStack** | ConfigDrive or metadata service | [OpenStack User Data](https://docs.openstack.org/nova/queens/user/user-data.html) | [Install on OpenStack](/how-to/installation/cloud/openstack.md) |

For step-by-step deployment walkthroughs including instance creation with user-data, see the platform-specific tutorials:
- [First Boot on AWS](/tutorials/cloud/first-boot-aws.md)
- [First Boot on Azure](/tutorials/cloud/first-boot-azure.md)
- [First Boot on GCP](/tutorials/cloud/first-boot-gcp.md)
- [First Boot on OpenStack](/tutorials/cloud/first-boot-openstack.md)

### Default Usernames per Platform

Garden Linux cloud images include a platform-specific default user:

| Platform  | Default Username |
| --------- | --------------- |
| AWS       | admin           |
| Azure     | azureuser       |
| GCP       | gardenlinux     |
| OpenStack | admin           |

These users are pre-configured with SSH key access via the cloud platform's metadata service or the User-Data. You only need to enable SSH to access them.

## Advanced Configuration

### Multi-Part MIME User-Data

Combine multiple user-data formats (cloud-config + shell script):

```python
#!/usr/bin/env python3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

combined = MIMEMultipart()

# Part 1: cloud-config
cloud_config = """#cloud-config
users:
  - name: gardenlinux
    groups: wheel
"""
combined.attach(MIMEText(cloud_config, 'cloud-config'))

# Part 2: shell script
shell_script = """#!/usr/bin/env bash
systemctl enable --now ssh
"""
combined.attach(MIMEText(shell_script, 'x-shellscript'))

print(combined.as_string())
```

### Conditional Execution

Run commands only on specific platforms:

```yaml
#cloud-config
runcmd:
  - [ sh, -c, 'if [ "$(cloud-init query platform)" = "aws" ]; then echo "Running on AWS"; fi' ]
```

### Fetch External Configuration

Download and apply configuration from external sources:

```yaml
#cloud-config
runcmd:
  - curl -o /tmp/setup.sh https://example.com/setup.sh
  - bash /tmp/setup.sh
```

## Troubleshooting

### View cloud-init Logs

Check cloud-init execution logs:

```bash
# View cloud-init status
cloud-init status --long

# View cloud-init logs
journalctl -u cloud-init

# View detailed logs
cat /var/log/cloud-init.log
cat /var/log/cloud-init-output.log
```

### Validate Configuration Syntax

Test cloud-config syntax before deploying:

```bash
# Validate cloud-config YAML
cloud-init schema --config-file user_data.yaml

# Dry-run cloud-init
cloud-init devel schema --config-file user_data.yaml
```

### Common Errors

- **SSH not enabled** — Ensure user-data includes `systemctl enable --now ssh`
- **User not created** — Verify cloud-config YAML syntax and check `/var/log/cloud-init.log`
- **Metadata not fetched** — Confirm the instance has network connectivity to the metadata service
- **Script not executed** — Ensure shell scripts start with a valid shebang (`#!/usr/bin/env bash`)

## Reference

- [cloud-init Documentation](https://cloudinit.readthedocs.io/)
- [cloud-init Examples](https://cloudinit.readthedocs.io/en/latest/reference/examples.html)
- [cloud-init Module Reference](https://cloudinit.readthedocs.io/en/latest/reference/modules.html)
- [cloud-init Network Configuration](https://cloudinit.readthedocs.io/en/latest/reference/network-config.html)
- [AWS EC2 User Data](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html#userdata-linux)
- [Azure Custom Data](https://learn.microsoft.com/en-us/azure/virtual-machines/custom-data)
- [GCP cloud-init](https://cloud.google.com/container-optimized-os/docs/how-to/create-configure-instance#use-cloud-init)
- [OpenStack User Data](https://docs.openstack.org/nova/queens/user/user-data.html)

## Related Topics

<RelatedTopics />
