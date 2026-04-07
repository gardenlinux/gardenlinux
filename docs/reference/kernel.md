---
title: "Kernel"
migration_status: "adapt"
migration_source: "00_introduction/kernel.md"
migration_issue: ""
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/reference/kernel.md
github_target_path: docs/reference/kernel.md
---

# Kernel

Garden Linux aims towards a complete open, reproducible and easy-to-understand solution. That also includes all activities around the Kernel.
[Kernel.org](https://kernel.org) is the source of the official Linux kernels and therefore all kernels in Garden Linux are mainly based on this. Not to forget our Debian roots: we integrate with the build environment [Debian kernels](https://wiki.debian.org/Kernel) to support the Debian featureset to be compatible. Garden Linux tries to keep the amount of patches in the kernel diverging from Debian and kernel.org low, so everybody can easily support the Garden Linux kernel and no deep knowledge of Garden Linux internals is needed.

## Kernel versioning strategy

In contrast to Debian, Garden Linux integrates always with the latest Long Term Support kernel (LTS) and maintains this kernel at least for one overlapping period till the next kernel will be available. You can find the release categories and the time schedule for LTS releases also on [kernel.org](https://www.kernel.org/category/releases.html).
Garden Linux aims to integrate the latest long term release.

### Why does Garden Linux not integrate the mainline stable?

Mainline stable introduces features to the new Linux kernel, which happens every ~2 months. Some of those features affect the way e.g. container or network environment interact with the kernel and need some time to be adopted in surrounding tooling. Also some other feature introduce bugs, recognized after release and need to be reverted or other changes. In short: to avoid this we wait until a kernel version becomes a longterm stable and try to integrate always the latest long term stable and the one before to have a decent deprecation phase.
**Garden Linux takes advantage of these patches.**

### A new long term kernel is released, when will it be integrated?

We are probably on it, but feel free to open a Github issue.

## Relationship to Debian

Garden Linux 💚 Debian.

Debian is free and open source software. There are good [reasons](https://www.debian.org/intro/why_debian)
to use Debian. In the following we explain our reasons in the kernel context.

First, Debian provides an enterprise grade server operating system,
while protecting the claim to stay 100% free and open source.
Debian is rigorous when it comes to non-free software licenses,
also when it comes to the Linux Kernel. A prominent example of
what this means, is the extraction of non-free firmware from
the Linux Kernel.

Debian scans licenses and patches out everything
that violates the claim to stay 100% free. Since Garden Linux shares this
approach, we benefit from Debian patches.

Additionally, Debian provides a good kernel configuration,
which is used by Garden Linux as a base for configuration.
We extend this kernel configuration to our specific requirements during the
kernel integration process.

Furthermore, Debian kernel [patches](https://salsa.debian.org/kernel-team/linux/-/tree/master/debian/patches) are applied in most cases.

## Kernel flavours

| Flavour     | Architecture | Description                                                    |
| ----------- | ------------ | -------------------------------------------------------------- |
| amd64       | x86_64       | 64-bit PCs; includes Intel SGX, TDX, Mellanox SmartNIC support |
| cloud-amd64 | x86_64       | Cloud VMs (AWS, Azure, GCP) - stripped-down with cloud drivers |
| arm64       | aarch64      | 64-bit ARMv8 machines                                          |
| cloud-arm64 | aarch64      | Cloud VMs (AWS, Azure, GCP) - stripped-down with cloud drivers |

Cloud flavours disable graphics, USB, wireless, Bluetooth, and audio drivers
and enable Hyper-V, virtio, Xen, ENA (AWS), GVE (GCE), and MANA (Azure).

## Supported kernel versions

| Branch       | Kernel | Description           |
| ------------ | ------ | --------------------- |
| `main`       | 6.18   | Latest LTS maintained |
| `maint-6.12` | 6.12   | Previous LTS          |
| `maint-6.6`  | 6.6    | Older LTS             |

## Kernel build system

The kernel build lives in a separate repository:
[gardenlinux/package-linux](https://github.com/gardenlinux/package-linux).

Key components:

- `config/` — Garden Linux-specific kernel configuration
- `fixes_debian/` — Patches to Debian build when needed
- `upstream_patches/` — Kernel patches not in Debian but part of Garden Linux
- `prepare_source` — Merges Debian kernel packaging with upstream sources

For details on building kernels, performing backports, and automated patch
updates, see the [Kernel Builds how-to](../how-to/kernel-builds.md).

## Automated kernel updates

Patch-level updates are automated via GitHub Actions. A scheduled workflow scans
configured branches and creates pull requests when new patch versions are
available.

## Further reading

- [kernel.org LTS releases](https://www.kernel.org/category/releases.html)
- [Debian kernel patches](https://salsa.debian.org/kernel-team/linux/-/tree/master/debian/patches)
- [Kernel Builds how-to](../how-to/kernel-builds.md)
