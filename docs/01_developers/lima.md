# Lima VM Images

[Lima](https://lima-vm.io/) is a tool for running Linux virtual machines.
Originally intended to allow running Linux containers on mac, it became a quite versatile tool for virtual machine life cycle management.
It makes it convenient to open a shell via ssh in virtual machines and can mount local directories into the virtual machine.

Lima is open source and can be used on macOS and Linux hosts.
For a general introduction to the Lima command line interface, see [the official docs page](https://lima-vm.io/docs/) or [the community-provided tl;dr page](https://github.com/tldr-pages/tldr/blob/main/pages/common/limactl.md).

Garden Linux can be used as a guest operating system with Lima.
For this, Garden Linux provides ready-built disk images and yaml manifest files.
You may use the yaml manifest as provided, or [download](https://images.gardenlinux.io/kvm_curl-lima-today.yaml) and modify it according to your needs.
See the [example configuration](https://github.com/lima-vm/lima/blob/master/examples/default.yaml) for available options.

## Motivation

> I use Garden Linux, why would I want to use it with Lima?

This depends on what you are trying to do.
If you are asking the question, you probably don't need Lima.
Using the Garden Linux image with Lima might be useful for evaluating Garden Linux as it provides a simple way to boot an Garden Linux instance as a virtual machine without needing to take care of setting up SSH for remote login.
Lima might also be useful to open a bug report in Garden Linux if you can reproduce an issue in a specific Garden Linux image.
It might be useful to track down a regression in a new Garden Linux version as it makes it easy to build identical virtual machines for different versions of Garden Linux.
It might be useful to try out if third-party software is compatible with Garden Linux.

> I use Lima, why would I want to use Garden Linux as a guest instead of any other Linux distribution?

If any of the [specific Garden Linux features](https://github.com/gardenlinux/gardenlinux?tab=readme-ov-file#features) are interesting to you, Garden Linux might be a useful guest OS for you.
It might be useful to get a small, container-focussed guest OS with a recent software stack.

## Using pre-built images

Garden Linux does offer a few pre-built disk images suitable for using as a Lima guest.

To get started, run the following commands:

```
$ limactl create --name=gardenlinux-today https://images.gardenlinux.io/kvm_curl-lima-today.yaml
$ limactl start gardenlinux-today
$ limactl shell gardenlinux-today
```

## Building images yourself

You might want to build your own disk image for example if you need features that are not part of the pre-built images available.
Let's assume you need the `nodejs` feature in your image in addition to the provided `kvm_curl-lima` features.

> [!IMPORTANT]
> When building images for use with Lima, you should always at least include the `kvm` and the `lima` feature as they provide the base requirements.
Adding additional features is fine as long as they don't conflict with any of them.
You should never mix another platform feature like `vmware`, or the `_dev` feature with the `lima` feature as they are known to be incompatible.

Build the disk image for both `amd64` and `arm64` architecture using this command:

```
$ ./build kvm_curl-nodejs-lima-arm64 kvm_curl-nodejs-lima-amd64
```

This will create a files named similar to this: `kvm-nodejs_curl-lima-amd64-today-baefbd7.qcow2` and `kvm-nodejs_curl-lima-arm64-today-baefbd7.qcow2`.

Next, generate the `yaml` file for lima using the `generate-manifest.py` script like this:

```
$ ./features/lima/generate-manifest.py --cname_base=kvm-nodejs_curl-lima --gardenlinux_version=today --commit_id=baefbd7
```

> [!IMPORTANT]
> Be sure to adapt the arguments to suit the disk images you've built before.

Note that this script does not need any external python dependencies, but it requires python to be at least version 3.12.
If you get an error like `AttributeError: module 'hashlib' has no attribute 'file_digest'` this hints at a too old python version.

This will generate a yaml file `kvm-nodejs_curl-lima-today.yaml` that can be used with Lima.

> [!IMPORTANT]
> Be sure to adapt the disk image location in the yaml file to suit your actual location.

Now you can run `limactl create`, `limactl start` and `limactl shell` like this:

```
$ limactl create --name=gardenlinux-today ./path/to/kvm-nodejs_curl-lima-today.yaml
$ limactl start gardenlinux-today
$ limactl shell gardenlinux-today
```
