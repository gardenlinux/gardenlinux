# Garden Linux Build Scripts

## build system recommendations

    min 2 Cores
    min. RAM 16 GB (image is built in RAM)
    min. 5 GB free disk space  

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
