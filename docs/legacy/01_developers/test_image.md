## Testrun your previously created PXE-Build (raw file)

This is an easy way to test your build on most systems. A handy way to run gardenlinux is via PXE-Boot. Gardenlinux provides a script to run your build with qemu, e.g. qemu-system-x86_64. 
This script should run on all kinds of devices. No need for root privileges.

This file is located at gardenlinux/bin/start-vm.

There's no need to change any other files for this Virtualization Test.

#### prerequisites:

1. you successfully built gardenlinux with feature _pxe into an outputfolder now named $pxepath, e.g. gardenlinux/.build
2. this path contains at least those files: 
- rootfs.squashfs
- rootfs.vmlinuz
- rootfs.initrd
- *.raw (the image file)
3. (optional) define ignition file (e.g. for creating users to login)

#### run:

1. start Gardenlinux with

	`gardenlinux/bin/start-vm --ignfile /path/to/ignition.json --pxe $pxepath`

2. (Stop Gardenlinux Virtualization by pressing Ctrl+A, then X)


## Testing .raw Build with ignition without PXE

`gardenlinux/bin/start-vm --ignfile /path/to/ignition.json <filename>.raw`


#### Additional Links/Info
- run `gardenlinux/bin/start-vm --help`
- https://docs.fedoraproject.org/en-US/fedora-coreos/producing-ign/


---
## Test .iso Build
This does not fully work yet - use the branch named "iso" for building and testing.
You should be able to successfully build the .iso file, as always by adding _iso feature.

it is planned to also be able to test it by running

	`gardenlinux/bin/start-vm gardenlinux/.build/metal_iso-amd64-dev-local.iso`

but it is not fully supported, yet.

in the meanwhile the following command should work (choose the right .iso file, this example used metal-iso)

	`qemu-system-x86_64 -boot d -cdrom .build/metal_iso-amd64-dev-local.iso -m 2048 -nographic`

(exchange qemu_system_x86_64 with qemu_system_x86 if you use a x86 machine)

(You can also exit QEMU by typing Ctrl+A, X)

## Alternative Way for testing .raw Build:

	qemu-system-x86_64 -drive format=raw,file=gardenlinux/.build/<filename>.raw -m 2048 -nographic


   
