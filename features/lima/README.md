---
title: "Feature: lima"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
  - /tutorials/local/first-boot-lima
  - /how-to/installation/local/lima
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/lima/README.md
github_target_path: docs/reference/features/lima.md
---

## Feature: lima

### Description

A [platform](/reference/glossary.html#platform) feature that builds a Garden Linux
image for use with [Lima](/reference/glossary#lima), a Linux virtual machine manager
for macOS and Linux. Artifacts are delivered as `.qcow2` files.

### What it does

Produces a Lima-compatible Garden Linux image and a matching Lima YAML manifest.
Key configurations:

- **Image conversion**: `convert.qcow2` converts the raw artifact to `.qcow2`
  format required by Lima.
- **Lima manifest**: `exec.config` writes a `.lima.yaml` manifest file
  alongside the build artifact, enabling `limactl start` to consume the image
  directly.
- **Kernel command line**: sets default boot parameters and console settings
  for the Lima virtualization environment.
- **Kernel hook**: installs a `postinst` hook so that the kernel command line
  is regenerated after kernel package updates.

Pre-built nightly and release images are published for direct use with `limactl`.

See `samples/` for example Lima manifest files covering common use cases such
as Kubernetes, containerd, and rootless Podman.

:::info Using Garden Linux with Lima

For step-by-step instructions, see:

- [First Boot on Lima](/tutorials/local/first-boot-lima.md) — tutorial covering
  how to launch Garden Linux under Lima using pre-built images
- [Install Locally Using Lima](/how-to/installation/local/lima.md) — how-to guide
  covering manifest generation, building your own image, and sample manifests

:::

### Files

Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of each file type.

| File | Purpose |
|---|---|
| [`convert.qcow2`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/convert.qcow2) ([ref](/reference/features/#image-image-ext-convert-ext-convert-exta-extb)) | Converts the `.raw` artifact to a `.qcow2` image for Lima. |
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Writes a `.lima.yaml` manifest file alongside the build artifact for use with `limactl start`. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: platform` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs `cloud-init`, `dosfstools`, `dmidecode`, `efibootmgr`, `efitools`, and `openssh-server`. |
| [`file.include/etc/kernel/cmdline.d/00-default.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/file.include/etc/kernel/cmdline.d/00-default.cfg) ([`file.include`](/reference/features/#file-include)) | Sets default kernel boot parameters for the Lima virtual machine. |
| [`file.include/etc/kernel/cmdline.d/10-console.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/file.include/etc/kernel/cmdline.d/10-console.cfg) ([`file.include`](/reference/features/#file-include)) | Sets the kernel console parameter for Lima. |
| [`file.include/etc/kernel/postinst.d/00-kernel-cmdline`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/file.include/etc/kernel/postinst.d/00-kernel-cmdline) ([`file.include`](/reference/features/#file-include)) | Kernel package post-install hook that regenerates the kernel command line after kernel updates. |
| [`samples/README.md`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/samples/README.md) | Documentation for the Lima sample manifests. |
| [`samples/gardenlinux-containerd.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/samples/gardenlinux-containerd.yaml) | Sample Lima manifest for a Garden Linux VM with containerd. |
| [`samples/gardenlinux-k8s.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/samples/gardenlinux-k8s.yaml) | Sample Lima manifest for a Garden Linux VM with Kubernetes. |
| [`samples/gardenlinux-rootless-podman.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/samples/gardenlinux-rootless-podman.yaml) | Sample Lima manifest for a Garden Linux VM with rootless Podman. |
| [`samples/_images/gardenlinux-2150.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/samples/_images/gardenlinux-2150.yaml) | Sample Lima manifest for a specific Garden Linux 2150 release image. |

### Related features

**Includes:**

- [`cloud`](/reference/features/cloud) — provides common cloud-init integration and base cloud configuration.

**Excludes (incompatible with):**

- [`sap`](/reference/features/sap) — SAP-specific configuration is incompatible with Lima desktop use.
- [`firewall`](/reference/features/firewall) — the default firewall rules conflict with Lima networking requirements.
- [`_selinux`](/reference/features/_selinux) — SELinux is not supported in the Lima environment.

### Further reading

- [cloud-init documentation](https://cloudinit.readthedocs.io/)
- [Lima documentation](https://lima-vm.io/docs/)

## Related topics

<RelatedTopics />
