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

## What Are Flavors?

Garden Linux's flavor system solves a fundamental challenge: how to create dozens of specialized operating system images for different platforms, architectures, and use cases without creating a maintainability nightmare. At its core, a flavor is not a standalone definition, but a **composition** of smaller, reusable components called features.

Imagine needing to create images for:

- AWS, Azure, GCP, OpenStack, BareMetal ... platforms
- Each with amd64 and arm64 architectures
- Some with TPM2 and/or SecureBoot features
- Most for the Gardener/Kubernetes use case
- Some for different use cases

The combinatorial explosion of possibilities would be impossible to manage if each image variant required a complete, independent definition. The flavor system addresses this by separating concerns:

1. **[Platform features](/explanation/features#feature-types)** - The deployment target (e.g., [`aws`](/reference/features/aws), [`azure`](/reference/features/azure), [`baremetal`](/reference/features/baremetal))
2. **[Element features](/explanation/features#feature-types)** - Functional components (e.g., [`gardener`](/reference/features/gardener), [`cis`](/reference/features/cis))
3. **[Flag features](/explanation/features#feature-types)** - Lightweight modifiers (e.g., [`_prod`](/reference/features/_prod), [`_fips`](/reference/features/_fips), [`_usi`](/reference/features/_usi))

This compositional approach allows Garden Linux to generate many unique flavor variants from the simple YAML definitions in [`flavors.yaml`](/reference/flavors.md).

## The Composition Philosophy

The flavor system embodies Garden Linux's customizable design philosophy. Instead of creating separate, hand-crafted images for each use case, we compose images from standardized building blocks.

Features are the primary building blocks of flavors. Each feature is a complete configuration unit that may include packages, configuration files, scripts, and dependencies on other features. Features combine through a directed acyclic graph (DAG) to form the complete image definition.

For a detailed explanation of feature types, the DAG resolution process, and the single-platform enforcement rule, see [Features](/explanation/features).

:::tip
A complete list of features can be seen in the [Features Reference](/reference/features/).
:::

:::tip
For an explanation of how boot-related features interact, see
[Boot Modes](/explanation/boot-modes) and
[Secure Boot and Trusted Boot](/explanation/secure-boot).
:::

## The Publication Pipeline

The flavor system not only defines what to build, but also manages the journey from development to production through the build/test/publish triad.

### Selective Publication

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

### From Build to Publish

The publication pipeline follows a staged maturity model:

1. **Build**: Create the image from feature components
2. **Test**: Run validation suites across platforms (chroot, qemu, cloud)
3. **Publish**: Distribute to public channels (S3, GHCR, GitHub)

Each stage acts as a gate. A flavor might have `build: true` but `test: false` during initial development. Once tests pass reliably, it can progress to `test: true` and eventually `publish: true`.

### Naming and Identification

As flavors progress through the pipeline, each build is identified by a four-level naming hierarchy: **cname** (canonical name encoding just the feature set), **flavor** (cname plus architecture), **versioned flavor** (flavor plus version), and **artifact base name** (versioned flavor plus commit hash).

For the complete specification of this naming hierarchy including encoding rules and worked examples, see the [canonical names section in the Flavors Reference](/reference/flavors#canonical-names).

## Integration Points

The flavor system integrates with several other components in the Garden Linux ecosystem:

The `gl-flavors-parse` command-line tool parses [`flavors.yaml`](/reference/flavors.md) and generates filtered output matrices. For full command details and flags, see the [Flavors Configuration Reference](/reference/flavors.md#gl-flavors-parse-tool).

## Related Topics

<RelatedTopics />
