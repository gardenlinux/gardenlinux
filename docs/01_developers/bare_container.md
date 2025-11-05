# Garden Linux Bare Container Documentation

## Overview
Garden Linux offers a range of specialized bare container images, each tailored for specific applications and designed for minimalism and security:

- **Bare-libc**: Ideal for C/C++ applications requiring only essential C runtime libraries.
- **Bare-python**: Equipped with Python runtime, perfect for Python-based applications.
- **Bare-sapmachine**: Customized for sapmachine with necessary libraries and binaries.
- **Bare-nodejs**: Includes Node.js environment, suitable for server-side JavaScript applications.

These containers are optimized as base images for Dockerfiles. 
Their development is streamlined by the [unbase_oci](https://github.com/gardenlinux/unbase_oci) tool, which efficiently minimizes image size by removing unnecessary components from base container images.

### Unbase OCI Tool
- **Description**: The `unbase_oci` tool is instrumental in the development of these "bare" container images. 
- **Functionality**:
  - Strips unnecessary components from base container images.
  - Reduces image size and potential security vulnerabilities.
  - Operates on OCI archives, comparing base and target images to identify and retain only necessary additions and their dependencies.
- **Repository Link**: [unbase_oci](https://github.com/gardenlinux/unbase_oci)
- **Impact**: This tool is pivotal in creating streamlined, "distroless-like" images, ensuring that the resulting containers are lean and secure.

### Bare-libc
- **Description**: A streamlined container image for applications that need only the basic C library.
- **Features**:
  - Includes essential C runtime libraries.
  - Suited for C/C++ applications with minimal dependencies.
  - Enhanced security through a minimal attack surface.
- **Container Link**: [bare-libc](https://github.com/orgs/gardenlinux/packages/container/package/gardenlinux%2Fbare-libc)

### Bare-python
- **Description**: Optimized for Python applications, this image provides the Python runtime.
- **Features**:
  - Contains the Python interpreter and necessary libraries.
  - Ideal for Python-based applications.
  - Designed for improved security and efficiency.
- **Container Link**: [bare-python](https://github.com/orgs/gardenlinux/packages/container/package/gardenlinux%2Fbare-python)
- **Usage in Dockerfile**:
  ```Dockerfile
  FROM ghcr.io/gardenlinux/gardenlinux/bare-python:nightly
  COPY hello.py /
  CMD ["python3", "/hello.py"]
  ```

### bare-sapmachine
- **Description**: Customized for SAP applications, ensuring compatibility and optimized performance.
- **Features**:
  - Necessary libraries and binaries for SAP included.
  - Optimized for sapmachine.
  - Security-focused design.
- **Container Link**: [bare-sapmachine](https://github.com/orgs/gardenlinux/packages/container/package/gardenlinux%2Fbare-sapmachine)

### Bare-nodejs
- **Description**: A container tailored for Node.js applications, providing the Node.js runtime.
- **Features**:
  - Includes Node.js environment.
  - Suitable for server-side JavaScript applications.
  - Minimized footprint for enhanced security and performance.
- **Container Link**: [bare-nodejs](https://github.com/orgs/gardenlinux/packages/container/package/gardenlinux%2Fbare-nodejs)


## Development and Debugging Bare Containers

If a setup works in the normal container, but fails in the corresponding bare container, debugging the problem can get challenging, as the unbase_oci tool removes basic binaries like `sh`.
By following the steps in this section, you can regain the basic functionalities without rebuilding the image.

### General Setup

As the first step, we want to mount the bare image to a debian installation. As mounting does not automatically pull the image, we pull it manually:

```bash
podman image pull ghcr.io/gardenlinux/gardenlinux/bare-<flavor>:<version>
podman run --rm -it --mount type=image,src=ghcr.io/gardenlinux/gardenlinux/bare-<flavor>:<version>,dst=/mnt,rw=true debian
```

Now, you should be in the debian shell and be able see the image under `/mnt`.
You can already change things in the image and enter it's programs by executing

```bash
chroot /mnt <program>
```

### Installing Basic Utilities

To spawn a shell inside the bare image, we recommend installing [toybox](https://landley.net/toybox/), as it contains a lot of useful command line tools in a single file.
To install toybox, execute the following in the debian shell:

```bash
apt update && apt install curl -y
curl http://landley.net/bin/toybox/latest/toybox-$(uname -m) -o /mnt/bin/toybox
chmod +x /mnt/bin/toybox
```

And finally spawn a shell inside the bare image with:
```bash
chroot /mnt toybox sh
```

### Analyzing the Image Size

Bare images may unexpectedly grow. To find the cause of the issue, we can install tools to the debian container and use the on the `/mnt` folder.
For example, install dust:

```bash
apt update && apt install du-dust
```

And print the size of the directories:

```
$ dust -n 32 -w 64 -r /mnt
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

## Support and Contributions

If you need support or wish to contribute to the development of the "bare" flavor containers, including the `unbase_oci` tool, please refer to the following resources:

- **General Issues and Contributions**: For issues specific to the "bare" containers or to contribute to Garden Linux, visit the [Garden Linux GitHub Repository](https://github.com/gardenlinux/gardenlinux/pulls).
- **Specific Container Repositories**: For detailed information or contributions to individual containers, explore their respective GitHub repository pages linked in their descriptions above.

Your contributions and feedback are valuable in improving these specialized containers and tools.
