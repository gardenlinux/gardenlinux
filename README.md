# Garden Linux Build Scripts

## Documentation

Install required packages using apt:

    apt install git build-essential dosfstools docker sudo

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
