---
title: "Feature: openstack"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/openstack/README.md
github_target_path: docs/reference/features/openstack.md
---

## Feature: openstack

### Description

A [platform](/reference/glossary.html#platform) feature that builds a Garden Linux
image for [OpenStack](/reference/glossary#openstack). Artifacts are delivered as `.raw`, `.qcow2`, and `.vmdk`
files.

### What it does

Assembles the OpenStack platform by composing the
[`openstackCloud`](/reference/features/openstackCloud) and
[`openstackMetal`](/reference/features/openstackMetal) elements, with
[`server`](/reference/features/server) included to enforce correct feature
ordering. The composition adapts automatically: if `metal` is present in the
build, the platform builds as an OpenStack-on-metal image; otherwise it builds
as a standard OpenStack cloud image.

Configures cloud-init for OpenStack:

- **Cloud-init**: removes `growpart`, `resizefs`, and `ntp` modules (handled
  by the initramfs and `systemd-timesyncd` respectively).
- **Datasource**: configures the OpenStack datasource for cloud-init.
- **Platform variant**: writes `GARDENLINUX_PLATFORM_VARIANT` to
  `/etc/os-release` (`vmware` or `metal`) for runtime platform detection.
- **Image conversion**: `convert.qcow2` and `convert.vmdk` produce the
  alternative image formats.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`convert.qcow2`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstack/convert.qcow2) ([ref](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Converts the `.raw` artifact to a `.qcow2` image for OpenStack Glance import. |
| [`convert.vmdk`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstack/convert.vmdk) ([ref](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Converts the `.raw` artifact to a `.vmdk` image. |
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstack/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Strips `growpart`, `resizefs`, and `ntp` from cloud-init; writes `GARDENLINUX_PLATFORM_VARIANT` to `/etc/os-release`. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstack/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstack/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: platform` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstack/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `cloud-init`, `dmidecode`, and `python3-cffi-backend`. |
| [`file.include/etc/cloud/ds-identify.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstack/file.include/etc/cloud/ds-identify.cfg) ([`file.include`](/reference/features/#file-include)) | Configures `ds-identify` to select the correct cloud-init datasource for OpenStack. |
| [`file.include/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstack/file.include/etc/cloud/cloud.cfg.d/01_debian-cloud.cfg) ([`file.include`](/reference/features/#file-include)) | Debian-specific cloud-init configuration baseline. |
| [`file.include/etc/cloud/cloud.cfg.d/50-datasource.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/openstack/file.include/etc/cloud/cloud.cfg.d/50-datasource.cfg) ([`file.include`](/reference/features/#file-include)) | Restricts cloud-init datasource detection to OpenStack. |

### Related features

**Includes:**

- [`openstackCloud`](/reference/features/openstackCloud) — provides OpenStack cloud-specific configuration (cloud-init, networking).
- [`openstackMetal`](/reference/features/openstackMetal) — provides OpenStack on-metal configuration when combined with the `metal` element.
- [`server`](/reference/features/server) — included to enforce correct feature sort order in the build.

### Further reading

- [cloud-init OpenStack datasource](https://cloudinit.readthedocs.io/en/latest/reference/datasources/openstack.html)

## Related topics

<RelatedTopics />

