---
title: "Feature: aws"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/aws/README.md
github_target_path: docs/reference/features/aws.md
---

## Feature: aws

### Description

A [platform](/reference/glossary.html#platform) feature that builds a Garden Linux
image for [Amazon Web Services (AWS)](/reference/glossary#aws). The image is delivered as a `.raw` file
suitable for import into AWS.

### What it does

Installs `cloud-init` and `amazon-ec2-utils` to handle instance initialization,
metadata retrieval, and EC2-specific utilities. The feature configures:

- **DNS resolver**: configures `systemd-resolved` with AWS-specific settings.
- **Time synchronization**: configures `systemd-timesyncd` to use the
- **Clocksource**: enables a systemd service (`aws-clocksource.service`) that
  selects the appropriate clocksource for the EC2 hypervisor.
  AWS-provided NTP endpoint.
- **Cloud-init**: removes the `growpart`, `resizefs`, and `ntp` modules from
  the cloud-init configuration (partition growth is handled in the initramfs;
  NTP is managed by `systemd-timesyncd`).
- **Kernel command line**: sets console and NVMe parameters for the AWS
  environment.
- **Dracut**: includes the `xen-blkfront` driver for compatibility with
  Xen-based instance types.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aws/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Strips `growpart`, `resizefs`, and `ntp` modules from `cloud-init` configuration and enables `aws-clocksource.service`. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aws/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aws/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: platform` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aws/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `cloud-init`, `amazon-ec2-utils`, `dmidecode`, and `python3-cffi-backend`. |
| [`file.include/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aws/file.include/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg) ([`file.include`](/reference/features/#file-include)) | Debian-specific cloud-init configuration baseline. |
| [`file.include/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aws/file.include/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg) ([`file.include`](/reference/features/#file-include)) | Disables cloud-init network configuration management (networking is handled by systemd). |
| [`file.include/etc/dracut.conf.d/90-xen-blkfront-driver.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aws/file.include/etc/dracut.conf.d/90-xen-blkfront-driver.conf) ([`file.include`](/reference/features/#file-include)) | Includes the `xen-blkfront` kernel module in the initramfs for Xen-backed instance types. |
| [`file.include/etc/kernel/cmdline.d/10-console.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aws/file.include/etc/kernel/cmdline.d/10-console.cfg) ([`file.include`](/reference/features/#file-include)) | Sets the kernel console parameter for the AWS serial console. |
| [`file.include/etc/kernel/cmdline.d/70-nvme.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aws/file.include/etc/kernel/cmdline.d/70-nvme.cfg) ([`file.include`](/reference/features/#file-include)) | Adds NVMe-specific kernel parameters. |
| [`file.include/etc/systemd/resolved.conf.d/00-gardenlinux-aws.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aws/file.include/etc/systemd/resolved.conf.d/00-gardenlinux-aws.conf) ([`file.include`](/reference/features/#file-include)) | Configures `systemd-resolved` with AWS DNS settings. |
| [`file.include/etc/systemd/system/aws-clocksource.service`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aws/file.include/etc/systemd/system/aws-clocksource.service) ([`file.include`](/reference/features/#file-include)) | Systemd service that sets the clocksource appropriate for the EC2 hypervisor. |
| [`file.include/etc/systemd/system/cloud-init-local.service.d/override.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aws/file.include/etc/systemd/system/cloud-init-local.service.d/override.conf) ([`file.include`](/reference/features/#file-include)) | Systemd drop-in that adjusts `cloud-init-local` ordering. |
| [`file.include/etc/systemd/timesyncd.conf.d/00-gardenlinux-aws.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aws/file.include/etc/systemd/timesyncd.conf.d/00-gardenlinux-aws.conf) ([`file.include`](/reference/features/#file-include)) | Configures `systemd-timesyncd` to use the AWS NTP endpoint (`169.254.169.123`). |
| [`file.include/usr/local/sbin/clocksource-setup.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/aws/file.include/usr/local/sbin/clocksource-setup.sh) ([`file.include`](/reference/features/#file-include)) | Script invoked by `aws-clocksource.service` to detect and set the correct clocksource. |

### Related features

**Includes:**

- [`cloud`](/reference/features/cloud) — provides common cloud-init integration and base cloud configuration shared across cloud platforms.

### Further reading

- [cloud-init documentation](https://cloudinit.readthedocs.io/)
- [amazon-ec2-utils](https://github.com/amazonlinux/amazon-ec2-utils)

## Related topics

<RelatedTopics />

