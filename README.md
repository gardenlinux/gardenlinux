# Garden Linux Build Scripts

## build system reocmmendations

    min 2 Cores
    min. RAM 16 GB (image is built in RAM)
    min. 5 GB free disk space  

## Documentation

Install required packages using apt:

    apt install git build-essential dosfstools docker.io docker sudo

Build all images:

    sudo make all

Build specific images:

    sudo make aws
    sudo make gcp
    sudo make azure
    sudo make vmware
    sudo make openstack
    sudo make kvm

## License

Copyright 2020 by SAP SE
