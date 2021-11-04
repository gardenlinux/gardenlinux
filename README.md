<p align="center">
 <a href="https://www.gardenlinux.io/">
  <img
     src="https://raw.githubusercontent.com/gardenlinux/gardenlinux/main/logo/gardenlinux-logo-black-text.svg"
     width="380"
  />
 </a>
</p>

<hr />
<p align="center">&bull;
    <a href="#Features">Features</a> &bull;
    <a href="#build-requirements">Build Requirements</a> &bull;
    <a href="#quick-start">Quick Start</a> &bull;
    <a href="#customize-builds">Customize</a> &bull;
    <a href="#garden-linux-releases">Releases</a> &bull;
</p>
<hr />

[![CII Best Practices](https://bestpractices.coreinfrastructure.org/projects/3925/badge)](https://bestpractices.coreinfrastructure.org/projects/3925)

Garden Linux is a [Debian](https://debian.org) derivate that aims to provide a small, auditable linux image for most Cloud Providers and Bare Metal.

## Features:
- easy to use build system for OS images
- builds are repeatable and auditable
- small footprint (based on minbase of Debian)
- subscribes for debian/testing, so no huge (problematic) version jumps needed
- whole setup is purely systemd based (network, fstab etc.) [#101](https://github.com/gardenlinux/gardenlinux/issues/101) [#102](https://github.com/gardenlinux/gardenlinux/issues/102)
- initramfs is dracut generated [#105](https://github.com/gardenlinux/gardenlinux/issues/105)
- optional complete immutability [#104](https://github.com/gardenlinux/gardenlinux/issues/105)
- regular updates (since the whole build process is completely automated via a Tekton CI) and
- thorough automated testing
  - unit tests against the local build and
  - integration tests against the various cloud Providers (only rc builds)
- aiming to always integrate the latest LTS kernel [#100](https://github.com/gardenlinux/gardenlinux/issues/100) (currently 5.4)
- running scans against common issues like
  - license voilations (we try to be completely open! [#1](https://github.com/gardenlinux/gardenlinux/issues/1))
  - scans for outdated software versions
- project licensed under [MIT](https://github.com/gardenlinux/gardenlinux/blob/master/LICENSE)
- supporting major platforms out-of-the-box
  - major cloud providers AWS, Azure, Google, Alicloud
  - major virtualizer VMware, OpenStack, KVM
  - bare metal

## Build Requirements

The entire build runs in a docker container (well a privileged one with extended capabilities - since we need loop back support)
We can run on any system supporting Docker and having loopback support and has

- 2+ GiB (use RAM-disk; use fs with sparse-file support)
- 10+ GiB free disk space
- Internet connection to access snapshot.debian.org and repo.gardenlinux.io

### Required packages for a convenient build (on Debian/Ubuntu):

`apt install bash docker.io docker-compose make coreutils gnupg git qemu-system-x86`

### Required packages for deployment on cloud services:

`apt install python3`

- Alicloud: [Aliyun CLI](https://github.com/aliyun/aliyun-cli)
- AWS: [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- Azure: [Azure CLI](https://docs.microsoft.com/de-de/cli/azure/install-azure-cli-apt)
- GCP: [Cloud SDK](https://cloud.google.com/sdk/docs/quickstart?utm_source=youtube&utm_medium=Unpaidsocial&utm_campaign=car-20200311-Quickstart-Mac#linux), [gsutil](https://cloud.google.com/storage/docs/gsutil_install?hl=de#install)
- OpenStack: [OpenStackCLI](https://github.com/openstack/python-openstackclient)

### Required kernel modules

ext4, loop, squashfs, vfat, vsock (for VM image builds and extended virtualized tests)

### Required packages to configure the CI pipeline

`apt install bash git python`

`pip install tekton`

## Quick start

Build all images:

    make all

Building specific platform images:

    make aws
    make gcp
    make azure
    make ali
    make vmware
    make openstack
    make kvm
    make metal

See in `.build/` folder for the outcome, there are subdirectories for the platform and the build date.

## Customize builds

Our build is based on a [feature system](features/README.md).

The feature system distinguishes between
- Platforms (aws, azure, google ...)
- Features (container host, virtual host ...)
- Modifiers (_slim. _readonly, _pxe ...)

if you want to manually build choose:

    build.sh <Platform>,[<feature1>],[<featureX>],[_modifier1],[_modifierX] destination [version]

    e.g. build.sh server,cloud,chost,vmware build/

builds a server image, cloud-like, with a container host for the VMware platform. The build result can be found in `build/`

also look into our [Version scheme](VERSION.md) since adding a date or a Version targets the whole build for a specific date


## Garden Linux releases

Garden Linux frequently publishes snapshot releases. These are available as machine images in most major cloud providers as well as
file-system images for manual import. See the [releases](docs/releases.md) page for more info.

## Pipeline Integration
Garden Linux can build in an automated way for continous integration. See [ci/README.md](ci/README.md) for details.
