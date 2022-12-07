
**Table of Content**
- [Introduction](#introduction)
- [Building](#building)
  - [Build via make (recommended)](#build-via-make-recommended)
  - [Build via build.sh](#build-via-buildsh)
  - [Build Artifacts](#build-artifacts)
    - [Output files](#output-files)
    - [Output image types](#output-image-types)
    - [Naming of output files](#naming-of-output-files)
  - [Build in an air-gapped environment](#build-in-an-air-gapped-environment)
    - [Requirements](#requirements)
      - [Build tools](#build-tools)
      - [Container Runtime Environment (CRE)](#container-runtime-environment-cre)
    - [Sources](#sources)
      - [Container images](#container-images)
      - [Example](#example)
- [Kernel Module](#kernel-module)
  - [build-kernelmodule container](#build-kernelmodule-container)
- [Package Build](#package-build)
  - [Git Source](#git-source)
  - [Snapshot Source](#snapshot-source)
- [Customize](#customize)
  - [Local Packages](#local-packages)
  - [Replace Kernel](#replace-kernel)

# Introduction

Garden Linux offers pre-built images via the [Github Release feature](https://github.com/gardenlinux/gardenlinux/releases) in non-regular intervals.
The following section explains how to create your own build.
Creating your own build also allows to customize the image to your requirements.

# Building

## Build via make (recommended)
Use the [Makefile](/Makefile) to build a Garden Linux Image with a pre-defined set of features.
```
# Example
make metal_dev
```
For more targets, simply run `make generate-targets` which generates the defaults build targets in `make_targets.cache`. The build targets call the [build.sh](/build.sh) with a pre-defined set of features.

You can also customize the build target to your needs, e.g. by adding a feature, platform or modifier by editing the [flavours.yaml](/flavours.yaml) and rerunning `make generate-targets`. You may also pass the options directly to the

## Build via build.sh
If you really want to directly call build.sh, you can checkout [Makefile](/Makefile) for some good examples and start from there.

In general, the `build.sh` starts and prepares the build container, in which `garden-build` gets executed. Afterwards, PyTest
based unit tests are performed.

## Build Artifacts
Build artifacts are stored in the output folder (default: `.build/`). The output folder can be overwritten by appending a directory name when invoking the `build.sh` (see also: [here](https://github.com/gardenlinux/gardenlinux/blob/main/build.sh#L8) or the help output on `stdout`).

### Output files
During the build multiple output files are created. Next to the primary image (the output file may differ based on the target hyperscaler [e.g. `.vhd` for Azure or `.ova` for VMWare]) further meta files and a rootfs for debugging are created.

**Output:**
| File | Description | Example |
|----------|:-------------:|:-------------:|
| Image | The bootable image for the related architecture | kvm_dev-arm64-today-local.raw|
| rootfs| A compressed tar ball including the whole rootfs with all features | kvm_dev-arm64-today-local.tar.xz |
| rootfs SHA256 | The SHA256 checksum for the rootfs | kvm_dev-arm64-today-local.tar.xz.sha256 |
| fullfeature.info | A comma separated list oft features included the image | fullfeature.info |
| OS release file | A copy of `/etc/os-release` including all important information | kvm_dev-arm64-today-local.os-release |
| Package manifest | Containing all .deb based packages that are used | kvm_dev-arm64-today-local.manifest |

*Hint: Keep in mind, that some artifacts will only be created by certain features. Image suffixes may also differ based on the defined target hyperscaler. More information can be found within the next chapter.*

### Output image types
Overview of all possible image output filetypes regarding the defined target hyperscaler/platform:

| Hyperscaler/Platform | Suffix |
|----------|:-------------:|
| Aliyun | `.qcow2` |
| AWS | `.raw` |
| Azure | `.vhd` |
| chroot | `.tar.gz` |
| Firecracker | `.vmlinux` (kernel image) <br> `.ext4` (fs) |
| GCP | `.tar.gz` |
| KVM | `.raw` |
| OpenStack | `.vmdk` |
| VMWare | `.ova` |



### Naming of output files
The naming convention of output files is related to the Garden Linux [feature system](https://github.com/gardenlinux/gardenlinux/blob/main/features/README.md#general) where the `feature types` are represented in a hierarchy order together with the desired target hardware architecture. This results in a file name like:

```
<platform>_<feature>-<modifier>-<architecture>-<version>
```

## Build in an air-gapped environment
Garden Linux also supports building in an air-gapped environments (offline) without any further internet connectivity. However, this requires to obtain all needed dependencies before. Keep in mind, that unit tests that require external connection are unsupported, all other ones remain usable.

### Requirements
Make sure to match this requirements to build Garden Linux without any further internet connectivity.

#### Build tools
Ensure that the build system satisfies the build requirements. This may depend on the used operating system and distribution. For the common ones see also [README.md](https://github.com/gardenlinux/gardenlinux#build-requirements).

#### Container Runtime Environment (CRE)
Garden Linux heavily relies on containers for building the artifacts. Therefore, a CRE is required to build and to perform further unit tests. Currently, Podman and Docker are supported.

### Sources
At lease the following GitHub projects should be downloaded and shipped:

 * Garden Linux source (download [repository](https://github.com/gardenlinux/gardenlinux/archive/refs/heads/main.zip))

You may use the GIT, ZIP archive or any other way but keep in mind to have the tools to unarchive the files (e.g. `unzip` for the zip archive).

#### Container images
While the whole build process is done within a container the following images related to your host build architecture are needed:

 * gardenlinux/build-cert:today
 * gardenlinux/build-image:today
 * gardenlinux/base-test:today

Currently, these images are not public and need to be created on a different machine before.

#### Example
This example provides a short overview how to proceed. First, we start on a machine with internet access (called `A`). We expect to already fulfill the build requirements on both machines and may copy our container images to `B` afterwards.

On machine `A`:
```
$> mkdir gardenlinux_build
$> cd gardenlinux_build
# Get Garden Linux sources
$> wget https://github.com/gardenlinux/gardenlinux/archive/refs/heads/main.zip
$> unzip main.zip
$> cd gardenlinux/container
# Build the container images
$> make needslim
$> make build-cert
$> make build-image
$> make build-base-test
$> cd ../..
# Export container images (you may just replace docker by podman if needed)
$> docker save -o gl_slim.container gardenlinux/slim:today
$> docker save -o gl_build_cert.container gardenlinux/build-cert:today
$> docker save -o gl_build_image.container gardenlinux/build-image:today
$> docker save -o gl_base_test.container gardenlinux/base-test:today
```

You can now copy the whole `gardenlinux_build` folder to an air-gapped system (`B`) and perform an offline build by running the following commands on machine `B`:
```
$> cd gardenlinux_build
# Import container images (you may just replace docker by podman if needed)
$> docker load -i gl_slim.container
$> docker load -i gl_build_cert.container
$> docker load -i gl_build_image.container
$> docker load -i gl_base_test.container
# Create your desired image (e.g. metal)
$> cd gardenlinux
$> make metal
```

# Kernel Module
Drivers/LKMs not included in upstream linux of kernel.org can be build out of tree.

## build-kernelmodule container
We provide a build container that come with Garden Linux linux-headers installed.
These build containers have a `uname -r` wrapper installed.
This wrapper outputs the latest installed kernel header in that container.

Container is created here: https://gitlab.com/gardenlinux/driver/gardenlinux-driver-build-container

```
docker pull registry.gitlab.com/gardenlinux/driver/gardenlinux-driver-build-container/gl-driver-build:dev
```

1. Load your kernel module sources into the container
1. If the Makefile does not use `uname -r`, make sure to reference the correct kernel headers
    * e.g: ```$(MAKE) -C /lib/modules/$(BUILD_KERNEL)/build M=$(CURDIR) modules```
1. continue with the LKM build instructions


# Package Build
Packages provided via the [repository](/docs/repository/README.md) are built, signed and deployed via the Garden Linux gitlab pipelines.

The https://gitlab.com/gardenlinux/gardenlinux-package-build contains the central gitlab pipelines, used by packages in the
[Garden Linux Gitlab Group ](https://gitlab.com/gardenlinux).

## Git Source
To create a package from a git source that contains already the `Debian` files you need to:

1. create a gitlab repository in the gardenlinux group
1. add a `.gitlab-ci.yml`
1. Add a (unique) git tag to the repository. The git tag must contain the correct version name.

<details>
    <summary>Example: .gitlab-ci.yml</summary>

```
variables:
  DEBFULLNAME: "Garden Linux builder"
  DEBEMAIL: "contact@gardenlinux.io"
  BUILD_ARCH_ALL: 'true'
  SOURCE_REPO: 'https://github.com/FRRouting/frr'
  SOURCE_REPO_REF: 'frr-8.2.2'

include:
- project: gardenlinux/gardenlinux-package-build
  file:
  - pipeline/pipeline.yml
```

</details>

## Snapshot Source

To create a new package version that is compatible with old runtime dependency (e.g. glibc),
you need to:

1. Create a gitlab repository, or a branch if there exists already a gitlab repo for a non-backported version
1. Copy the relevant pipelines to the new gitlab repo/branch
    * https://gitlab.com/gardenlinux/gardenlinux-package-build/-/blob/main/pipeline/build.yml
1. Modify the pipelines to use
    * a specific snapshot docker image for the build, for example: `Debian:unstable-20211011-slim`
    * a specific apr repository for the build, for example: `deb http://snapshot.debian.org/archive/debian/20211028T151025Z/ bookworm main`
1. Download and install additional dependencies from snapshot.debian.org, for example `https://snapshot.debian.org/archive/debian/20211028T151025Z/pool/`
1. Configure the .gitlab-ci.yml of the new gitlab repo/branch to use the local versions of the pipelines


<details>
    <summary>Example: .gitlab-ci.yml</summary>

```
include:
- project: gardenlinux/gardenlinux-package-build
  file:
  - pipeline/workflow.yml
- local: .gitlab/ci/source.yml
- local: .gitlab/ci/build.yml
```

</details>

# Customize
When customizing your own build of Garden Linux you may want to add your own packages that are not in the Garden Linux repository or add your own kernel.

## Local Packages
To install locally build packages, that are not available in the Garden Linux repository, the build pipeline offers an easy way to add own packages.
To make a package available create the directory `local_packages` in the root of the Garden Linux directory where the `build.sh` is located.
Place all you own packages in that directory and add the package name (the package name is the name you would use to install it via `apt` and not the
file name of the package) to the `pkg.include` file of the feature that needs the package.

*Hint: You may also define a remote URL to a .deb package within the `pkg.include` file like `https://repo.gardenlinux.io/mirror/vim/vim.deb`.*

## Replace Kernel
Building a Garden Linux image with more than one kernel install is not supported. In general it should work with legacy boot, but with uefi boot it
will not be possible to choose the kernel at boot time since Garden Linux does not offer a menu for that. With the `_readonly` or `_secureboot` feature
enabled the image build will fail. The recommended way to use a custom kernel is to replace the default kernel.

To replace the Garden Linux kernel with a custom kernel, place the package with the custom kernel in the `local_packages` directory as describe in the
[Local Packages](#local-packages) chapter. For the next steps we recommend to create your own new feature in the [features](/features) directory and
place a `pkg.include`, `pgk.exclude` and an `info.yaml` in your feature directory. Last but not least add your new feature to the build target you are
building in the [Makefile](/Makefile).

The `pkg.include` file should contain the package name of the custom kernel you placed in the `local_packages` directory and any other package you
wish to install. The `pkg.exclude` file must contain the package name of the default kernel that normally would be installed. Also, you can exclude
any other package here you do not want in the Garden Linux image. To find the package name of the default kernel check the `pkg.include` files of the
[cloud](/features/cloud/pkg.include), [metal](/features/metal/pkg.include) or [firecracker](/features/firecracker/pkg.include) feature, depending of
what flavor of Garden Linux you want to build. To make a directory in the [features directory](/features) a [feature](/features/README.md), it must
contain an `info.yaml` file.

<details>
    <summary>Example: info.yaml</summary>

```
description: "custom changes"
type: flag
```

</details>

For more options take a look at the [info.yaml](/features/example/info.yaml) in the example feature.