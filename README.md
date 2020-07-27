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
</p>
<hr />

Garden Linux is a [Debian](https://debian.org) derivat that aims to provide a small, autitable linux image for most Cloud Providers and Bare Metal.

## Features:
- easy to use build System for images
- build are repeatable and auditable
- small footprint (based on minbase of Debian)
- subscribes for debian/testing, so no huge (problematic) version jumps needed
- whole setup is purely systemd based (network, fstab etc.) [#101](https://github.com/gardenlinux/gardenlinux/issues/101) [#102](https://github.com/gardenlinux/gardenlinux/issues/102)
- initramfs is dracut generated [#105](https://github.com/gardenlinux/gardenlinux/issues/105)
- optional complete immutability [#104](https://github.com/gardenlinux/gardenlinux/issues/105)
- regular updates (since the whole build process is completly automated via a Tekton CI) and
- thoroughfull automated testing
  - unit tests against the local build and
  - integration tests against the various cloud Providers (only rc builds)
- aiming always to integrate the lates LTS kernel [#100](https://github.com/gardenlinux/gardenlinux/issues/100) (currently 5.4)
- running scans against against common issues like
  - License voilations (we try to be completely open! [#1](https://github.com/gardenlinux/gardenlinux/issues/1))
  - Scans for outdated software versions
- project licensed under [MIT](https://github.com/gardenlinux/gardenlinux/blob/master/LICENSE)
- supporting major platforms out-of-the-box
  - major cloud providers AWS, Azure, Google, Alicloud
  - major virtualizer VMware, OpenStack, KVM
  - bare metal

## Build Requirements

All the build runs in a docker conainter (well a privileged on with extended capabilities - since we need loop back support)
We can run on any system supporting Docker and having loopback support and has

- 2+ GiB (use RAM-disk; use fs with sparse-file support)
- 10+ GiB free disk space

required packages are (on Debian/Ubuntu):
    apt install docker.io make

Recommended packages for to run recommended supporting services (like a build cache) and extended test (virtualize image runs)

    apt install docker-compose qemu-system-x86

## Quick start

Build all images:

    make all

Build specific platform specic images:

    make aws
    make gcp
    make azure
    make ali
    make vmware
    make openstack
    make kvm
    make metal

See in `build/` folder for the outcome

## Customize builds

Our build ist based on a [feature system](features/README.md).

The feature sytem distinguishes between
- Platforms (aws, azure, google ...)
- Features (container host, virtual host ...)
- Modifiers (_slim. _readonly, _pxe ...)

if you want to manually build choose:

    build.sh <Platform>,[<feature1>],[<featureX>],[_modifier1],[_modifierX] destination [version]

    e.g. build.sh server,cloud,chost,vmware build/

builds an Server image, cloud-like, with a container host for the Platform VMware. The build result can be found in `build/`

also look into our [Version scheme](VERSION.md) since adding a date or a Version targets the whole build for a specific date
