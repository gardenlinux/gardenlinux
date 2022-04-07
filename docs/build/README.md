
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

# Introduction

Garden Linux offers pre-built images via the [Github Release feature](https://github.com/gardenlinux/gardenlinux/releases )in non-regular intervals.
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

In general, the `build.sh` starts and prepares the build container, in which `garden-build` and `garden-test` are executed.

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
To create a package from a git source that contains already the `debian` files you need to:

1. create a gitlab repository in the gardenlinux group
2. add a `.gitlab-ci.yml`, for example:
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
3. Add a (unique) git tag to the repository. The git tag must contain the correct version name.

## Snapshot Source

To create a new package version that is compatible with old runtime dependency (e.g. glibc), 
you need to:

1. Create a gitlab repository, or a branch if there exists already a gitlab repo for a non-backported version
2. Copy the relevant pipelines to the new gitlab repo/branch
   1. https://gitlab.com/gardenlinux/gardenlinux-package-build/-/blob/main/pipeline/build.yml
3. Modify the pipelines to use 
   1. a specific snapshot docker image for the build, for example: `debian:unstable-20211011-slim`
   2. a specific apr repository for the build, for example: `deb http://snapshot.debian.org/archive/debian/20211028T151025Z/ bookworm main`
4. Download and install additional dependencies from snapshot.debian.org, for example `https://snapshot.debian.org/archive/debian/20211028T151025Z/pool/`
5. Configure the .gitlab-ci.yml of the new gitlab repo/branch to use the local versions of the pipelines
```
include:
- project: gardenlinux/gardenlinux-package-build
  file:
  - pipeline/workflow.yml
- local: .gitlab/ci/source.yml
- local: .gitlab/ci/build.yml
``` 



