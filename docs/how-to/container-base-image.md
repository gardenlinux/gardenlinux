---
title: "Container Base Image"
description: "How to use Garden Linux full and bare (distroless-style) OCI container images as base images in Containerfiles and Dockerfiles"
category: "how-to"
tags:
  [
    "how-to",
    "container",
    "oci",
    "docker",
    "podman",
    "base-image",
    "bare-container",
  ]
migration_status: "new"
migration_source: "01_developers/bare_container.md"
migration_issue: ""
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/container-base-image.md
github_target_path: docs/how-to/container-base-image.md
---

# Use Garden Linux as a Container Base Image

Garden Linux provides two types of [Open Container Initiative (OCI)](https://opencontainers.org/) container images:

- **Full container images** — Standard Garden Linux with a full userland (apt, systemd, etc.)
- **Bare container images** — Distroless-style images with minimal footprint, stripped of unnecessary components

This guide covers using both types as base images in your own `Containerfile` or `Dockerfile`.

## Prerequisites

Before starting, you'll need:

- A container runtime: [Podman](https://podman.io/docs/installation) or [Docker](https://docs.docker.com/get-docker/)
- Familiarity with `Containerfile` or `Dockerfile` syntax
- For bare images with pip/npm dependencies: basic understanding of [multi-stage builds](https://docs.docker.com/build/building/multi-stage/)

:::tip
This guide uses `podman` commands throughout. If you use Docker, replace `podman` with `docker` — the commands are interchangeable.
:::

## Full Container Base Image

The full Garden Linux container image provides a complete Linux environment with package manager access.

### Choosing a Version

Garden Linux publishes two image streams to the GitHub Container Registry:

| Image Stream | URI                                         | Use Case                   |
| ------------ | ------------------------------------------- | -------------------------- |
| Release      | `ghcr.io/gardenlinux/gardenlinux:<version>` | Stable, versioned releases |
| Nightly      | `ghcr.io/gardenlinux/nightly:<version>`     | Latest development builds  |

For production use, prefer release images with a specific version tag:

```bash
GL_VERSION="2150.0.0"
GL_IMAGE="ghcr.io/gardenlinux/gardenlinux:${GL_VERSION}"
```

For testing or development, use the nightly stream:

```bash
GL_IMAGE="ghcr.io/gardenlinux/nightly:latest"
```

:::tip
For a complete list of maintained releases and their support lifecycle, see the [releases reference](../reference/releases/index.md).
:::

### Basic Containerfile Example

Use the full Garden Linux container as a base for applications that need a standard Linux environment:

```dockerfile
FROM ghcr.io/gardenlinux/gardenlinux:2150.0.0

# Install additional packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html /var/www/html/

# Set runtime configuration
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Installing Additional Packages

The full container image includes `apt`, allowing you to install packages at build time:

```dockerfile
FROM ghcr.io/gardenlinux/gardenlinux:2150.0.0

RUN apt-get update && apt-get install -y --no-install-recommends \
    <your-packages> \
    && rm -rf /var/lib/apt/lists/*
```

:::warning
Always include `rm -rf /var/lib/apt/lists/*` at the end of `apt-get` commands to reduce image size.
:::

## Bare Container Images

Bare container images are stripped-down, distroless-style images optimized for production deployments where minimal attack surface and small image size matter.

### Overview

Garden Linux produces four bare image variants using the [unbase_oci](https://github.com/gardenlinux/unbase_oci) tool, which compares a base image with a target image and retains only the added components and their dependencies.

| Image             | Description                                                       | Registry URI                                                |
| ----------------- | ----------------------------------------------------------------- | ----------------------------------------------------------- |
| `bare-libc`       | C runtime (libc6, zoneinfo) — for C/C++ applications              | `ghcr.io/gardenlinux/gardenlinux/bare-libc:<version>`       |
| `bare-python`     | Python runtime — for Python applications                          | `ghcr.io/gardenlinux/gardenlinux/bare-python:<version>`     |
| `bare-nodejs`     | Node.js runtime — for JavaScript applications                     | `ghcr.io/gardenlinux/gardenlinux/bare-nodejs:<version>`     |
| `bare-sapmachine` | SAPMachine JDK (Java Development Kit) — for Java/SAP applications | `ghcr.io/gardenlinux/gardenlinux/bare-sapmachine:<version>` |

:::tip
Bare images intentionally omit basic utilities like `sh`. For debugging, see the [Debug a Bare Container](#debug-a-bare-container) section below.
:::

### bare-libc: C/C++ Applications

Use `bare-libc` for compiled applications that require only the C library:

```dockerfile
# Build stage: compile the application
FROM gcc:bookworm AS compile
COPY source.c /
RUN gcc -O2 -o myapp source.c

# Production stage: copy the compiled binary into the bare image
FROM ghcr.io/gardenlinux/gardenlinux/bare-libc:2150.0.0
COPY --from=compile /myapp /
CMD [ "/myapp" ]
```

### bare-python: Python Applications

Use `bare-python` for Python applications. The image includes Python but not `pip`:

```dockerfile
FROM ghcr.io/gardenlinux/gardenlinux/bare-python:2150.0.0
COPY hello.py /
CMD [ "python3", "/hello.py" ]
```

#### Adding Python Dependencies

Since `bare-python` lacks `pip`, use a multi-stage build with the `container-python-dev` image to install dependencies, then copy them into the bare image:

```dockerfile
# Build stage: install dependencies
FROM ghcr.io/gardenlinux/gardenlinux/container-python-dev:2150.0.0 AS packages
COPY requirements.txt /
RUN pip3 install -r requirements.txt --break-system-packages --no-cache-dir
RUN exportLibs.py

# Production stage: copy dependencies into bare image
FROM ghcr.io/gardenlinux/gardenlinux/bare-python:2150.0.0
COPY --from=packages /usr/local/lib/python3.13/dist-packages/ /usr/local/lib/python3.13/dist-packages/
COPY --from=packages /required_libs /
COPY main.py /
ENTRYPOINT [ "python3", "/main.py" ]
```

The `exportLibs.py` script traces shared library dependencies of pip-installed packages and copies them to `/required_libs` for the production stage.

### bare-nodejs: Node.js Applications

Use `bare-nodejs` for Node.js applications:

```dockerfile
FROM ghcr.io/gardenlinux/gardenlinux/bare-nodejs:2150.0.0
COPY index.js /
CMD [ "node", "/index.js" ]
```

For applications with npm dependencies, use a multi-stage build similar to the Python example, using a Node.js development image in the first stage.

### bare-sapmachine: Java/SAP Applications

Use `bare-sapmachine` for Java applications using SAPMachine:

```dockerfile
# Build stage: compile Java application
FROM docker.io/library/sapmachine:latest AS compile
COPY Test.java /
RUN javac Test.java && jar -c -f test.jar -e Test Test.class

# Production stage: copy JAR into bare image
FROM ghcr.io/gardenlinux/gardenlinux/bare-sapmachine:2150.0.0
COPY --from=compile /test.jar /
CMD [ "java", "-jar", "/test.jar" ]
```

## Debug a Bare Container

Bare images lack basic utilities like `sh`, making debugging challenging. To debug, mount the bare image into a Debian container:

### Step 1: Pull and Mount the Image

```bash
podman pull ghcr.io/gardenlinux/gardenlinux/bare-python:2150.0.0
podman run --rm -it \
    --mount type=image,src=ghcr.io/gardenlinux/gardenlinux/bare-python:2150.0.0,dst=/mnt,rw=true \
    debian
```

You are now in a Debian shell with the bare image accessible at `/mnt`.

### Step 2: Enter the Bare Image

Run commands inside the bare image using `chroot`:

```bash
chroot /mnt <command>
```

### Step 3: Install Basic Utilities

To spawn a shell inside the bare image, install [toybox](https://landley.net/toybox/), which provides many CLI utilities in a single binary:

```bash
apt update && apt install curl -y
curl http://landley.net/bin/toybox/latest/toybox-$(uname -m) -o /mnt/bin/toybox
chmod +x /mnt/bin/toybox
```

Now you can spawn a shell:

```bash
chroot /mnt toybox sh
```

### Step 4: Analyze Image Size

To diagnose unexpected image growth, analyze directory sizes:

```bash
apt update && apt install du-dust
dust -n 32 -w 64 -r /mnt
```

This shows which directories consume the most space, helping identify unnecessary files.

## Further Reading

- [Building Flavors Guide](customization/building-flavors.md) — Build custom Garden Linux images from source
- [OCI Platform-Specific Features](platform-specific/oci.md) — OCI image build process and platform configurations
- [Garden Linux Releases Reference](../reference/releases/index.md) — Maintained releases and support lifecycle
- [unbase_oci GitHub Repository](https://github.com/gardenlinux/unbase_oci) — Tool for creating bare container images
