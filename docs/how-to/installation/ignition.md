---
title: "Provision with Ignition"
description: "First-boot provisioning for bare-metal and PXE deployments using Ignition"
order: 6
related_topics:
  - /how-to/installation/on-premises/pxe-boot.md
  - /how-to/installation/on-premises/iso.md
  - /how-to/installation/post-install.md
  - /how-to/installation/cloud-init.md
migration_status: "done"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4623"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/installation/ignition.md
github_target_path: docs/how-to/installation/ignition.md
---

# Provision with Ignition

Ignition is a first-boot provisioning tool that configures Garden Linux systems declaratively before the system becomes operational. Garden Linux uses Ignition for PXE network boot deployments and bare-metal installations.

## What is Ignition?

[Ignition](https://github.com/coreos/ignition) is a low-level provisioning system that runs during the initramfs stage on first boot. It reads a declarative configuration (in JSON format) and performs system configuration tasks including:

- Creating users and groups
- Adding SSH authorized keys
- Writing files to disk (configuration files, scripts, certificates)
- Setting file permissions and ownership
- Enabling and configuring systemd units
- Formatting disks and creating filesystems

Ignition runs only once during the first boot (`ignition.firstboot=1`). After completing its tasks, it will not run again on subsequent boots.

## When to Use Ignition

Use Ignition for bare-metal and PXE deployments. The `_pxe` feature includes the `_ignite` feature, which provides Ignition support during the initramfs stage.

For cloud platform deployments (AWS, Azure, GCP, OpenStack), use [cloud-init](/how-to/installation/cloud-init.md) instead, as these platforms integrate with cloud-init natively.

## Prerequisites

- Garden Linux build with the `_ignite` feature (automatically included with `_pxe`)
- [Butane](https://github.com/coreos/butane) (optional but recommended, for translating YAML to JSON)

## Configuration format and basic structure

Ignition configurations are written in JSON format. For improved readability, write configurations in YAML using the [Butane](https://github.com/coreos/butane) translator, which converts YAML to the JSON format Ignition requires.

### Basic structure (YAML with Butane)

Create a basic Ignition configuration in YAML format:

```yaml
variant: fcos
version: 1.3.0
storage:
  files: []
systemd:
  units: []
passwd:
  users: []
```

- `variant: fcos` — Specifies Fedora CoreOS compatibility (Garden Linux uses the same Ignition specification)
- `version: 1.3.0` — Ignition configuration version

### Translate YAML to JSON with Butane

Install Butane to translate YAML configurations to JSON:

```bash
# Download Butane from GitHub releases
BUTANE_VERSION="v0.23.0"
curl -L -o butane \
  "https://github.com/coreos/butane/releases/download/${BUTANE_VERSION}/butane-x86_64-unknown-linux-gnu"

chmod +x butane
```

Translate the YAML configuration to JSON:

```bash
./butane --pretty --strict ignition.yaml > ignition.json
```

The `--strict` flag reports warnings as errors, ensuring configuration correctness.

## Common provisioning tasks

### Create users

Add a user with passwordless sudo access:

```yaml
variant: fcos
version: 1.3.0
passwd:
  users:
    - name: gardenlinux
      groups:
        - wheel
```

The `wheel` group provides passwordless sudo access in Garden Linux.

### Add SSH authorized keys

Add SSH public keys for user authentication:

```yaml
variant: fcos
version: 1.3.0
passwd:
  users:
    - name: gardenlinux
      groups:
        - wheel
      ssh_authorized_keys:
        - ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExamplePublicKeyHere user@host
```

### Configure networking

Configure a static IP address using systemd-networkd:

```yaml
variant: fcos
version: 1.3.0
storage:
  files:
    - path: /etc/systemd/network/10-eth0.network
      mode: 0644
      overwrite: true
      contents:
        inline: |
          [Match]
          Name=eth0
          
          [Network]
          Address=192.168.1.100/24
          Gateway=192.168.1.1
          DNS=9.9.9.9
```

### Install packages

Create a systemd unit that runs once to install additional packages:

```yaml
variant: fcos
version: 1.3.0
systemd:
  units:
    - name: install-packages.service
      enabled: true
      contents: |
        [Unit]
        Description=Install Additional Packages
        After=network-online.target
        Wants=network-online.target
        ConditionFirstBoot=yes
        
        [Service]
        Type=oneshot
        RemainAfterExit=yes
        ExecStart=/usr/bin/mount -o remount,rw /usr
        ExecStart=/usr/bin/apt-get update
        ExecStart=/usr/bin/apt-get install -y htop vim curl
        ExecStart=/usr/bin/mount -o remount,ro /usr
        
        [Install]
        WantedBy=multi-user.target
```

Garden Linux mounts `/usr` read-only by default. Remount it read-write before installing packages, then remount read-only afterward.

### Enable and start services

Enable systemd services on first boot:

```yaml
variant: fcos
version: 1.3.0
systemd:
  units:
    - name: ssh.service
      enabled: true
    - name: my-app.service
      enabled: true
      contents: |
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
```

### Write configuration files

Write custom configuration files to disk:

```yaml
variant: fcos
version: 1.3.0
storage:
  files:
    - path: /etc/hostname
      mode: 0644
      overwrite: true
      contents:
        inline: |
          my-server.example.com
    - path: /opt/myapp/config.yaml
      mode: 0600
      overwrite: true
      contents:
        inline: |
          database:
            host: db.example.com
            port: 5432
```

### Run custom scripts

Create a systemd unit that runs a custom script on first boot:

```yaml
variant: fcos
version: 1.3.0
storage:
  files:
    - path: /usr/local/bin/setup.sh
      mode: 0755
      overwrite: true
      contents:
        inline: |
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
systemd:
  units:
    - name: custom-setup.service
      enabled: true
      contents: |
        [Unit]
        Description=Custom Setup Script
        After=network-online.target
        Wants=network-online.target
        ConditionFirstBoot=yes
        
        [Service]
        Type=oneshot
        RemainAfterExit=yes
        ExecStart=/usr/local/bin/setup.sh
        
        [Install]
        WantedBy=multi-user.target
```

## Deliver the Configuration

How you deliver the Ignition configuration depends on the deployment method:

| Deployment Method | Delivery Mechanism |
|-------------------|-------------------|
| **PXE Boot** | Specify `ignition.config.url=` in the kernel command line (see [PXE Boot guide](/how-to/installation/on-premises/pxe-boot.md)) |
| **Bare Metal (Pre-install)** | Inject the configuration into the disk image before first boot |
| **VM Testing** | Use firmware configuration (`fw_cfg`) or attach as a volume |

### PXE boot example

In your iPXE boot script, specify the Ignition configuration URL:

```
#!ipxe
set base-url http://192.168.1.10:8080
kernel ${base-url}/rootfs.vmlinuz initrd=rootfs.initrd \
  gl.ovl=/:tmpfs gl.url=${base-url}/root.squashfs gl.live=1 \
  ip=dhcp ignition.firstboot=1 \
  ignition.config.url=${base-url}/ignition.json \
  ignition.platform.id=metal
initrd ${base-url}/rootfs.initrd
boot
```

## Advanced configuration

### Partition and format disks

Define custom partition layouts and filesystems:

```yaml
variant: fcos
version: 1.3.0
storage:
  files:
    - path: /opt/onmetal-install/partitions
      mode: 0755
      overwrite: true
      contents:
        inline: |
          label: gpt
          type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, name="EFI", size=510MiB
          type=4f68bce3-e8cd-4db1-96e7-fbcaf984b709, name="ROOT"
    - path: /opt/onmetal-install/target
      mode: 0755
      overwrite: true
      contents:
        inline: |
          disk=/dev/sda
```

This configuration is used by the Garden Linux PXE installation script to partition the target disk.

:::info
The ROOT partition type uses the x86-64 root partition GUID (`4f68bce3-e8cd-4db1-96e7-fbcaf984b709`) from the [Discoverable Partitions Specification](https://uapi-group.org/specifications/specs/discoverable_partitions_specification/). For ARM64 systems, use `b921b045-1df0-41c3-af44-4c6f280d3fae`.
:::

### Merge multiple configurations

Split complex configurations into multiple files using the `merge` directive:

```yaml
variant: fcos
version: 1.3.0
ignition:
  config:
    merge:
      - source: http://example.com/base-config.json
      - source: http://example.com/network-config.json
storage:
  files:
    - path: /etc/hostname
      mode: 0644
      overwrite: true
      contents:
        inline: |
          my-server.example.com
```

Ignition fetches and merges the referenced configurations during first boot.

### Ignition platforms

Ignition uses the `ignition.platform.id=` kernel parameter to identify the platform and determine where to fetch configuration:

| Platform ID | Description |
|-------------|-------------|
| `metal` | Bare-metal or VM without cloud metadata |
| `qemu` | QEMU/KVM virtualization |
| `openstack` | OpenStack cloud platform |

For Garden Linux PXE deployments, use `ignition.platform.id=metal`.

## Troubleshooting

### View Ignition logs

If Ignition fails during first boot, check the journal for error messages:

```bash
journalctl -u ignition-fetch.service
journalctl -u ignition-disks.service
journalctl -u ignition-files.service
```

### Validate configuration syntax

Use Butane to validate your YAML configuration before translating to JSON:

```bash
./butane --strict ignition.yaml > /dev/null
```

If the configuration is valid, Butane outputs nothing. Errors are reported to stderr.

### Common errors

- **Configuration not fetched** — Verify the URL specified in `ignition.config.url=` is reachable from the target system
- **Files not written** — Ensure file paths are absolute and parent directories exist
- **Units not enabled** — Check systemd unit syntax using `systemd-analyze verify`

## Reference

- [Ignition Documentation (Fedora CoreOS)](https://docs.fedoraproject.org/en-US/fedora-coreos/producing-ign/)
- [Ignition Specification](https://coreos.github.io/ignition/)
- [Ignition Configuration Examples](https://coreos.github.io/ignition/examples/)
- [Butane Documentation](https://coreos.github.io/butane/)
- [Butane Configuration Specification](https://coreos.github.io/butane/config-fcos-v1_5/)

## Related topics

<RelatedTopics />
