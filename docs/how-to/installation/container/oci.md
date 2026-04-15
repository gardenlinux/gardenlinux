---
title: "OCI Platform"
description: "Garden Linux OCI container images: building, publishing, and platform-specific configurations"
category: "how-to"
tags: ["how-to", "oci", "container", "platform"]
migration_status: "new"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4623"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/installation/container/oci.md
github_target_path: docs/how-to/installation/container/oci.md
---

# OCI Platform

Garden Linux provides Open Container Initiative (OCI) compliant container images. This page covers the platform-specific build process and references the comprehensive base image guide.

## OCI Image Build Process

Garden Linux uses the `features/container` feature to produce OCI images:

- **Build output**: `.tar.gz` archive in `docker-archive` format, compatible with Docker and Podman
- **Default command**: `/bin/bash`
- **OCI metadata**: Image is tagged with title, version, architecture, source, revision, and description

For details on the build mechanism, see `features/container/README.md` and `features/container/image.oci` in the repository.

## Using Garden Linux as a Base Image

For comprehensive documentation on using Garden Linux container images as base images in your own Containerfiles and Dockerfiles — including both full and bare (distroless-style) images — see the dedicated guide:

**[Container Base Image](/how-to/container-base-image.md)**

This guide covers:

- Full container base images (using `ghcr.io/gardenlinux/gardenlinux:<version>`)
- Bare container images (bare-libc, bare-python, bare-nodejs, bare-sapmachine)
- Multi-stage build patterns for adding dependencies
- Debugging bare containers

## Further Reading

- [Use Garden Linux as a Container Base Image](/how-to/container-base-image.md)
