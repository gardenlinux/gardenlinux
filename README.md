# Garden Linux Build Scripts

## Documentation

Install required packages using apt:

    apt install git build-essential dosfstools docker suod

Build all images:

    make all

Build specific images:

    make aws
    make gcp
    make azure
    make vmware
    make openstack
    make kvm

