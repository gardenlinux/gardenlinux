---
title: "Getting Images"
description: "How to obtain pre-built Garden Linux images"
order: 3
related_topics:
  - /how-to/choosing-flavors
  - /explanation/flavors
  - /reference/flavor-matrix
  - /reference/releases/maintained-releases
  - /how-to/building-images
migration_status: "done"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4625"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/getting-images.md
github_target_path: docs/how-to/getting-images.md
---



# Getting Images

Once you have [chosen a flavor](/how-to/choosing-flavors), you need to obtain
the image. Garden Linux provides pre-built images via GitHub Releases, cloud
provider integrations, and the GitHub Container Registry (GHCR). If no
pre-built [flavor](/explanation/flavors) meets your requirements, you can also
build your own.

## Official Images

All Garden Linux [flavors](/explanation/flavors) are published as `.tar.xz`
archives on the
[GitHub Releases page](https://github.com/gardenlinux/gardenlinux/releases).
This is the primary method for obtaining images for all
platforms, including cloud, virtualization, bare-metal, and local development.

Each release contains:

- Compressed tarballs with platform-specific VM disk images (`.raw`, `.vhd`, `.qcow2`,
  `.gcpimage.tar.gz`)
- A "Published Images" section listing cloud-native references (AMI IDs,
  Community Gallery URNs, GCP image names) where applicable

### Downloading from GitHub Releases

Use the following script as a starting point for any platform. Set
`GL_FLAVOR` to the [flavor](/explanation/flavors) name — look it up in the
[Flavor Matrix](/reference/flavor-matrix) if you are unsure of the exact name.

```bash
GL_VERSION="<version>"   # e.g. 2150.0.0
GL_COMMIT="<commit>"     # e.g. eb8696b9 (from the release page)
GL_ARCH="amd64"          # or arm64
GL_FLAVOR="<flavor>"     # e.g. aws-gardener_prod, kvm-gardener_prod

GL_ASSET="${GL_FLAVOR}-${GL_ARCH}-${GL_VERSION}-${GL_COMMIT}"
GL_TAR_XZ="${GL_ASSET}.tar.xz"

curl -L -o "${GL_TAR_XZ}" \
  "https://github.com/gardenlinux/gardenlinux/releases/download/${GL_VERSION}/${GL_TAR_XZ}"

tar -xf "${GL_TAR_XZ}"
```

:::tip
The commit hash (`GL_COMMIT`) for a release is listed in the "Assets" section
on the [GitHub Releases page](https://github.com/gardenlinux/gardenlinux/releases)
as part of each asset filename.
For a complete list of maintained releases and their support lifecycle, see the
[releases reference](/reference/releases/).
:::

### Image Formats by Platform

Each platform target produces a different image format:

| Platform                                     | Image Format      | File Extension     |
| -------------------------------------------- | ----------------- | ------------------ |
| [`aws`](/reference/features/aws)             | Raw disk image    | `.raw`             |
| [`azure`](/reference/features/azure)         | Virtual Hard Disk | `.vhd`             |
| [`gcp`](/reference/features/gcp)             | GCP image tarball | `.gcpimage.tar.gz` |
| [`openstack`](/reference/features/openstack) | QCOW2 disk image  | `.qcow2`           |
| [`kvm`](/reference/features/kvm)             | Raw disk image    | `.raw`             |
| [`baremetal`](/reference/features/baremetal) | Raw disk image    | `.raw`             |
| [`vmware`](/reference/features/vmware)       | Raw disk image    | `.raw`             |

### Platform-Specific Tutorials

For complete step-by-step instructions on downloading and deploying images,
including cloud infrastructure setup and first-boot configuration, see:

- [First Boot on AWS](/tutorials/cloud/first-boot-aws) — download and import
  as AMI
- [First Boot on Azure](/tutorials/cloud/first-boot-azure) — download and
  upload to Azure Blob Storage
- [First Boot on GCP](/tutorials/cloud/first-boot-gcp) — download and upload
  to Google Cloud Storage
- [First Boot on OpenStack](/tutorials/cloud/first-boot-openstack) — download
  and upload to Glance
- [First Boot on KVM](/tutorials/local/first-boot-kvm) — download and run
  with QEMU/KVM
- [First Boot on Bare Metal](/tutorials/on-premises/first-boot-bare-metal) —
  download and write to disk with `dd`

## Cloud Provider Marketplaces

:::warning
[Publishing official Garden Linux images in cloud provider marketplaces](https://github.com/gardenlinux/gardenlinux/issues/4592)
is currently being worked on. Until this is ready — if you do not have access
to the images listed below — use the
[Official Images](#official-images) method above.
:::

Where available, Garden Linux publishes images directly to cloud provider
shared image galleries. These identifiers are listed in the "Published Images"
section of each release on the
[GitHub Releases page](https://github.com/gardenlinux/gardenlinux/releases).

| Provider                             | Mechanism                 | Identifier Format                                                           |
| ------------------------------------ | ------------------------- | --------------------------------------------------------------------------- |
| [`aws`](/reference/features/aws)     | Published AMIs per region | `ami-<id>`                                                                  |
| [`azure`](/reference/features/azure) | Azure Community Gallery   | `/CommunityGalleries/gardenlinux-<uuid>/Images/<flavor>/Versions/<version>` |
| [`gcp`](/reference/features/gcp)     | Shared GCP project        | `projects/sap-se-gcp-gardenlinux/global/images/<image-name>`                |

## Container Images

Garden Linux OCI container images are published to the
[GitHub Container Registry](https://github.com/gardenlinux/gardenlinux/pkgs/container/gardenlinux).

```bash
# Pull a versioned release image
podman pull ghcr.io/gardenlinux/gardenlinux:<version>

# Pull the latest nightly image
podman pull ghcr.io/gardenlinux/gardenlinux:nightly
```

:::tip
Replace `podman` with `docker` if you use Docker — the commands are
interchangeable.
:::

For distroless (`bare-*`) variants, see the
[Container Base Image](/how-to/container-base-image/) how-to guides.

For a complete walkthrough, see
[First Boot as OCI Image](/tutorials/container/first-boot-oci).

## Build Your Own Images

If no pre-built [flavor](/explanation/flavors) matches your requirements, or
you need a custom feature combination, build your own image:

- [Building Images](/how-to/building-images) — full build guide for any
  platform and feature combination
- [Create a custom Feature](/how-to/custom-feature) — extend Garden Linux
  with your own features

## Related Topics

<RelatedTopics />
