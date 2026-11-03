---
title: "Feature: gdch"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/gdch/README.md
github_target_path: docs/reference/features/gdch.md
---

## Feature: gdch

### Description

A [platform](/reference/glossary.html#platform) feature that builds a Garden Linux
image for [Google Distributed Cloud Hosted (GDCH)](/reference/glossary#gdch). Artifacts are delivered as
`.raw` files packaged in a `.gcpimage.tar.gz` tarball.

### What it does

Configures Garden Linux for GDCH deployment, which uses a Google Cloud-like
environment hosted on-premises or in a private data center:

- **Time synchronization**: uses `chrony` (instead of `systemd-timesyncd`,
  which is excluded) for time synchronization in the GDCH environment.
- **Timezone**: sets the default timezone to UTC.
- **Cloud-init**: provides GDCH-specific cloud-init system configuration.
- **SSH**: appends the Google OS Login `AuthorizedKeysCommand` directives to
  `sshd_config`.
- **Kernel command line**: sets GDCH-specific kernel boot parameters and
  console settings.
- **Image conversion**: `convert.gcpimage.tar.gz` produces a tarball in the
  GCP image import format.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`convert.gcpimage.tar.gz`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gdch/convert.gcpimage.tar.gz) ([ref](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Packages the `.raw` artifact into a `disk.raw`-named tarball for GDCH image import. |
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gdch/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Sets timezone to UTC and appends Google OS Login SSH directives to `sshd_config`. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gdch/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gdch/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: platform` and included/excluded features. |
| [`pkg.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gdch/pkg.exclude) ([ref](/reference/features/#pkg-exclude)) | Prevents installation of `irqbalance` and `systemd-timesyncd` (replaced by `chrony`). |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gdch/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `chrony`, `cloud-init`, `nvme-cli`, and `python3-cffi-backend`. |
| [`file.include/etc/cloud/cloud.cfg.d/91-gdch-system.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gdch/file.include/etc/cloud/cloud.cfg.d/91-gdch-system.cfg) ([`file.include`](/reference/features/#file-include)) | GDCH-specific cloud-init system configuration, including datasource and module settings. |
| [`file.include/etc/kernel/cmdline.d/00-cmdline.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gdch/file.include/etc/kernel/cmdline.d/00-cmdline.cfg) ([`file.include`](/reference/features/#file-include)) | Sets GDCH-specific kernel boot parameters. |
| [`file.include/etc/kernel/cmdline.d/10-console.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gdch/file.include/etc/kernel/cmdline.d/10-console.cfg) ([`file.include`](/reference/features/#file-include)) | Sets the kernel console parameter for the GDCH serial console. |

### Related features

**Includes:**

- [`cloud`](/reference/features/cloud) — provides common cloud-init integration and base cloud configuration shared across cloud platforms.

### Further reading

- [cloud-init documentation](https://cloudinit.readthedocs.io/)
- [chrony documentation](https://chrony-project.org/documentation.html)

## Related topics

<RelatedTopics />

