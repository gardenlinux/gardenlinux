---
title: Driver 
weight: 10
disableToc: false
---

Drivers/LKMs not included in upstream linux of kernel.org can be build out of tree.

## build-kernelmodule container 
We provide build container that come with gardenlinux linux-headers installed. 
These build containers have a `uname -r` wrapper installed. 
This wrapper outputs the latest installed kernel header in that container.

Container is created here: https://gitlab.com/gardenlinux/driver/gardenlinux-driver-build-container


```
docker pull registry.gitlab.com/gardenlinux/driver/gardenlinux-driver-build-container/gl-driver-build:dev
```

## manual kernel module build

1. Load your kernel module sources into the container
1. If the Makefile does not use `uname -r`, make sure to reference the correct kernel headers
    * e.g: ```$(MAKE) -C /lib/modules/$(BUILD_KERNEL)/build M=$(CURDIR) modules```
1. continue with the LKM build instructions

