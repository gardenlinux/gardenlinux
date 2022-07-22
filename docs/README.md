
# Documentaion
Everything that is not included in the main [../README.md](../README.md),
should be described or referenced in the `docs/` folder. 

- [Documentaion](#documentaion)
  - [Build System](#build-system)
  - [Feature System](#feature-system)
  - [Test](#test)
  - [Pipelines](#pipelines)
  - [Offical Garden Linux Releases](#offical-garden-linux-releases)
  - [Deploy](#deploy)
  - [Software packages](#software-packages)
  - [Linux Kernel](#linux-kernel)
  - [Troubleshooting](#troubleshooting)
  - [FAQ](#faq)

## Build System

We recommend to first checkout the [Quick Start](../README.md#quick-start) Guide, it will run you through a Garden Linux build step by step. If you need to understand the build system, please refer to the [build-system.md](build-system.md)

## Feature System

Garden Linux OS is composed of features. The Garden Linux Maintainers define and maintain the feature sets for the official releases.
See [releases](#offical-garden-linux-releases) chapter for more information on official releases.

The easiest method to customize Garden Linux in a reproducible way, is to work with the feature system.
Either by creating a new feature and add it to your feature set of your target build image,
or by modifying existing features to your needs. Documentation for the feature system can be found in [../features/README.md](../features/README.md).

## Test

The `tests/` folder provides a self-contained test environment for Garden Linux.
It is used by the Garden Linux build system for unit tests, integration and platform tests.
Documentation can be found [here](../tests/README.md).

## Pipelines

:construction: Pipelines are under construction. :construction:	
GitHub Pipeline (build & test) -> Upload to S3 -> Tekton pipeline (publish)
 
### Github Pipeline
Documentation TODO.

### Tekton Pipeline
Documented [here](../ci/README.md)

## Offical Garden Linux Releases
The following cloud platforms are officially supported by Garden linux.

| Name                      | Garden Linux Feature              |
|---------------------------|-----------------------------------|
| Amazon Web Services (aws) | [aws](../features/aws)             |
| Microsoft Azure (azure)   | [azure](../features/azure)         |
| Google Cloud Platform     | [gcp](../features/gcp)             |
| Alibaba Cloud             | [ali](../features/ali)             |
| metal                     | [metal](../features/metal)         |
| Openstack CCEE            | [openstack](../features/openstack) |
| VMware vSphere            | [vmware](../features/vmware)       |


The release cycle is currently reworked, documentation update will follow.

## Deploy

Garden Linux is installable on desktop machines, all relevant cloud providers and most known virtualization solutions.
Export your freshly build raw image or use the well known iso format, or deploy it via PXE Boot.

- [ipxe](deploy/ipxe-install.md)
- [openstack](deploy/openstack.md)
- [vmware ova](deploy/vmware-ova.md)
- [manual / non default](deploy/install-non-default.md)


## Software packages
Packages are maintained in separate gitlab repositories. 
Each package repository has a `.gitlab-ci.yaml` that defines the pipeline process for that package.
The Gitlab pipeline definitions are maintained and documented [here](https://gitlab.com/gardenlinux/gardenlinux-package-build).
However, a package repo may use custom pipeline stages defined locally in their respective repostiroy of that package. 

Packages are eventually published to an apt repository; repo.gardenlinux.io.
This apt repository is used by the Garden Linux build system to retrieve software for Garden Linux.
See [Gitlab package build docs](https://gitlab.com/gardenlinux/gardenlinux-package-build/-/tree/main/docs) for further details.


## Linux Kernel
Garden Linux aims towards a complete open, reproducible and easy-to-understand solution. That also    
includes all activities around the Kernel. [Kernel.org](https://kernel.org) is the source of the official
Linux kernels and therefore all kernels in Garden Linux are mainly based on this. Not to forget our   
Debian roots: we integrate with the build environment [Debian kernels](https://wiki.debian.org/Kernel) to
support the Debian feature set to be compatible. Garden Linux tries to keep the amount of patches in   
the kernel diverging from Debian and kernel.org low, so everybody can easily support the Garden Linux 
kernel and no deep knowledge of Garden Linux internals is needed. In contrast to Debian, Garden Linux 
integrates always with the latest Long Term Support kernel (LTS) and maintains this kernel at least   
for one overlapping period till the next kernel will be available. You can find the release categories
and the time schedule for LTS releases also on [kernel.org](https://www.kernel.org/category/releases.html).
Garden Linux aims to integrate the latest long term release. 

Our current maintained kernel versions can be found here:
- [Linux 5.10](https://gitlab.com/gardenlinux/gardenlinux-package-linux-5.10)
- [Linux 5.15](https://gitlab.com/gardenlinux/gardenlinux-package-linux-5.15)

A config list is maintained per kernel project, which explicitly enables (and tests) `CONFIG_` flags. 
The Debian kernel sources which Garden Linux bases on, can be found in [here](https://salsa.debian.org/kernel-team/linux)

## Troubleshooting

In the [troubleshooting.md](troubleshooting.md) document you will find solutions for common and uncommon issues related to your build environment. If you are facing runtime issues with Garden Linux please open a Github Issue.

## FAQ

### How can I contribute?

Please read [../CONTRIBUTING.md](../CONTRIBUTING.md) if you want to contribute to the Garden Linux project.

### Why does Garden Linux not integrate the mainline stable?                                           
                                                                                                      
Mainline stable introduces features to the new Linux kernel, which happens every ~2 months. Some of   
those features affect the way e.g. container or network environment interact with the kernel and need 
some time to be adopted in surrounding tooling. Also some other feature introduce bugs, recognized    
after release and need to be reverted or other changes. In short: to avoid this we wait until a kernel
version becomes a longterm stable and try to integrate always the latest long term stable and the one 
before to have a decent deprecation phase. Garden Linux takes advantage of these patches.             
                                                                                                      
### A new long term kernel is released, when will it be integrated?                                    
                                                                                                      
We are probably on it, but feel free to open a Github issue.

### Why does Garden Linux use Debian kernel patches and configuration?                                 
                                                                                                      
Debian is free and open source software. There are good reasons                                       
https://www.debian.org/intro/why_debian to use Debian. In the following we explain our reasons in the 
kernel context.                                                                                       
                                                                                                    
First, Debian provides an enterprise grade server operating system, while protecting the claim to stay
100% free and open source. Debian is rigorous when it comes to non-free software licenses, also when it
comes to the Linux Kernel. A prominent example of what this means, is the extraction of non-free      
firmware from the Linux Kernel.                                                                       
                                                                                                    
Debian scans licenses and patches out everything that violates the claim to stay 100% free. Since     
Garden Linux shares this approach, we benefit from Debian patches.                                    
                                                                                                    
Additionally, Debian maintains a sane kernel configuration, which is used by Garden Linux as base.
