---
title: "Feature: container"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/container/README.md
github_target_path: docs/reference/features/container.md
---

## Feature: container

### Description

A [platform](/reference/glossary.html#platform) feature that builds a Garden Linux
container image compatible with [Docker](/reference/glossary#docker) and [Podman](/reference/glossary#podman). The artifact is delivered as
an [OCI image](/reference/glossary#oci-oci-image-format) tarball.

### What it does

Produces an OCI-compatible container image via `image.oci`. The image is a
minimal base image built on top of the [`base`](/reference/features/base) and
[`_archgrouped`](/reference/features/_archgrouped) elements, with package
management utilities and daemon services excluded that are not needed in a
container environment.

Custom images built with this feature can be loaded directly into a container
runtime:

```bash
podman load -i container-amd64-today-local.container.tar.gz
# or
docker load -i container-amd64-today-local.container.tar.gz

```

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`image.oci`](https://github.com/gardenlinux/gardenlinux/blob/main/features/container/image.oci) ([ref](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Builds an OCI image tarball from the rootfs, packaging it with the correct OCI manifest and config layers. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/container/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: platform` and included/excluded features. |
| [`pkg.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/container/pkg.exclude) ([ref](/reference/features/#pkg-exclude)) | Prevents installation of `garden-repo-manager` and `rng-tools` (not needed in containers). |

### Related features

**Includes:**

- [`base`](/reference/features/base) — provides the minimal Garden Linux base system.
- [`_archgrouped`](/reference/features/_archgrouped) — groups architecture-specific package selections for the container build.

## Related topics

<RelatedTopics />

