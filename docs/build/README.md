
**Table of Content**
- [Introduction](#introduction)
	- [Build via make (recommended)](#build-via-make-recommended)
	- [Build via build.sh](#build-via-buildsh)
	- [Build Artifacts](#build-artifacts)
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

## Build via make (recommended)
Use the [Makefile](/Makefile) to build a Garden Linux Image with a pre-defined set of features. 
```
# Example 
make metal-dev
```
For more targets, checkout the [Makefile](/Makefile). The targets call `build.sh` with a pre-defined set of features.  

You can also customize a Makefile target to your needs, e.g. by adding a feature.

## Build via build.sh 
If you really want to directly call build.sh, you can checkout [Makefile](/Makefile) for some good examples and start from there.

In general, the `build.sh` starts and prepares the build container, in which `garden-build` gets executed. Afterwards, PyTest
based unit tests are performed.

## Build Artifacts
Build artifacts are stored in the output folder (default `.build/`).
Some artifacts will only be created by certain features. 

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
The Garden Linux build pipeline offers some features to easily customize your own build of Garden Linux.



## Local Packages
To install locally build packages, that are not available in the Garden Linux repository the build pipeline offers an easy way to add own packages.
To make a package available create the directory `local_packages` in the [root](/) of the Garden Linux directory where the `build.sh` is located.
Place all you own packages in that directory and add the package name (the package name is the name you would use to install it via `apt` and not the
file name of the package) to the `pkg.include` file of the feature that needs the package.

## Replace Kernel
Building a Garden Linux image with more than one kernel install is not supported. In general it should work with legacy boot, but with uefi boot it
will not be possible to choose the kernel at boot time since Garden Linux does not offer a menu for that. With the _readonly or _secureboot feature
enabled the image build will fail. The recommended way to use a custom kernel is to replace the default kernel.

To replace the Garden Linux kernel with a custom kernel place the package with the custom kernel in the `local_packages` directory as describe in the
[Local Packages](#local-packages) chapter. For the next steps we recommend to create your own new feature in the [features](/features) directory and
place a `pkg.include`, `pgk.exclude` and an `info.yaml` in your feature directory. Last but not least add your new feature to the build target you are 
building in the [Makefile](/Makefile).

The `pkg.include` file should contain the package name of the custom kernel you placed in the `local_packages` directory and any other package you
wish to install. The `pkg.exclude` file must contain the package name of the default kernel that normally would be installed, also you can exclude
any other package here you do not want in the Garden Linux image. To find the package name of the default kernel check the `pkg.include` files of the
cloud, metal or firecracker feature, depending of what flavor of Garden Linux your want to build. To make a directory in the [features](/features)
directory a feature it must contain an `info.yaml` file, a minimal example looks like this.

```example info.yaml
description: "custom changes"
type: flag
```
For more options take a look at the [info.yaml](/features/example/info.yaml) in the example feature.