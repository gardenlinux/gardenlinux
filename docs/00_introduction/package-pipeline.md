# The Garden Linux Package Pipeline

Garden Linux is based on [Debian](https://www.debian.org), but it has a unique design for how packages are built.
This pipeline might look overly complex on first sight, but is based on it's requirements and past experience.
This document aims to explain the decisions and tradeoffs made.

## The bigger picture

Garden Linux release artifacts are disk images for various platforms such as kvm, cloud providers or bare metal hardware.
To build those artifacts, Garden Linux makes use of an [APT repository](https://wiki.debian.org/DebianRepository).
APT is the Debian package management tool.

## Qualities of the Garden Linux package pipeline

Based on previous experience, the design goals of our package pipeline are the following:

- We want to ship a stable operating system with a modern software stack
- We want the latest LTS linux kernel with all the Debian benefits as described in [Linux Kernel](./kernel.md)
- We want to be able to reproduce release artifacts (disk images) and patch individual packages as needed
- We require updated packages (rebuilt from source, with patches applied) to be absolutely binary compatible with existing releases
  - This is a challenge because Garden Linux is based on Debian *Testing* where components such as libc or the go compiler might change in incompatible ways without prior notice
- We want the pipeline to work with short-lived (ephemeral) runners or any machine with a Linux container runtime, so no long-lived vm is needed for the process
- We require the APT repos to be consistent. For this reason, APT repo distributions (like `1443.8`) must be immutable.
- We need to keep the required tooling providers low. In the past, complex setups lead to integration issues. Our new tooling is fully geared towards containerized environments, allowing it to run on developer laptops and on most CI systems.

## Package pipeline overview

A technical [process overview is found in the gardenlinux/repo readme](https://github.com/gardenlinux/repo/blob/main/README.md).

We create and update a mirror of the Debian Testing APT repository multiple times a day.
For each *snapshot* of the APT mirror, a corresponding *container image* is built from this specific version.
Using those container images, new Debian packages can be built with the exact same version of dependencies.
We don't need to rebuild all packages as those packages that we don't need to rebuild, we can just reuse the binary packages by debian to avoid wasted resources for recompiling.
Due to our APT snapshot we avoid accidental updates of packages, ensuring full binary compatibility.
Packages with known security weaknesses are rebuilt using the latest patch or mitigation enabled.
Package rebuilds happen on GitHub Actions using our snapshot container image.
Due to the containerized nature of the build, running a build locally is easy if you have a Linux container runtime available.
Because the rebuild happens in a snapshot container, the produced package is binary compatible to the given Garden Linux release.
