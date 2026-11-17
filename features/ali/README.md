---
title: "Feature: ali"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/ali/README.md
github_target_path: docs/reference/features/ali.md
---

## Feature: ali

### Description

A [platform](/reference/glossary.html#platform) feature that builds a Garden Linux
image for [Alibaba Cloud (Aliyun)](/reference/glossary#alibaba-cloud-aliyun). Artifacts are delivered as `.raw` and `.qcow2`
files.

### What it does

Installs `cloud-init` for instance initialization on Alibaba Cloud and
configures platform-specific settings:

- **DNS resolver**: configures `systemd-resolved` with Alibaba Cloud DNS settings.
- **Time synchronization**: configures `systemd-timesyncd` with the Alibaba
  Cloud NTP endpoint.
- **Cloud-init**: provides a Debian-compatible cloud-init baseline and disables
  cloud-init network management (networking handled by systemd).
- **Kernel command line**: sets the console parameter for the Alibaba Cloud
  serial console.
- **Image conversion**: `convert.qcow2` produces a `.qcow2` image from the raw
  build artifact.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`convert.qcow2`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ali/convert.qcow2) ([ref](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Converts the `.raw` artifact to a `.qcow2` image for Alibaba Cloud import. |
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ali/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Applies Alibaba Cloud-specific cloud-init and system configuration. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ali/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ali/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: platform` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ali/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `cloud-init`, `dmidecode`, and `python3-cffi-backend`. |
| [`file.include/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ali/file.include/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg) ([`file.include`](/reference/features/#file-include)) | Debian-specific cloud-init configuration baseline. |
| [`file.include/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ali/file.include/etc/cloud/cloud.cfg.d/99_disable-network-config.cfg) ([`file.include`](/reference/features/#file-include)) | Disables cloud-init network configuration management. |
| [`file.include/etc/kernel/cmdline.d/10-console.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ali/file.include/etc/kernel/cmdline.d/10-console.cfg) ([`file.include`](/reference/features/#file-include)) | Sets the kernel console parameter for the Alibaba Cloud serial console. |
| [`file.include/etc/systemd/resolved.conf.d/00-gardenlinux-ali.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ali/file.include/etc/systemd/resolved.conf.d/00-gardenlinux-ali.conf) ([`file.include`](/reference/features/#file-include)) | Configures `systemd-resolved` with Alibaba Cloud DNS settings. |
| [`file.include/etc/systemd/timesyncd.conf.d/00-gardenlinux-ali.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/ali/file.include/etc/systemd/timesyncd.conf.d/00-gardenlinux-ali.conf) ([`file.include`](/reference/features/#file-include)) | Configures `systemd-timesyncd` to use the Alibaba Cloud NTP endpoint. |

### Related features

**Includes:**

- [`cloud`](/reference/features/cloud) — provides common cloud-init integration and base cloud configuration shared across cloud platforms.

### Further reading

- [cloud-init documentation](https://cloudinit.readthedocs.io/)

## Related topics

<RelatedTopics />

