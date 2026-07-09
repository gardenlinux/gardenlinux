---
title: Flavors
description: Conceptual explanation of Garden Linux's flavor system and its role in image creation
order: 120
related_topics:
  - /explanation/os-releases.md
  - /reference/flavors.md
  - /explanation/release-hierarchy.md
  - /reference/flavor-matrix.md
  - /explanation/github-workflows.md
migration_status: "done"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4600"
migration_stakeholder: "@tmangold, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/explanation/flavors.md
github_target_path: docs/explanation/flavors.md
---

# Flavors

## What are flavors?

Garden Linux's flavor system solves a fundamental challenge: how to create dozens of specialized operating system images for different platforms, architectures, and use cases without creating a maintainability nightmare. At its core, a flavor is not a standalone definition, but a **composition** of smaller, reusable components called features.

Imagine needing to create images for:

- AWS, Azure, GCP, OpenStack, BareMetal ... platforms
- Each with amd64 and arm64 architectures
- Some with TPM2 and/or SecureBoot features
- Most for the Gardener/Kubernetes use case
- Some for different use cases

The combinatorial explosion of possibilities would be impossible to manage if each image variant required a complete, independent definition. The flavor system addresses this by separating concerns into three dimensions:

1. **[Target](#target-abstraction)** - The platform or environment (e.g., aws, azure, baremetal)
2. **[Features](#feature-based-design)** - Capabilities and configurations (e.g., gardener, \_prod, \_usi)

This compositional approach allows Garden Linux to generate many unique flavor variants from the simple YAML definitions in [`flavors.yaml`](/reference/flavors.md).

## The composition philosophy

The flavor system embodies Garden Linux's customizable design philosophy. Instead of creating separate, hand-crafted images for each use case, we compose images from standardized building blocks.

### Feature-based design

Features are the primary building blocks. -python`(Python),`bare-nodejs`(Node.js),
  and`bare-sapmachine` (Java/SAP). These images have a minimal footprint and
attack surface, omitting shells and package managers by design.
A feature is not just a package list, but a complete configuration unit that may include:

- **Packages** - APT packages to install
- **Configuration files** - System configuration with appropriate defaults
- **Scripts** - Setup and lifecycle scripts
- **Dependencies** - A list of other Features to include/exclude

For example, the `gardener` feature doesn't just install `containerd` it also configures systemd services and includes other features as `log` to set up logging.

:::tip
A complete list of features can be seen in the [Features Reference](/reference/features/).
:::

:::tip
For an explanation of how boot-related features interact, see
[Boot Modes](/explanation/boot-modes) and
[Secure Boot and Trusted Boot](/explanation/secure-boot).
:::

### Target abstraction

Targets represent deployment platforms, but they're designed to minimize duplication. The `aws` target doesn't copy-paste all cloud-related configuration - it inherits base `cloud` configuration and adds AWS-specific elements like EC2 instance metadata handling and other AWS-specific settings-python`(Python),`bare-nodejs`(Node.js),
  and`bare-sapmachine` (Java/SAP). These images have a minimal footprint and
attack surface, omitting shells and package managers by design.
.

This hierarchical inheritance allows the flavor system to:

- **Promote consistency** - Common cloud configurations are shared
- **Reduce errors** - Changes to base cloud configuration propagate to all platforms
- **Simplify maintenance** - Platform-specific issues are isolated

:::info Single platform enforcement
Each Garden Linux build enforces exactly one platform feature by default.
Specifying zero or multiple platforms causes the build to fail, preventing
silent misconfigurations where multiple platforms could produce unpublished or
broken images. See
[ADR 0020](/reference/adr/0020-enforce-single-platform-by-default-in-builder)
for the rationale and the opt-in override flag.
:::

## The publication pipeline

The flavor system not only defines what to build, but also manages the journey from development to production through the build/test/publish triad.

### Selective publication

Not all built flavors are published to end users. The `publish` flag in [`flavors.yaml`](/reference/flavors.md) controls distribution:

```yaml
- features:
    - gardener
    - _prod
  arch: amd64
  build: true
  test: true
  test-platform: true
  publish: true
```

This separation enables several important workflows:

- **Internal testing** of new configurations before public release
- **Restricted use** of compliance images that have licensing constraints
- **Gradual rollout** of stable images to production
- **Rapid iteration** on experimental features without affecting users

:::tip
More information can be looked up in the [Flavors Configuration Reference](/reference/flavors.md)
:::

### From build to publish

The publication pipeline follows a staged maturity model:

1. **Build**: Create the image from feature components
2. **Test**: Run validation suites across platforms (chroot, qemu, cloud)
3. **Publish**: Distribute to public channels (S3, GHCR, GitHub)

Each stage acts as a gate. A flavor might have `build: true` but `test: false` during initial development. Once tests pass reliably, it can progress to `test: true` and eventually `publish: true`.

### The CNAME system

As flavors progress through the pipeline, they receive a canonical name (CNAME) that uniquely identifies them. The CNAME format `{target}-{features}-{arch}-{version}-{commit}` serves several critical functions:

- **Unique identification**: No two artifacts have the same name
- **Traceability**: The CNAME contains all information needed to reproduce the build
- **Automation**: CI/CD pipelines can programmatically reference specific image variants
- **Distribution**: S3 paths and container tags are derived from the CNAME

:::info Feature name concatenation in the CNAME
Regular features are joined to the target and to each other with `-`. Features whose names begin with `_` are appended directly, without a preceding `-`.

For example, `aws-gardener_prod_fips` is composed of:

- `aws` — the target
- `gardener` — joined with `-` → `aws-gardener`
- `_prod` — appended directly (no `-`) → `aws-gardener_prod`
- `_fips` — appended directly (no `-`) → `aws-gardener_prod_fips`
  :::

The CNAME system ensures that what was tested is exactly what gets deployed.

## Integration points

The flavor system integrates with several other components in the Garden Linux ecosystem:

### gl-flavors-parse tool

The `gl-flavors-parse` command-line tool parses [`flavors.yaml`](/reference/flavors.md) and generates filtered output matrices. It's details can be looked up in the [Python Library Command-lin Interface](/reference/python-gardenlinux-lib-cli)

```bash
# Generate build matrix for publishable flavors
gl-flavors-parse --publish --json-by-arch
```

This parsing step transforms the static configuration into a dynamic build plan.

## Related topics

<RelatedTopics />
