---
title: "Container Base Image"
description: "Understanding Garden Linux full and bare (distroless-style) OCI container images"
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
github_source_path: docs/explanation/container-base-image.md
github_target_path: docs/explanation/container-base-image.md
---

# Container Base Image

Garden Linux provides two families of [Open Container Initiative (OCI)](/reference/glossary.html#oci-oci-image-format) container images designed for different use cases in containerized environments. Understanding the differences between these image types helps you select the most appropriate foundation for your applications based on your requirements for functionality, size, and security.

## Full Container Images

Full container images provide a complete Debian-based Linux environment with access to the APT package manager, systemd init system, and common utilities.

These images are suitable for applications that require:

- Package installation and management at build or runtime
- Full Linux distribution compatibility
- Access to system services and daemons
- Extensive tooling for debugging and development

:::warning
While offering maximum compatibility, full images have a larger footprint and potentially larger attack surface due to the inclusion of package managers and shells.
:::

## Bare Container Images (Distroless-style)

Bare container images follow a distroless approach, containing only the specific runtime and its direct dependencies required to run an application. The [Garden Linux Container Image Reference](/reference/container-images.md#full-container-images) lists several specialized bare image variants.

These images provide significant benefits:

- Minimal footprint leading to faster pull times and lower storage usage
- Reduced attack surface by omitting shells, package managers, and unnecessary utilities
- Improved security through minimization
- Consistent, reproducible builds

:::info
By design, bare images intentionally exclude components like shells (`sh`, `bash`) and package managers (`apt`, `pip`, `npm`) to enforce dependency containment and minimize potential vulnerabilities.
:::

## Choosing Between Full and Bare Images

Select full container images when your application requires:

- Runtime package installation or updates
- Access to system utilities for maintenance or debugging
- Compatibility with software expecting a full Linux distribution
- Development environments where build-time flexibility is needed

Choose bare container images when:

- Deploying compiled applications or applications with pre-resolved dependencies
- Minimizing image size and attack surface is a priority
- Running in security-sensitive environments
- Using multi-stage builds to separate build-time dependencies from runtime

The decision ultimately depends on balancing your application's functional requirements against operational considerations like size, security, and maintenance overhead.

## The unbase_oci Tool

Garden Linux bare images are created using the [`unbase_oci`](https://github.com/gardenlinux/unbase_oci) tool, which analyzes container images to identify and retain only the files necessary for specific runtime environments. This tool:

- Compares base images with application-specific builds
- Identifies and preserves only required files and their dependencies
- Removes unnecessary components like documentation, shells, and package managers
- Enables the creation of truly minimal, purpose-built container images

The unbase_oci process results in images that contain exactly what an application needs to run—nothing more, nothing less—achieving the distroless ideal while maintaining compatibility with Garden Linux's security and reliability standards.

## Best Practices

When using Garden Linux container base images:

- Match the image variant to your application's language/runtime requirements
- Leverage multi-stage builds when using bare images to handle build-time dependencies
- Regularly update to newer image versions to include security patches
- Consider your deployment context: development vs. production environments may warrant different image choices
- Consult the [Container Images reference](/reference/container-images.md) for specific image variants and tags
- Refer to the [how-to guides](/how-to/container-base-image/index.md) for detailed usage examples

By understanding the conceptual differences between Garden Linux's container image offerings, you can make informed decisions that optimize your containerized applications for size, security, and operational efficiency.

## Further Reading

- [unbase_oci GitHub Repository](https://github.com/gardenlinux/unbase_oci) — Tool for creating bare container images

## Related Topics

<RelatedTopics />
