---
title: Driver 
weight: 10
disableToc: false
---

Drivers/LKMs not included in upstream linux of kernel.org can be build out of tree.

## build-kernelmodule container 

The ```gardenlinux/build-kernelmodule:$(KERNEL_VERSION)``` container comes with pre-installed kernel headers for the respective kernel version.

Before building this container, the following packages are required to be available under ```.packages/main/l/linux/```

- ```linux-kbuild*$(KERNEL_VERSION)*.deb ```
- ```linux-compiler-gcc*$(KERNEL_VERSION)*.deb ```
- ```linux-headers*$(KERNEL_VERSION)*.deb ```

The ```KERNEL_VERSION``` variable is set in docker/Makefile. 

## manual LKM/Driver build

1. Load your LKM sources into the container
1. Make sure the LKM Makefile uses the kbuild system preinstalled in the container 
    * e.g: ```$(MAKE) -C /lib/modules/$(BUILD_KERNEL)/build M=$(CURDIR) modules```
1. continue with the LKM build instructions

