---
title: "Feature: capi"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/capi/README.md
github_target_path: docs/reference/features/capi.md
---

## Feature: capi

### Description

A feature that groups configurations needed for [Kubernetes](/reference/glossary#kubernetes) cluster nodes in [IronCore](/reference/glossary#ironcore) and [SAP Converged Cloud](/reference/glossary#sap-converged-cloud) environments. Use with the [`metal`](/reference/features/metal) platform.

### What it does

This feature groups a set of features needed when network-bootstrapping servers for use in a Kubernetes cluster. The notable addition is the replacement of `ignition` with `ignition-legacy`, which adds support for v2 [ignition](/reference/glossary#ignition) configs. This is required because only ignition v2 is supported when ignition is used as the configuration engine for bootstrapping workload cluster machines with the Kubernetes Cluster API.

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/capi/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.exclude`](https://github.com/gardenlinux/gardenlinux/blob/main/features/capi/pkg.exclude) ([ref](/reference/features/#pkg-exclude)) | Prevents installation of: `ignition`. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/capi/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `ignition-legacy`. |

### Related features

**Includes:**

- [`server`](/reference/features/server) — provides the base server configuration (networking, SSH, auditd, SELinux).
- [`khost`](/reference/features/khost) — provides Kubernetes host node configuration.
- [`_pxe`](/reference/features/_pxe) — enables PXE network boot support for metal provisioning.

**Excludes (incompatible with):**

- [`_selinux`](/reference/features/_selinux) — SELinux conflicts with the Kubernetes CNI networking stack used in this environment.
- [`firewall`](/reference/features/firewall) — the nftables firewall conflicts with Kubernetes CNI networking.

## Related topics

<RelatedTopics />

