---
title: Linux Kernel
weight: 10
disableToc: false
---

# Linux Kernel


Kernel.org releases Linux kernels in different [categories](https://www.kernel.org/category/releases.html).
Garden Linux aims to integrate the latest long term release.


## How to build a Linux Kernel for Garden Linux

Compiling, packaging and signing a Linux kernel package for garden Linux can be
done with the help of scripts located in ```packages/manual```.

```bash
cd packages

# creates a docker container build environment
make manual

# build a Linux kernel .deb package
./manual/Linux-5.10

# sign the Linux .deb package
./manual/Linux-5.10-signed

```

## Why does Garden Linux not integrate the mainline?
Mainline introduces new features to the Linux kernel, which happens every 2-3 months.
Until a kernel version becomes a longterm release,
it receives patches frequently.
**Garden Linux takes advantage of these patches.**

## A new long term kernel is released, when will it be integrated?

We are on it! Integrating a new kernel requires effort. We
apply Garden Linux specific patches, and carefully select the features we need.

## Why does Garden Linux use Debian kernel patches and configuration?
Garden Linux :heart: Debian.

Debian is free and open source software. There are good [reasons](https://www.debian.org/intro/why_debian)
to use Debian. In the following we explain our reasons in the kernel context.

First, debian provides an enterprise grade server operating system,
while protecting the claim to stay 100% free and open source.
Debian is rigorous when it comes to non-free software licenses,
also when it comes to the Linux Kernel. A prominent example of
what this means, is the extraction of non-free firmware from
the Linux Kernel.

Debian scans licenses and patches out everything
that violates the claim to stay 100% free. Since Garden Linux shares this
approach, we benefit from Debian patches.

Additionally, debian provides a good kernel configuration,
which is used by Garden Linux as a base for configuration.
We extend this kernel configuration to our specific requirements during the
kernel integration process.

## I need a Driver for my Garden Linux!

If your driver is free, and part of the kernel but not yet included in your
Garden Linux Image you may want to change the kernel configuration to include it.






