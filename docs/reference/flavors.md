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

Each target defines a platform or environment for Garden Linux images.

### Fields

**name** (string, required)
: The identifier for this target. Used in [CNAME generation](/explanation/flavors.md#the-cname-system), workflow steps, and artifact naming.

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

## Feature List

A complete list of all available features can be looked up in the [Features Reference](/reference/features)

## gl-flavors-parse Tool

The `gl-flavors-parse` command-line tool parses flavors.yaml and generates filtered output matrices. It's details can be looked up in the [Python Library Command-lin Interface](/reference/python-gardenlinux-lib-cli)

```bash
# Generate build matrix for publishable flavors
gl-flavors-parse --publish --json-by-arch
```

## Related Topics

<RelatedTopics />
