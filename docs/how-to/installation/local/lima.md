---
title: "Install Locally Using Lima"
description: "How to install Garden Linux on Lima"
related_topics:
  - /tutorials/local/first-boot-lima.md
  - /how-to/installation/post-install.md
  - /reference/features/lima
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/installation/local/lima.md
github_target_path: docs/how-to/installation/local/lima.md
---

# Install Locally Using Lima

This guide covers platform-specific installation and configuration tasks for deploying Garden Linux on Lima (Linux virtual machines on macOS and Linux).

::: tip New to Lima Deployments?

For a complete step-by-step first-boot walkthrough, see the [First Boot on Lima](/tutorials/local/first-boot-lima.md) tutorial. The tutorial covers installing Lima, creating a YAML configuration, launching a VM, and connecting via SSH.

:::

## Generate a Lima manifest using the script directly

If you have [`glrd`](/reference/supporting_tools/glrd/) installed locally, you can run
`generate-lima-yaml.py` directly from the gardenlinux repository without Podman:

```bash
# Latest release:
./bin/generate-lima-yaml.py | limactl start --name gardenlinux -

# Specific release version:
./bin/generate-lima-yaml.py --version <version> | limactl start --name gardenlinux -

# Latest nightly:
./bin/generate-lima-yaml.py --version nightly | limactl start --name gardenlinux -

# Specific nightly version (requires --allow-nightly):
./bin/generate-lima-yaml.py --version <version> --allow-nightly | limactl start --name gardenlinux -
```

For all options: `./bin/generate-lima-yaml.py --help`

:::info Installing glrd

See [Run GLRD](/how-to/releases/glrd/run-glrd.md) for installation instructions.

:::

## Use a locally built Lima image

After [building a Garden Linux Lima image](/how-to/building-images), create a Lima
manifest that points to your local `.qcow2` file:

```yaml
os: Linux
images:
  - location: /path/to/your/gardenlinux/.build/lima-<arch>-<version>-<commit_sha>.qcow2
containerd:
  system: false
  user: false
```

Start the VM:

```bash
cat manifest.yaml | limactl start --name=gardenlinux -
limactl shell gardenlinux
```

## Sample Lima manifests

Lima YAML manifests can include provisioning shell scripts that run on first boot.
The gardenlinux repository ships examples in
[`features/lima/samples/`](https://github.com/gardenlinux/gardenlinux/tree/main/features/lima/samples/):

- [`gardenlinux-containerd.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/samples/gardenlinux-containerd.yaml) — installs the Garden Linux build of containerd
- [`gardenlinux-k8s.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/samples/gardenlinux-k8s.yaml) — sets up Kubernetes
- [`gardenlinux-rootless-podman.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/lima/samples/gardenlinux-rootless-podman.yaml) — installs and configures rootless Podman

For complex provisioning, building a [custom Garden Linux image](/how-to/custom-feature)
is preferable to provisioning scripts as it produces a reproducible, hardened artifact.

## Post-Installation Steps

After installation, follow one or more of these post-installation steps to complete your Lima setup:

- [Creating A User Using the `fwcfg`-script for LIMA Deployments](/how-to/installation/post-install.md#method-2-fwcfg-script-kvmqemu)

## Related topics

<RelatedTopics />

<!-- TODO: Merge from: 02_operators/lima-vm.md, 02_operators/local-k8s-lima.md -->
