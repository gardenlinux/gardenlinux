---
title: "Use Cases"
description: "When and why to choose Garden Linux for your workload"
order: 9
related_topics:
  - /explanation/architecture
  - /explanation/flavors
  - /how-to/choosing-flavors
  - /how-to/building-images
  - /reference/releases/release-lifecycle
  - /reference/flavor-matrix
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/explanation/use-cases.md
github_target_path: docs/explanation/use-cases.md
---



# Use Cases

## Introduction

Garden Linux is a Debian GNU/Linux derivative that provides small, auditable,
and highly customizable Linux images for cloud providers, bare-metal servers,
and container runtimes. It is the official Container Operating System for
[Gardener](https://gardener.cloud), the Kubernetes-as-a-Service project, and
excels in cloud-native and containerized environments.

## When to Choose Garden Linux

Consider Garden Linux when you need:

- Small, reproducible builds with a minimal attack surface
- Full hardware access or cloud-native optimizations
- Security-hardened or compliance-ready systems (FIPS, CIS)
- A modular, feature-based build system for custom OS variants
- Consistent operating system across multiple infrastructure platforms

## Primary use cases

### Gardener Kubernetes Nodes

Garden Linux is the default and officially recommended OS for
[Gardener](https://gardener.cloud) and serves as the reference implementation in
all
[Kubernetes conformance tests](https://testgrid.k8s.io/conformance-gardener),
ensuring full compatibility and reliability across cloud providers.

It is listed in the
[Gardener extensions documentation](https://gardener.cloud/docs/extensions/os-extensions/gardener-extension-os-gardenlinux/)
and maintained via the
[gardener-extension-os-gardenlinux](https://github.com/gardener/gardener-extension-os-gardenlinux)
controller. Garden Linux ships with the
[`gardener`](/reference/features/gardener) feature pre-configured: containerd is
installed (systemd unit disabled, enabled by Gardener).

This use case applies to AWS, Azure, GCP, OpenStack, and bare-metal platforms.
Choose one of these when operating Kubernetes clusters managed by Gardener in
public or private clouds.

**Features:** [`gardener`](/reference/features/gardener),
[`_prod`](/reference/features/_prod)

**Platforms:** [`aws`](/reference/features/aws),
[`azure`](/reference/features/azure), [`gcp`](/reference/features/gcp),
[`openstack`](/reference/features/openstack),
[`baremetal`](/reference/features/baremetal)

#### Recommended Flavors

| Platform                                     | Flavor                                                                                 | Key Features                                                                     | Architecture |
| -------------------------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- | ------------ |
| [`aws`](/reference/features/aws)             | [`aws-gardener_prod`](/reference/flavor-matrix.md#aws-gardener_prod-amd64)             | [`gardener`](/reference/features/gardener), [`_prod`](/reference/features/_prod) | amd64, arm64 |
| [`azure`](/reference/features/azure)         | [`azure-gardener_prod`](/reference/flavor-matrix.md#azure-gardener_prod-amd64)         | [`gardener`](/reference/features/gardener), [`_prod`](/reference/features/_prod) | amd64, arm64 |
| [`gcp`](/reference/features/gcp)             | [`gcp-gardener_prod`](/reference/flavor-matrix.md#gcp-gardener_prod-amd64)             | [`gardener`](/reference/features/gardener), [`_prod`](/reference/features/_prod) | amd64, arm64 |
| [`openstack`](/reference/features/openstack) | [`openstack-gardener_prod`](/reference/flavor-matrix.md#openstack-gardener_prod-amd64) | [`gardener`](/reference/features/gardener), [`_prod`](/reference/features/_prod) | amd64, arm64 |
| [`kvm`](/reference/features/kvm)             | [`kvm-gardener_prod`](/reference/flavor-matrix.md#kvm-gardener_prod-amd64)             | [`gardener`](/reference/features/gardener), [`_prod`](/reference/features/_prod) | amd64, arm64 |
| [`vmware`](/reference/features/vmware)       | [`vmware-gardener_prod`](/reference/flavor-matrix.md#vmware-gardener_prod-amd64)       | [`gardener`](/reference/features/gardener), [`_prod`](/reference/features/_prod) | amd64, arm64 |
| [`baremetal`](/reference/features/baremetal) | [`baremetal-gardener_prod`](/reference/flavor-matrix.md#baremetal-gardener_prod-amd64) | [`gardener`](/reference/features/gardener), [`_prod`](/reference/features/_prod) | amd64, arm64 |

:::tip
For FIPS-compliant variants, see the [`_fips`](/reference/features/_fips)
feature. For Trusted Boot variants, see
[`_trustedboot`](/reference/features/_trustedboot) and [`_tpm2`](/reference/features/_tpm2)
and the [Secure Boot and Trusted Boot](/explanation/secure-boot) explanation. The full list of published
flavors is in the [Flavor Matrix](/reference/flavor-matrix).
:::

### Bare-Metal Gardener Kubernetes Nodes via IronCore

For organizations needing to run Gardener-managed Kubernetes on physical
hardware, Garden Linux integrates with [IronCore](https://ironcore.dev) to
provision bare-metal worker nodes via the Cluster API. This use case combines
the [`capi`](/reference/features/capi) (Cluster API) feature with the [`baremetal`](/reference/features/baremetal) platform to enable PXE
boot, ignition-based provisioning, and full hardware lifecycle management. It is
designed for large-scale on-premises or edge deployments where control plane and
worker nodes run on dedicated servers without a hypervisor layer.

IronCore provides the IaaS integration layer that translates Gardener's
infrastructure requests into bare-metal operations.

**Features:** [`capi`](/reference/features/capi)

**Platform:**
[`baremetal`](/reference/features/baremetal)

#### Recommended Flavors

| Platform                                     | Flavor                                                               | Key Features                       | Architecture |
| -------------------------------------------- | -------------------------------------------------------------------- | ---------------------------------- | ------------ |
| [`baremetal`](/reference/features/baremetal) | [`baremetal-capi`](/reference/flavor-matrix.md#baremetal-capi-amd64) | [`capi`](/reference/features/capi) | amd64, arm64 |

### Vanilla Kubernetes nodes

Garden Linux is also perfectly capable of running non-Gardener vanilla
[Kubernetes](https://kubernetes.io/) Nodes. Garden Linux ships with the
[`khost`](/reference/features/khost) feature pre-configured: containerd is
installed.

This use case applies to all platforms. Choose this when operating vanilla
Kubernetes clusters in public or private clouds.

**Features:** [`khost`](/reference/features/khost)

**Platforms:**
[`aws`](/reference/features/aws), [`azure`](/reference/features/azure),
[`gcp`](/reference/features/gcp), [`openstack`](/reference/features/openstack),
[`baremetal`](/reference/features/baremetal)

#### Recommended Flavors

The [`khost`](/reference/features/khost) feature is not published as a standalone [flavor](/explanation/flavors) in the default
`flavors.yaml`. Build a custom flavor by combining [`khost`](/reference/features/khost) with your target
platform. See [Building Images](/how-to/building-images) for instructions.

### Container base images

Garden Linux produces two families of Open Container Initiative (OCI) container
images:

- [**Full images**](/how-to/container-base-image/full.md) —
  Complete Debian-based environment with `apt`, systemd, and common utilities.
  Suitable for applications that need a package manager or extensive tooling.
- [**Bare images**](/how-to/container-base-image/bare.md) —
  Distroless-style images with only the runtime and its dependencies. Variants
  include `bare-libc` (C/C++), `bare-python` (Python), `bare-nodejs` (Node.js),
  and `bare-sapmachine` (Java/SAP). These images have a minimal footprint and
  attack surface, omitting shells and package managers by design.

All container images are published to
[GitHub Container Registry](https://github.com/gardenlinux/gardenlinux/pkgs/container/gardenlinux).
Use these as base images in your `Containerfile` or `Dockerfile` when you need
an auditable, minimal foundation.

**Features:** [`container`](/reference/features/container) (full images),
`bare-*` variants like
[`bare-libc`](https://github.com/gardenlinux/gardenlinux/tree/main/bare_flavors/libc),
[`bare-nodejs`](https://github.com/gardenlinux/gardenlinux/tree/main/bare_flavors/nodejs),
[`bare-python`](https://github.com/gardenlinux/gardenlinux/tree/main/bare_flavors/python),
[`bare-sapmachine`](https://github.com/gardenlinux/gardenlinux/tree/main/bare_flavors/sapmachine)

**Platform:** [`container`](/reference/features/container) (full images)

#### Recommended Flavors

| Type              | Flavor                                                                         | Description                          | Architecture |
| ----------------- | ------------------------------------------------------------------------------ | ------------------------------------ | ------------ |
| Full              | [`container`](/reference/flavor-matrix.md#container-amd64)                     | Complete Debian-based OCI base image | amd64, arm64 |
| Full (Python dev) | [`container-pythonDev`](/reference/flavor-matrix.md#container-pythondev-amd64) | Full image with Python toolchain     | amd64, arm64 |
| Bare (C/C++)      | [`bare-libc`](/reference/flavor-matrix.md#bare-libc-amd64)                     | Minimal C/C++ runtime (distroless)   | amd64, arm64 |
| Bare (Python)     | [`bare-python`](/reference/flavor-matrix.md#bare-python-amd64)                 | Minimal Python runtime (distroless)  | amd64, arm64 |
| Bare (Node.js)    | [`bare-nodejs`](/reference/flavor-matrix.md#bare-nodejs-amd64)                 | Minimal Node.js runtime (distroless) | amd64, arm64 |
| Bare (Java/SAP)   | [`bare-sapmachine`](/reference/flavor-matrix.md#bare-sapmachine-amd64)         | Minimal SAPMachine JDK (distroless)  | amd64, arm64 |

### Virtualization host

Garden Linux serves well as host for virtualized environments by support running
workloads in KVM/libvirt. Garden Linux ships with the
[`vhost`](/reference/features/vhost) feature pre-configured:

- KVM kernel modules and libvirt are installed and enabled.

This use case applies to all platforms. Choose this when operating KVM/libvirt
hypervisors in public or private clouds.

**Features:** [`vhost`](/reference/features/vhost)

**Platforms:** [`baremetal`](/reference/features/baremetal)

#### Recommended Flavors

| Platform                                     | Flavor                                                                 | Key Features                         | Architecture |
| -------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------ | ------------ |
| [`baremetal`](/reference/features/baremetal) | [`baremetal-vhost`](/reference/flavor-matrix.md#baremetal-vhost-amd64) | [`vhost`](/reference/features/vhost) | amd64, arm64 |

## Supported deployment environments

Nearly all of the above use cases can be deployed in one of three environment
categories:

### Cloud providers

Major public clouds are supported out of the box: AWS, Microsoft Azure, Google
Cloud Platform (GCP), and OpenStack for private clouds. Garden Linux images
include [cloud-init for initialization](/how-to/installation/post-install.html#method-3-cloud-init-user-data-cloud-platforms).

### On-premises / bare-metal

Deploy directly to physical servers by writing a raw disk image (`.raw`) to the
target drive or via PXE network boot. This environment gives complete hardware
control with no hypervisor overhead. The [`baremetal`](/reference/features/baremetal) platform includes drivers
for common server hardware and supports UEFI and legacy BIOS boot modes. Use
cases include data-center infrastructure nodes, edge appliances, and
single-tenant hardware.

### Virtualization & local development

Run Garden Linux as a guest virtual machine in libvirt/KVM, VMware and OpenStack
or use libvirt/KVM or Lima for local development on Linux and macOS. This
environment is ideal for testing, CI pipelines, and developer workflows where
rapid iteration and reproducibility are priorities.

## Flavor selection guide

For a step-by-step guide on choosing the right flavor, see
[Choosing Flavors](/how-to/choosing-flavors). For the complete matrix of all
flavors including FIPS, USI, and Trusted Boot variants, see the
[Flavor Matrix](/reference/flavor-matrix).

## Related topics

<RelatedTopics />
