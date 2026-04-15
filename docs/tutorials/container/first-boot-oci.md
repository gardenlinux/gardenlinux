---
title: "First Boot as OCI Image"
description: "Step-by-step guide to running Garden Linux as an OCI container image"
category: "tutorials"
tags: ["tutorial", "oci", "container", "podman", "docker", "beginner"]
migration_status: "adapt"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4595"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/tutorials/container/first-boot-oci.md
github_target_path: "docs/tutorials/container/first-boot-oci.md"
---

# First Boot as OCI Image

Garden Linux is a minimal, security-hardened Linux distribution designed for cloud and container environments. In addition to virtual machine and cloud images, Garden Linux publishes Open Container Initiative (OCI) container images that you can run directly with any OCI-compliant container runtime such as [Podman](https://podman.io/) or [Docker](https://www.docker.com/).

This tutorial guides you through pulling and running your first Garden Linux container, from selecting an image to verifying the installation.

**Difficulty:** Beginner | **Time:** ~5 minutes

**Learning Objective:** By the end of this tutorial, you'll have a running Garden Linux container and understand how to use the official OCI images.

## Prerequisites

Before starting, you'll need:

- A container runtime installed: [Podman](https://podman.io/docs/installation) or [Docker](https://docs.docker.com/get-docker/)
- Internet access to pull images from the GitHub Container Registry (ghcr.io)

:::tip
Install Podman on Debian/Ubuntu-based systems:

```bash
sudo apt install podman
```

On macOS, use [Homebrew](https://brew.sh/):

```bash
brew install podman
podman machine init
podman machine start
```

:::

:::tip
This tutorial uses `podman` commands throughout. If you use Docker, replace `podman` with `docker` — the commands are interchangeable.
:::

## What You'll Build

You'll pull a Garden Linux OCI image from the GitHub Container Registry and run an interactive container. No infrastructure setup, SSH configuration, or disk images are required — a single command gets you a running Garden Linux environment.

## Steps

### Step 1: Choose an Image

Garden Linux publishes OCI container images to the GitHub Container Registry. Two image streams are available:

- **Release images** — stable, versioned releases
- **Nightly images** — built from the latest development branch

#### Release Images (Recommended)

Choose a release from the [GitHub Releases page](https://github.com/gardenlinux/gardenlinux/releases). For this tutorial, we'll use [release 2150.0.0](https://github.com/gardenlinux/gardenlinux/releases/tag/2150.0.0).

```bash
GL_VERSION="2150.0.0"
GL_IMAGE="ghcr.io/gardenlinux/gardenlinux:${GL_VERSION}"
```

#### Nightly Images

To use the latest nightly build:

```bash
GL_VERSION="2198.0.0"
GL_IMAGE="ghcr.io/gardenlinux/nightly:${GL_VERSION}"
```

:::tip
For a complete list of maintained releases and their support lifecycle, see the [releases reference](../../reference/releases/index.md).
:::

#### Build Your Own Images

You can [Build your own Garden Linux Images](/how-to/building-images) or even [Create a custom Feature](/how-to/custom-feature).

### Step 2: Pull the Image

Pull the Garden Linux container image from the GitHub Container Registry:

```bash
podman pull "${GL_IMAGE}"
```

Expected output:

```text
Trying to pull ghcr.io/gardenlinux/gardenlinux:2150.0.0...
Getting image source signatures
Copying blob ...
...
Writing manifest to image destination
```

### Step 3: Run the Container

Start an interactive Garden Linux container:

```bash
podman run --rm -it "${GL_IMAGE}" /bin/bash
```

You are now inside a running Garden Linux container with a bash shell.

:::tip
The `--rm` flag removes the container when you exit. Omit it if you want the container to persist after exiting:

```bash
podman run -it --name gardenlinux "${GL_IMAGE}" /bin/bash
```

You can restart it later with `podman start -ai gardenlinux`.
:::

### Step 4: Verify the Installation

Once inside the container, verify your Garden Linux environment with the following commands:

```bash
# Check OS information
cat /etc/os-release

# Verify kernel version (shows the host kernel)
uname -a

# Check available packages
dpkg -l | head -20
```

Expected output from `/etc/os-release` should show:

```bash
ID=gardenlinux
NAME="Garden Linux"
VERSION="${GL_VERSION}"
...
```

### Step 5: Install Additional Software

The pre-built container images are intentionally minimal. Use `apt` to search and install additional packages:

```bash
apt update
apt search <package-name>
apt install <package-name>
```

## Success Criteria

You have successfully completed this tutorial when:

- You can pull the Garden Linux OCI image from the GitHub Container Registry
- You can start an interactive container session
- You can verify the Garden Linux version using `cat /etc/os-release`

## Cleanup

When you're finished with the tutorial, exit the container and remove the image:

```bash
# Exit the container (if still inside)
exit

# Remove the image
podman rmi "${GL_IMAGE}"
```

## Next Steps

Now that you have a running Garden Linux container, you can:

- Explore [OCI platform-specific features and configurations](../../how-to/installation/container/oci.md)
- Use Garden Linux as a [base image](../../how-to/container-base-image.md) in your own Containerfile or Dockerfile
