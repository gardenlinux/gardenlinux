---
title: "Choosing Flavors"
description: "How to select the right Garden Linux flavor for your workload"
order: 2
category: "how-to"
tags:
  - "flavors"
  - "use-cases"
  - "getting-started"
related_topics:
  - /explanation/use-cases
  - /explanation/flavors
  - /reference/flavor-matrix
  - /reference/flavors
  - /how-to/building-images
  - /how-to/getting-images
migration_status: "new"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4624"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/choosing-flavors.md
github_target_path: docs/how-to/choosing-flavors.md
---

# Choosing Flavors

A Garden Linux [flavor](/explanation/flavors) is a pre-composed combination of
a **platform target** (e.g. `aws`, `baremetal`) and one or more **features**
(e.g. `gardener`, `_prod`, `_fips`). The flavor name encodes both:
`<platform>-<feature1>_<feature2>` (e.g. `aws-gardener_prod`).

This guide walks you through selecting the right flavor in four steps. For
background on how flavors work, see [Flavors](/explanation/flavors). For the
complete list of all published flavors, see the
[Flavor Matrix](/reference/flavor-matrix).

## Step 1: Identify Your Use Case

Determine which of the primary Garden Linux use cases matches your workload.
Each use case maps to a specific feature set.

| Use Case                                             | Key Features                                                                     | Go To                                                                                               |
| ---------------------------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Gardener-managed Kubernetes nodes                    | [`gardener`](/reference/features/gardener), [`_prod`](/reference/features/_prod) | [Gardener Kubernetes Nodes](/explanation/use-cases#gardener-kubernetes-nodes)                       |
| Bare-metal Gardener nodes via IronCore (Cluster API) | [`capi`](/reference/features/capi)                                               | [Bare-Metal via IronCore](/explanation/use-cases#bare-metal-gardener-kubernetes-nodes-via-ironcore) |
| Vanilla (non-Gardener) Kubernetes nodes              | [`khost`](/reference/features/khost)                                             | [Vanilla Kubernetes Nodes](/explanation/use-cases#vanilla-kubernetes-nodes)                         |
| OCI container base image                             | [`container`](/reference/features/container) or `bare-*`                         | [Container Base Images](/explanation/use-cases#container-base-images)                               |
| KVM/libvirt virtualization host                      | [`vhost`](/reference/features/vhost)                                             | [Virtualization Host](/explanation/use-cases#virtualization-host)                                   |

If no existing use case matches, you can compose a custom flavor. See
[Building Images](/how-to/building-images) for instructions.

## Step 2: Determine Your Target Platform

The platform identifies the hardware or cloud environment where the image runs.
Choose the platform that corresponds to your infrastructure.

| Platform                                     | Category      | Description                                                                                            |
| -------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------ |
| [`aws`](/reference/features/aws)             | Public cloud  | Amazon Web Services EC2                                                                                |
| [`azure`](/reference/features/azure)         | Public cloud  | Microsoft Azure Virtual Machines                                                                       |
| [`gcp`](/reference/features/gcp)             | Public cloud  | Google Cloud Platform Compute Engine                                                                   |
| [`openstack`](/reference/features/openstack) | Private cloud | OpenStack-based private cloud or hosted OpenStack                                                      |
| [`vmware`](/reference/features/vmware)       | Hypervisor    | VMware vSphere / ESXi                                                                                  |
| [`kvm`](/reference/features/kvm)             | Hypervisor    | KVM/QEMU-based virtualization                                                                          |
| [`baremetal`](/reference/features/baremetal) | Bare-metal    | Physical servers, PXE boot, IronCore                                                                   |
| [`container`](/reference/features/container) | Container     | [Full OCI base images (Docker, Podman, containerd)](/reference/container-images#full-container-images) |
| [`lima`](/reference/features/lima)           | Local dev     | Lima-based local development on Linux and macOS                                                        |

:::info One platform per flavor
Each flavor must target exactly one platform. The build system enforces this
by default — specifying zero or multiple platforms causes the build to fail.
See [ADR 0020](/reference/adr/0020-enforce-single-platform-by-default-in-builder)
for the rationale and opt-in override.
:::

For the full list of platform targets and their YAML schema, see
[Flavors Reference](/reference/flavors).

## Step 3: Select Features

Features extend the base platform with additional capabilities. The most common
features are listed below.

| Feature                                            | Description                                                                                                                                                           |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`gardener`](/reference/features/gardener)         | Installs containerd for Gardener-managed Kubernetes; systemd unit disabled at build time and enabled by Gardener at runtime                                           |
| [`_prod`](/reference/features/_prod)               | Production hardening: disables debug tooling and applies security defaults                                                                                            |
| [`khost`](/reference/features/khost)               | Installs containerd for vanilla (non-Gardener) Kubernetes                                                                                                             |
| [`vhost`](/reference/features/vhost)               | Installs KVM kernel modules and libvirt for use as a hypervisor host                                                                                                  |
| [`capi`](/reference/features/capi)                 | Cluster API support for bare-metal provisioning via IronCore                                                                                                          |
| [`_fips`](/reference/features/_fips)               | FIPS 140-2 compliant cryptography                                                                                                                                     |
| [`_usi`](/reference/features/_usi)                 | Boot using a UKI with embedded EROFS root disk                                                                                                                        |
| [`_trustedboot`](/reference/features/_trustedboot) | [Trusted Boot](/explanation/secure-boot): validates the entire boot chain including the rootfs (requires [`_tpm2`](/reference/features/_tpm2) for persistent storage) |
| [`_tpm2`](/reference/features/_tpm2)               | TPM 2.0 sealed disk encryption for `/var`, bound to the Secure Boot certificate chain (see [Boot Modes: Mutable Data](/explanation/boot-modes#mutable-data-modes))    |

## Step 4: Look Up the Flavor Name

Once you have a platform and feature set, look up the exact flavor name and
confirm it is published.

- **Common flavors by use case:** The [Use Cases](/explanation/use-cases) page
  includes a "Recommended Flavors" table under each use case section.
- **Complete flavor list:** The [Flavor Matrix](/reference/flavor-matrix)
  lists every flavor built from `flavors.yaml`, with their resolved feature
  dependencies, architectures, and publication status.

:::info How features are joined into a flavor name
Garden Linux uses the [CNAME system](/explanation/flavors#the-cname-system) to
construct canonical flavor names.
:::

## Example: Choosing a Gardener Flavor on AWS

The following walkthrough illustrates all four steps for a common scenario.

1. **Use case:** Gardener-managed Kubernetes worker nodes.
2. **Platform:** [`aws`](/reference/features/aws).
3. **Features:** [`gardener`](/reference/features/gardener) (required for Gardener integration) and [`_prod`](/reference/features/_prod)
   (production hardening).
4. **Flavor name:** `aws-gardener_prod`

To obtain the image for this [flavor](/explanation/flavors), see
[Getting Images](/how-to/getting-images).

:::tip
The [Flavor Matrix](/reference/flavor-matrix) gives you an overview of pre-built flavors and the exact recursive features they contain.
:::

## Related Topics

<RelatedTopics />
