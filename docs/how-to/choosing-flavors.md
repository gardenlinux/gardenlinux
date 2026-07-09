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
migration_status: "done"
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

## Step 1: Identify your use case

Determine which of the primary Garden Linux use cases matches your workload.
Each use case maps to a specific feature set.

| Use Case                                             | Description | Suitable Feature                                                                     | Go To                                                                                               |
| ---------------------------------------------------- | --- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Gardener-managed Kubernetes nodes                    | Installs containerd for Gardener-managed Kubernetes; systemd unit disabled at build time and enabled by Gardener at runtime  | [`gardener`](/reference/features/gardener) | [Gardener Kubernetes Nodes](/explanation/use-cases#gardener-kubernetes-nodes)                       |
| Bare-metal Gardener nodes via IronCore (Cluster API) | Cluster API support for bare-metal provisioning via IronCore       | [`capi`](/reference/features/capi)                                               | [Bare-Metal via IronCore](/explanation/use-cases#bare-metal-gardener-kubernetes-nodes-via-ironcore) |
| Vanilla (non-Gardener) Kubernetes nodes              | Installs containerd for vanilla (non-Gardener) Kubernetes                                                                                             | [`khost`](/reference/features/khost)                                             | [Vanilla Kubernetes Nodes](/explanation/use-cases#vanilla-kubernetes-nodes)                         |
| OCI container base image                             | Creates a tarball to use on all OCI Runtime Environments | [`container`](/reference/features/container) or `bare-*`                         | [Container Base Images](/explanation/use-cases#container-base-images)                               |
| KVM/libvirt virtualization host                      | Installs KVM kernel modules and libvirt for use as a hypervisor host                                                                                                  | [`vhost`](/reference/features/vhost)                                             | [Virtualization Host](/explanation/use-cases#virtualization-host)                                   |

:::tip
If no existing use case matches, you can compose a custom flavor. See
[Building Images](/how-to/building-images) for instructions.
:::

## Step 2: Determine your target platform

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

## Step 3: Select additional features

You can extend the use case and platform specific features with additional features. The most common features are listed below.

| Feature                                            | Description                                                                                                                                                           |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`_prod`](/reference/features/_prod)               | Production hardening: disables debug tooling and applies security defaults                                                                                            |
| [`_fips`](/reference/features/_fips)               | FIPS 140-2 compliant cryptography                                                                                                                                     |
| [`_ephemeral`](/reference/features/_ephemeral)     | Provides an ephemeral encrypted `/var`
| [`_usi`](/reference/features/_usi)                 | Boot using a UKI with embedded EROFS root disk                                                                                                                        |
| [`_trustedboot`](/reference/features/_trustedboot) | [Trusted Boot](/explanation/secure-boot): validates the entire boot chain including the rootfs (includes [`_ephemeral`](/reference/features/_ephemeral) and [`_usi`](/reference/features/_usi), requires [`_tpm2`](/reference/features/_tpm2) for persistent `/var`) |
| [`_tpm2`](/reference/features/_tpm2)               | TPM 2.0 sealed disk encryption for `/var`, bound to the Secure Boot certificate chain (see [Boot Modes: Mutable Data](/explanation/boot-modes#mutable-data-modes))    |


## Step 4: Look up the flavor name

Once you have a platform and feature set, look up the exact flavor name and
confirm it is published.

:::info How features are joined into a flavor name
Garden Linux uses the [CNAME system](/explanation/flavors#the-cname-system) to
construct canonical flavor names.
:::

- **Common flavors by use case:** The [Use Cases](/explanation/use-cases) page
  includes a "Recommended Flavors" table under each use case section.
- **Complete flavor list:** The [Flavor Matrix](/reference/flavor-matrix)
  lists every flavor built from `flavors.yaml`, with their resolved feature
  dependencies, architectures, and publication status.

:::tip
The [Flavor Matrix](/reference/flavor-matrix) gives you an overview of pre-built flavors and the exact recursive features they contain.
:::

:::tip
If you do not find pre-built existing images for your use case, you can compose a custom flavor. See
[Building Images](/how-to/building-images) for instructions.
:::


## Example: Choosing a Gardener flavor on AWS

The following walkthrough illustrates all four steps for a common scenario, an AWS Gardener node.

1. **Use case feature:** [`gardener`](/reference/features/gardener) (Gardener-managed Kubernetes node)
2. **Platform:** [`aws`](/reference/features/aws) (Amazon Web Services)
3. **Features:**  [`_prod`](/reference/features/_prod) (production hardening)
4. **Flavor name:** `aws-gardener_prod`

To obtain the image for this [flavor](/explanation/flavors), see
[Getting Images](/how-to/getting-images).

## Related topics

<RelatedTopics />
