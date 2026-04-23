---
title: "Container Base Image"
description: "How to use Garden Linux full and bare (distroless-style) OCI container images as base images in Containerfiles and Dockerfiles"
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
github_source_path: docs/how-to/container-base-image/index.md
github_target_path: docs/how-to/container-base-image/index.md
---

# Use Garden Linux as a Container Base Image

Garden Linux provides two families of [Open Container Initiative (OCI)](https://opencontainers.org/) container images:

- **[Full container images](full.md)** — Standard Garden Linux with a full userland (apt, systemd, etc.)
- **[Bare container images](bare.md)** — Distroless-style images with minimal footprint, stripped of unnecessary components

[Have a look at the detailed explanation](/explanation/container-base-image.md).

## Further Reading

- [unbase_oci GitHub Repository](https://github.com/gardenlinux/unbase_oci) — Tool for creating bare container images

## Related Topics

<RelatedTopics />
