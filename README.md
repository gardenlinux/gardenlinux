# Garden Linux Build Scripts

## build system recommendations (per concurrent build)

- 2+ CPU Cores
- 2+ GiB (use RAM-disk; use fs with sparese-file support)
- 10+ GiB free disk space

## Documentation

Install required packages using apt:

    apt install git build-essential dosfstools docker.io docker sudo

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
