---
title: "Full Container Base Images"
description: "How to use Garden Linux full OCI container images as base images in Containerfiles and Dockerfiles"
related_topics:
  - /explanation/container-base-image.md
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
github_source_path: docs/how-to/container-base-image/full.md
github_target_path: docs/how-to/container-base-image/full.md
---

# Full Container Base Images

The full Garden Linux container images provide a complete Linux environment with package manager access.

## Prerequisites

Before starting, you'll need:

- A container runtime: [Podman](https://podman.io/docs/installation) or [Docker](https://docs.docker.com/get-docker/)
- Familiarity with `Containerfile` or `Dockerfile` syntax
- For bare images with pip/npm dependencies: basic understanding of [multi-stage builds](https://docs.docker.com/build/building/multi-stage/)

:::tip
This guide uses `podman` commands throughout. If you use Docker, replace `podman` with `docker` — the commands are interchangeable.
:::

## Choosing a Version

Choose a version by [looking at the Garden Linux Container Image Reference](/reference/container-images.md#full-container-images).

## Basic Containerfile Example

Use the full Garden Linux container as a base for applications that need a standard Linux environment:

```dockerfile
FROM ghcr.io/gardenlinux/gardenlinux:2150.0.0

# Install additional packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html /var/www/html/

# Set runtime configuration
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Installing Additional Packages

The full container image includes `apt`, allowing you to install packages at build time:

```dockerfile
FROM ghcr.io/gardenlinux/gardenlinux:2150.0.0

RUN apt-get update && apt-get install -y --no-install-recommends \
    <your-packages> \
    && rm -rf /var/lib/apt/lists/*
```

:::warning
Always include `rm -rf /var/lib/apt/lists/*` at the end of `apt-get` commands to reduce image size.
:::

## Further Reading

- [unbase_oci GitHub Repository](https://github.com/gardenlinux/unbase_oci) — Tool for creating bare container images

## Related Topics

<RelatedTopics />
