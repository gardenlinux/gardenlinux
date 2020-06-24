<p align="center">
 <a href="https://www.gardenlinux.io/">
  <img
     src="https://raw.githubusercontent.com/gardenlinux/gardenlinux/master/logo/gardenlinux-logo-black-text.svg"
     width="380"
  />
 </a>
</p>

<hr />
<p align="center">&bull;
    <a href="#build-system-recommendations">Build System Recommendations</a> &bull;
    <a href="#documentation">Documentation</a> &bull;
</p>
<hr />

Garden Linux is a [Debian](https://debian.org) derivat that aims to provide a small, autitable linux image for most Cloud Providers and Bare Metal.

### Features:
- easy to use build System for images
- build are repeatable and auditable
- small footprint (based on minbase of Debian)
- subscribes for debian/testing, so no huge (problematic) version jumps needed and expected
- whole setup is purely systemd based (network, fstab etc.) [#101](https://github.com/gardenlinux/gardenlinux/issues/101) [#102](https://github.com/gardenlinux/gardenlinux/issues/102)
- initramfs is dracut generated [#105](https://github.com/gardenlinux/gardenlinux/issues/105)
- optional complete immutability [#104](https://github.com/gardenlinux/gardenlinux/issues/105)
- regular updates (since the whole build process is completly automated) and
- thoroughfull automated testing
  - unit tests against the local build and
  - integration tests against the various cloud Providers (only rc builds)
- aiming always to integrate the lates LTS kernel [#100](https://github.com/gardenlinux/gardenlinux/issues/100) (currently 5.4)
- running scans against against common issues like
  - License voilations (we try to be completely open! [#1](https://github.com/gardenlinux/gardenlinux/issues/1))
  - Scans for outdated software versions
- project licensed under [MIT](https://github.com/gardenlinux/gardenlinux/blob/master/LICENSE)

## Build System Recommendations

All the build runs in a docker conainter (well a privileged on with extended capabilities - since we need loop back support)
We can run on any system supporting Docker and having loopback support and has

- 2+ GiB (use RAM-disk; use fs with sparse-file support)
- 10+ GiB free disk space

required packages are (on Debian/Ubuntu):
    apt install docker.io make

Recommended packages for to run recommended supporting services (like a build cache) and extended test (virtualize image runs)

    apt install docker-compose qemu-system-x86

## Documentation

Build all images:

    make all

Build specific images:

    make aws
    make gcp
    make azure
    make vmware
    make openstack
    make vmware
    make kvm
