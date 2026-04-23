---
title: "Container Images"
description: "Complete table of Garden Linux OCI Container Images"
related_topics:
  - /how-to/container-base-image/bare.md
  - /how-to/container-base-image/full.md
  - /reference/container-images.md
migration_status: "done"
migration_source: "01_developers/bare_container.md"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4626"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/reference/container-images.md
github_target_path: docs/reference/container-images.md
editLink: false
---

# Container Images

The following tables lists all Garden Linux OCI Container Images.

## Full Container Images

Garden Linux publishes two image streams for full Container Images to the GitHub Container Registry:

| Image Stream | Use Case                   | URI                                         |
| ------------ | -------------------------- | ------------------------------------------- |
| Release      | Stable, versioned releases | `ghcr.io/gardenlinux/gardenlinux:<version>` |
| Nightly      | Latest development builds  | `ghcr.io/gardenlinux/nightly:<version>`     |

For production use, prefer release images with a specific version tag:

```bash
GL_VERSION="2150.0.0"
GL_IMAGE="ghcr.io/gardenlinux/gardenlinux:${GL_VERSION}"
```

For testing or development, use the nightly stream:

```bash
GL_IMAGE="ghcr.io/gardenlinux/nightly:latest"
```

:::tip
For a complete list of maintained releases and their support lifecycle, see the [releases reference](../reference/releases/index.md).
:::

## Bare Container Images

Garden Linux offers a range of specialized bare container images, each tailored for specific applications and designed for minimalism and security.

These containers are optimized as base images for Dockerfiles.
Their development is streamlined by the [unbase_oci](https://github.com/gardenlinux/unbase_oci) tool, which efficiently minimizes image size by removing unnecessary components from base container images.

| Image             | Description                                                       | URI                                                         |
| ----------------- | ----------------------------------------------------------------- | ----------------------------------------------------------- |
| `bare-libc`       | C runtime (libc6, zoneinfo) — for C/C++ applications              | `ghcr.io/gardenlinux/gardenlinux/bare-libc:<version>`       |
| `bare-python`     | Python runtime — for Python applications                          | `ghcr.io/gardenlinux/gardenlinux/bare-python:<version>`     |
| `bare-nodejs`     | Node.js runtime — for JavaScript applications                     | `ghcr.io/gardenlinux/gardenlinux/bare-nodejs:<version>`     |
| `bare-sapmachine` | SAPMachine JDK (Java Development Kit) — for Java/SAP applications | `ghcr.io/gardenlinux/gardenlinux/bare-sapmachine:<version>` |

### Unbase OCI Tool

The `unbase_oci` tool is instrumental in the development of these "bare" container images.

- **Functionality**:
  - Strips unnecessary components from base container images.
  - Reduces image size and potential security vulnerabilities.
  - Operates on OCI archives, comparing base and target images to identify and retain only necessary additions and their dependencies.
- **Repository Link**: [unbase_oci](https://github.com/gardenlinux/unbase_oci)
- **Impact**: This tool is pivotal in creating streamlined, "distroless-like" images, ensuring that the resulting containers are lean and secure.
