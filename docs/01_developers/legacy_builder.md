# Legacy Builder

Garden Linux's earlier versions are built with legacy tooling, distinct from the tools used in more recent versions. 
This guide provides instructions on how to rebuild these older versions using the Legacy Builder, ensuring compatibility and maintaining the integrity of the original builds.


## Quickstart 

```shell
git checkout rel-934
make clean
make aws-prod
```

## Build Garden Linux Images with Legacy Builder
To build all supported images you may just run the following command:
```
    make all
```

However, to save time you may also build just a platform specific image by running one of the following commands. Related dev images can be created by appending the '-dev' suffix (e.g. "make aws-dev"), or the `-prod` suffix for re-building production images.
```
    make aws
    make gcp
    make azure
    make ali
    make vmware
    make openstack
    make kvm
    make metal
```

Artifacts are located in the `.build/` folder of the project's build directory.

## Production Flavors

Garden Linux supports all major cloud platforms and bare metal VMs. 
The following table shows the released Garden Linux flavors and how to re-build them

| Make Command          | Cloud Platform |
|-----------------------|----------------|
| `make ali-prod`       | Alibaba Cloud  |
| `make aws-prod`       | Amazon Web Services (AWS) |
| `make azure-prod`     | Microsoft Azure|
| `make gcp-prod`       | Google Cloud Platform (GCP) |
| `make kvm-prod`       | Kernel-based Virtual Machine (KVM) |
| `make metal-prod`     | Bare Metal    |
| `make openstack-prod` | OpenStack     |
| `make vmware-prod`    | VMware        |
