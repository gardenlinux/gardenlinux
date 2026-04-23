---
title: "Use Cases"
description: "When and why to choose Garden Linux for your workload"
category: "explanation"
tags:
  - "use-cases"
  - "gardener"
  - "containers"
  - "kubernetes"
  - "bare-metal"
related_topics:
  - /explanation/architecture
  - /explanation/flavors-and-features
  - /how-to/building-images
  - /reference/releases/release-lifecycle
  - /reference/flavor-matrix
migration_status: "done"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4635"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
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

## Primary Use Cases

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

### Bare-Metal Gardener Kubernetes Nodes via IronCore

For organizations needing to run Gardener-managed Kubernetes on physical
hardware, Garden Linux integrates with [IronCore](https://ironcore.dev) to
provision bare-metal worker nodes via the Cluster API. This use case combines
the `capi` (Cluster API) feature with the `baremetal` platform to enable PXE
boot, ignition-based provisioning, and full hardware lifecycle management. It is
designed for large-scale on-premises or edge deployments where control plane and
worker nodes run on dedicated servers without a hypervisor layer.

IronCore provides the IaaS integration layer that translates Gardener's
infrastructure requests into bare-metal operations.

**Features:** [`capi`](/reference/features/capi) **Platform:**
[`baremetal`](/reference/features/baremetal)

### Vanilla Kubernetes Nodes

Garden Linux is also perfectly capable of running non-Gardener vanilla
[Kubernetes](https://kubernetes.io/) Nodes. Garden Linux ships with the
[`khost`](/reference/features/khost) feature pre-configured: containerd is
installed.

This use case applies to all platforms. Choose this when operating vanilla
Kubernetes clusters in public or private clouds.

**Features:** [`khost`](/reference/features/khost) **Platforms:**
[`aws`](/reference/features/aws), [`azure`](/reference/features/azure),
[`gcp`](/reference/features/gcp), [`openstack`](/reference/features/openstack),
[`baremetal`](/reference/features/baremetal)

### Container Base Images

Garden Linux produces two families of Open Container Initiative (OCI) container
images:

- [**Full images**](/how-to/container-base-image#full-container-base-image) —
  Complete Debian-based environment with `apt`, systemd, and common utilities.
  Suitable for applications that need a package manager or extensive tooling.
- [**Bare images**](/how-to/container-base-image#bare-container-images) —
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

### Virtualization Host

Garden Linux serves well as host for virtualized environments by support running
workloads in KVM/libvirt. Garden Linux ships with the
[`vhost`](/reference/features/vhost) feature pre-configured:

This use case applies to all platforms. Choose this when operating KVM/libvirt
hypervisors in public or private clouds.

**Features:** [`vhost`](/reference/features/vhost)

**Platforms:** [`aws`](/reference/features/aws),
[`azure`](/reference/features/azure), [`gcp`](/reference/features/gcp),
[`openstack`](/reference/features/openstack),
[`baremetal`](/reference/features/baremetal)

## Supported Deployment Environments

Nearly all of the above use cases can be deployed in one of three environment
categories:

### Cloud Providers

Major public clouds are supported out of the box: AWS, Microsoft Azure, Google
Cloud Platform (GCP), and OpenStack for private clouds. Garden Linux images
include cloud-init for initialization.

### On-Premises / Bare-Metal

Deploy directly to physical servers by writing a raw disk image (`.raw`) to the
target drive or via PXE network boot. This environment gives complete hardware
control with no hypervisor overhead. The `baremetal` platform includes drivers
for common server hardware and supports UEFI and legacy BIOS boot modes. Use
cases include data-center infrastructure nodes, edge appliances, and
single-tenant hardware.

### Virtualization & Local Development

Run Garden Linux as a guest virtual machine in libvirt/KVM, VMware and OpenStack
or use libvirt/KVM or Lima for local development on Linux and macOS. This
environment is ideal for testing, CI pipelines, and developer workflows where
rapid iteration and reproducibility are priorities.

## Common Flavors

The following table lists commonly used Garden Linux flavors. For the complete
matrix including all variants (FIPS, USI, Trusted Boot, architectures), see
[Flavor Matrix](../reference/flavor-matrix.md).

| Flavor                                                                                   | Purpose                       | Key Features                     | Deployable In      |
| ---------------------------------------------------------------------------------------- | ----------------------------- | -------------------------------- | ------------------ |
| [`aws-gardener_prod`](../reference/flavor-matrix.md#aws-gardener_prod-amd64)             | Gardener nodes on AWS         | `gardener`, `_prod`, `aws`       | Cloud              |
| [`azure-gardener_prod`](../reference/flavor-matrix.md#azure-gardener_prod-amd64)         | Gardener nodes on Azure       | `gardener`, `_prod`, `azure`     | Cloud              |
| [`gcp-gardener_prod`](../reference/flavor-matrix.md#gcp-gardener_prod-amd64)             | Gardener nodes on GCP         | `gardener`, `_prod`, `gcp`       | Cloud              |
| [`openstack-gardener_prod`](../reference/flavor-matrix.md#openstack-gardener_prod-amd64) | Gardener nodes on OpenStack   | `gardener`, `_prod`, `openstack` | Cloud / On-Prem    |
| [`kvm-gardener_prod`](../reference/flavor-matrix.md#kvm-gardener_prod-amd64)             | Gardener nodes on KVM         | `gardener`, `_prod`, `kvm`       | Virtualization     |
| [`baremetal-gardener_prod`](../reference/flavor-matrix.md#baremetal-gardener_prod-amd64) | Gardener on physical hardware | `gardener`, `_prod`, `baremetal` | On-Prem            |
| [`baremetal-capi`](../reference/flavor-matrix.md#baremetal-capi-amd64)                   | IronCore / CAPI nodes         | `capi`, `baremetal`              | On-Prem (PXE)      |
| [`container`](../reference/flavor-matrix.md#container-amd64)                             | Generic OCI container base    | `container`                      | All (build target) |
| [`bare-libc`](../reference/flavor-matrix.md#bare-libc-amd64)                             | Minimal C/C++ runtime         | distroless libc only             | All (build target) |
| [`bare-python`](../reference/flavor-matrix.md#bare-python-amd64)                         | Minimal Python runtime        | distroless Python                | All (build target) |
| [`bare-nodejs`](../reference/flavor-matrix.md#bare-nodejs-amd64)                         | Minimal Node.js runtime       | distroless Node.js               | All (build target) |
| [`bare-sapmachine`](../reference/flavor-matrix.md#bare-sapmachine-amd64)                 | Minimal Java/SAP runtime      | distroless SAPMachine JDK        | All (build target) |

## Related Topics

<RelatedTopics />
