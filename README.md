<p align="center">
 <a href="https://www.gardenlinux.io/">
  <img
     src="https://raw.githubusercontent.com/gardenlinux/gardenlinux/master/logo/gardenlinux-logo-black-text.svg"
     width="380"
  />
 </a>
</p>

<hr />
<p align="center">
    <a href="#build-system-recommendations">Build System Recommendations</a>
    <a href="#documentation">Documentation</a>
    <a href="#license">License</a>
</p>
<hr />

## Build System Recommendations

- 2+ GiB (use RAM-disk; use fs with sparse-file support)
- 10+ GiB free disk space

## Documentation

Install required packages using apt:

    apt install docker.io make

Install recommended packages for better build performance and tests in a virtualizer

    apt install docker-compose qemu-system-x86

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

## License

Copyright 2020 by SAP SE
