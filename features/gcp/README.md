---
title: "Feature: gcp"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/gcp/README.md
github_target_path: docs/reference/features/gcp.md
---

## Feature: gcp

### Description

A [platform](/reference/glossary.html#platform) feature that builds a Garden Linux
image for [Google Cloud Platform (GCP)](/reference/glossary#gcp). Artifacts are delivered as `.raw` files
packaged in a `.gcpimage.tar.gz` tarball for GCP import.

### What it does

Installs Google Cloud guest packages (`google-guest-agent`,
`google-compute-engine-oslogin`, `google-compute-engine`) and configures
platform-specific settings:

- **Time synchronization**: configures `systemd-timesyncd` with the GCP NTP
  endpoint (`metadata.google.internal`).
- **Timezone**: sets the default timezone to UTC.
- **SSH**: appends the Google OS Login `AuthorizedKeysCommand` directives to
  `sshd_config` to enable OS Login-based SSH key management.
- **Guest agent**: enables `google-guest-agent.service` and masks
  `google-guest-agent-manager.service`.
- **Kernel command line**: sets console and GCP-specific kernel parameters.
- **udev**: adds a rule to remove stale GCE disk symlinks.
- **Image conversion**: `convert.gcpimage.tar.gz` produces the GCP-compatible
  tarball format.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`convert.gcpimage.tar.gz`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gcp/convert.gcpimage.tar.gz) ([ref](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Packages the `.raw` artifact into a `disk.raw`-named tarball in the format expected by the GCP `gcloud compute images create` command. |
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gcp/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Sets the timezone to UTC, configures the instance configs run directory, appends Google OS Login SSH directives, enables `google-guest-agent`, and masks `google-guest-agent-manager`. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gcp/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gcp/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: platform` and included/excluded features. |
| [`pkg.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gcp/pkg.exclude) ([ref](/reference/features/#pkg-exclude)) | Prevents installation of `irqbalance` (GCP manages CPU affinity externally). |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gcp/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `google-compute-engine-oslogin`, `google-compute-engine`, and `google-guest-agent`. |
| [`file.include/etc/kernel/cmdline.d/00-cmdline.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gcp/file.include/etc/kernel/cmdline.d/00-cmdline.cfg) ([`file.include`](/reference/features/#file-include)) | Sets GCP-specific kernel boot parameters. |
| [`file.include/etc/kernel/cmdline.d/10-console.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gcp/file.include/etc/kernel/cmdline.d/10-console.cfg) ([`file.include`](/reference/features/#file-include)) | Sets the kernel console parameter for the GCP serial console. |
| [`file.include/etc/systemd/timesyncd.conf.d/00-gardenlinux-gcp.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gcp/file.include/etc/systemd/timesyncd.conf.d/00-gardenlinux-gcp.conf) ([`file.include`](/reference/features/#file-include)) | Configures `systemd-timesyncd` to use the GCP metadata NTP server. |
| [`file.include/usr/lib/udev/rules.d/64-gce-disk-removal.rules`](https://github.com/gardenlinux/gardenlinux/blob/main/features/gcp/file.include/usr/lib/udev/rules.d/64-gce-disk-removal.rules) ([`file.include`](/reference/features/#file-include)) | Removes stale GCE persistent disk symlinks when a disk is detached. |

### Related features

**Includes:**

- [`cloud`](/reference/features/cloud) — provides common cloud-init integration and base cloud configuration shared across cloud platforms.

### Further reading

- [cloud-init documentation](https://cloudinit.readthedocs.io/)
- [Google Cloud guest packages](https://github.com/GoogleCloudPlatform/guest-configs)

## Related topics

<RelatedTopics />

