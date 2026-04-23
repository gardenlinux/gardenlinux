---
title: "Bare Container Base Images"
description: "How to use Garden Linux bare (distroless-style) OCI container images as base images in Containerfiles and Dockerfiles"
related_topics:
  - /explanation/container-base-image.md
  - /how-to/container-base-image/bare.md
  - /how-to/container-base-image/full.md
  - /reference/container-images.md
migration_status: "done"
migration_source: "01_developers/bare_container.md"
migration_issue: "https://github.com/gardenlinux/gardenlinux/issues/4626"
migration_stakeholder: "@tmang0ld, @yeoldegrove, @ByteOtter"
migration_approved: false
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/how-to/container-base-image/bare.md
github_target_path: docs/how-to/container-base-image/bare.md
---

# Bare Container Base Images

## Prerequisites

Before starting, you'll need:

- A container runtime: [Podman](https://podman.io/docs/installation) or [Docker](https://docs.docker.com/get-docker/)
- Familiarity with `Containerfile` or `Dockerfile` syntax
- For bare images with pip/npm dependencies: basic understanding of [multi-stage builds](https://docs.docker.com/build/building/multi-stage/)

:::tip
This guide uses `podman` commands throughout. If you use Docker, replace `podman` with `docker` — the commands are interchangeable.
:::

## Choosing an Image

Choose an image by [looking at the Garden Linux Container Image Reference](/reference/container-images.md#bare-container-images).

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

If a setup works in the normal container, but fails in the corresponding bare container, debugging the problem can get challenging, as the [unbase_oci tool](/explanation/container-base-image.md#the-unbase-oci-tool) removes basic binaries like `sh`.
By following the steps in this section, you can regain the basic functionalities without rebuilding the image.

### Step 1: Pull and Mount the Image

As the first step, we want to mount the bare image to a debian installation. As mounting does not automatically pull the image, we pull it manually:

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

Bare images may unexpectedly grow. To find the cause of the issue, we can install tools to the debian container and use them on the `/mnt` folder.

```bash
apt update && apt install du-dust
dust -n 32 -w 64 -r /mnt
 52M └─┬ mnt                        │████████████████████ │ 100%
 52M   └─┬ usr                      │████████████████████ │ 100%
 43M     ├─┬ lib                    │█████████████████░░░ │  82%
 28M     │ ├─┬ python3.13           │███████████▒▒▒▒▒▒░░░ │  55%
5.2M     │ │ ├── lib-dynload        │██▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │  10%
5.2M     │ │ ├── __pycache__        │██▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │  10%
2.4M     │ │ ├─┬ encodings          │█▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │   5%
780K     │ │ │ └── __pycache__      │█▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │   1%
1.5M     │ │ ├─┬ test               │█▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │   3%
768K     │ │ │ ├── support          │█▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │   1%
520K     │ │ │ └── libregrtest      │█▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │   1%
1.3M     │ │ ├─┬ asyncio            │█▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │   2%
732K     │ │ │ └── __pycache__      │█▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │   1%
1.0M     │ │ ├─┬ pydoc_data         │█▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │   2%
524K     │ │ │ └── __pycache__      │█▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │   1%
964K     │ │ ├── email              │█▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │   2%
776K     │ │ ├── multiprocessing    │█▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │   1%
772K     │ │ ├── xml                │█▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │   1%
616K     │ │ ├── importlib          │█▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │   1%
608K     │ │ ├── unittest           │█▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │   1%
540K     │ │ └── _pyrepl            │█▓▓▓▓▓▓▓▓▓▓▒▒▒▒▒▒░░░ │   1%
 14M     │ └─┬ aarch64-linux-gnu    │██████▒▒▒▒▒▒▒▒▒▒▒░░░ │  27%
5.8M     │   ├── libcrypto.so.3     │███▓▓▓▒▒▒▒▒▒▒▒▒▒▒░░░ │  11%
1.7M     │   ├── libc.so.6          │█▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒░░░ │   3%
1.6M     │   ├── libsqlite3.so.0.8.6│█▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒░░░ │   3%
1.1M     │   ├── libssl.so.3        │█▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒░░░ │   2%
708K     │   ├── libzstd.so.1.5.7   │█▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒░░░ │   1%
580K     │   └── libm.so.6          │█▓▓▓▓▓▒▒▒▒▒▒▒▒▒▒▒░░░ │   1%
7.0M     ├─┬ bin                    │███░░░░░░░░░░░░░░░░░ │  13%
6.9M     │ └── python3.13           │███░░░░░░░░░░░░░░░░░ │  13%
2.4M     └─┬ share                  │█░░░░░░░░░░░░░░░░░░░ │   5%
1.9M       └─┬ zoneinfo             │█░░░░░░░░░░░░░░░░░░░ │   4%
572K         └── America            │█░░░░░░░░░░░░░░░░░░░ │   1%
```

This shows which directories consume the most space, helping identify unnecessary files.

## Further Reading

- [unbase_oci GitHub Repository](https://github.com/gardenlinux/unbase_oci) — Tool for creating bare container images

## Related Topics

<RelatedTopics />
