---
title: Flavors Configuration Reference
description: Authoritative reference for all fields and syntax in flavors.yaml
related_topics:
  - /explanation/flavors.md
  - /explanation/os-releases.md
  - /reference/flavor-matrix.md
migration_status: "done"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4600"
migration_stakeholder: "@tmangold, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/reference/flavors.md
github_target_path: docs/reference/flavors.md
---

# Flavors Configuration Reference

This document provides complete, authoritative reference for the `flavors.yaml` file format used in Garden Linux builds.

## File Structure

The complete schema is organized hierarchically:

```yaml
targets:
  - name: string
    category: enum
    flavors: array
```

## Target Object

Each target defines a platform or environment for Garden Linux images. A target
entry is typically named after — and expected to include — a single
[`platform` feature](/reference/flavors#canonical-names) per the
single-platform rule in [ADR 0034](/reference/adr/0034-feature-terminology)
§2.1: every resolved flavor must contain exactly one platform feature.

### Fields

**name** (string, required)
: The identifier for this target. Used in [canonical name (cname) generation](/reference/flavors#canonical-names), workflow steps, and artifact naming.

**category** (enum, required)
: Organizational category for the target. One of:`

- `public-cloud` - Major cloud providers
- `container` - Container base images
- `baremetal` - Physical server deployments
- `hypervisor` - Virtualization platforms

**[flavors](/reference/flavors.md)** (array, required)
: Array of flavor configurations for this target

### Target List

All available targets are listed below:

| Name                                         | Category     | Platform                        |
| -------------------------------------------- | ------------ | ------------------------------- |
| [`ali`](/reference/features/ali)             | public-cloud | Alibaba Cloud                   |
| [`aws`](/reference/features/aws)             | public-cloud | Amazon Web Services             |
| [`azure`](/reference/features/azure)         | public-cloud | Microsoft Azure                 |
| [`bare`](/reference/features/bare)           | container    | Bare container base             |
| [`container`](/reference/features/container) | container    | Full container base             |
| [`gcp`](/reference/features/gcp)             | public-cloud | Google Cloud Platform           |
| [`gdch`](/reference/features/gdch)           | public-cloud | Google Distributed Cloud Hosted |
| [`kvm`](/reference/features/kvm)             | hypervisor   | KVM virtualization              |
| [`baremetal`](/reference/features/baremetal) | baremetal    | Bare metal deployment           |
| [`openstack`](/reference/features/openstack) | public-cloud | OpenStack integration           |
| [`vmware`](/reference/features/vmware)       | hypervisor   | VMware virtualization           |
| [`lima`](/reference/features/lima)           | hypervisor   | Lima for macOS                  |

## Flavor Object

Each flavor defines a specific image variant for its target.

### Fields

**features** (array of strings, required, non-empty)
: Feature identifiers to include in this flavor. Features combine to define image capabilities.

**arch** (enum, required)
: CPU architecture. One of:

- `amd64`
- `arm64`

**build** (boolean, required)
: Whether to include this flavor in the build pipeline.

- `true`: Build the image
- `false`: Skip building

**test** (boolean, required)
: Whether to run automated tests on this image.

- `true`: Execute test suite (chroot, qemu, oci)
- `false`: Skip testing

**test-platform** (boolean, required)
: Whether to run automated cloud platform tests on this image.

- `true`: Execute test suite (cloud)
- `false`: Not used as test platform

**publish** (boolean, required)
: Whether to distribute this flavor publicly.

- `true`: Publish to S3, GHCR, GitHub releases
- `false`: Build and test only, do not distribute

:::info
Flavors with `publish: false` are still available as GitHub workflow artifacts for internal testing.
:::

## Canonical Names

Each Garden Linux build is identified by a four-level naming hierarchy defined in [ADR 0035](/reference/adr/0035-cname-flavor-artifact-naming):

| Term                   | Format                                    | Example                                    |
| ---------------------- | ----------------------------------------- | ------------------------------------------ |
| **cname**              | `{feature-encoding}`                      | `aws-gardener_prod`                        |
| **flavor**             | `{cname}-{arch}`                          | `aws-gardener_prod-amd64`                  |
| **versioned flavor**   | `{cname}-{arch}-{version}`                | `aws-gardener_prod-amd64-2150.1.0`         |
| **artifact base name** | `{cname}-{arch}-{version}-{short_commit}` | `aws-gardener_prod-amd64-2150.1.0-abc1234` |

**cname** (canonical name) encodes only the feature set — no architecture, version, or commit. It is the minimal, canonically-sorted representation of the features selected for a build.

**flavor** qualifies the cname with a target architecture. This is the stable identifier used in `flavors.yaml` entries, CI job naming, and as the argument to the `./build` script.

**versioned flavor** qualifies the flavor with a version. The version is never passed on the `./build` command line — it is resolved internally from the `VERSION` file via `./get_version`.

**artifact base name** qualifies the versioned flavor with a short commit hash. It is the prefix of every file produced under `.build/` and the key used for S3 artifact storage.

:::info Feature name encoding in the cname
Features are concatenated with `-` as separator. Flag features (whose names begin with `_`) are joined directly to the preceding component without a leading `-`.

For example, `aws-gardener_prod_fips` is assembled from:

- [`aws`](/reference/features/aws) — the platform feature
- [`gardener`](/reference/features/gardener) — an element, joined with `-` → `aws-gardener`
- [`_prod`](/reference/features/_prod) — a flag, appended directly (no `-`) → `aws-gardener_prod`
- [`_fips`](/reference/features/_fips) — a flag, appended directly (no `-`) → `aws-gardener_prod_fips`
  :::

**Worked example** for [`aws`](/reference/features/aws) (platform), [`gardener`](/reference/features/gardener) (element), [`_prod`](/reference/features/_prod) (flag) features on `amd64` at version `2150.1.0` with commit `abc1234`:

1. **cname** = `aws-gardener_prod` (feature encoding only)
1. **flavor** = `aws-gardener_prod-amd64` (cname + arch)
1. **versioned flavor** = `aws-gardener_prod-amd64-2150.1.0` (flavor + version; resolved internally by `./build`)
1. **artifact base name** = `aws-gardener_prod-amd64-2150.1.0-abc1234` (versioned flavor + short commit; prefix for all output files)

:::info `today` as a version
The version is never specified on the `./build` command line. It is read from the `VERSION` file in the repository root via `./get_version`. On `main`, `VERSION` contains `today`, so the literal string `today` is used as the version. On a release branch, `VERSION` contains the full semver for that branch (e.g. `2150.5.0`), and `get_version` returns it as-is. Builds with version `today` are development builds and are not intended for distribution.
:::

For the authoritative specification of cname construction, sorting, and minimisation, see [ADR 0035](/reference/adr/0035-cname-flavor-artifact-naming). For the feature type definitions (`platform`, `element`, `flag`) see [ADR 0034](/reference/adr/0034-feature-terminology).

## gl-flavors-parse Tool

The `gl-flavors-parse` command-line tool parses flavors.yaml and generates filtered output matrices. It's details can be looked up in the [Python Library Command-line Interface](/reference/python-gardenlinux-lib-cli)

```bash
# Generate build matrix for publishable flavors
gl-flavors-parse --publish --json-by-arch
```

## Related Topics

<RelatedTopics />
