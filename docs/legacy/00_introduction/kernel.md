# Linux Kernel

Garden Linux aims towards a complete open, reproducible and easy-to-understand solution. That also includes all activities around the Kernel.
[Kernel.org](https://kernel.org) is the source of the official Linux kernels and therefore all kernels in Garden Linux are mainly based on this. Not to forget our Debian roots: we integrate with the build environment [Debian kernels](https://wiki.debian.org/Kernel) to support the Debian featureset to be compatible. Garden Linux tries to keep the amount of patches in the kernel diverging from Debian and kernel.org low, so everybody can easily support the Garden Linux kernel and no deep knowledge of Garden Linux internals is needed.
In contrast to Debian, Garden Linux integrates always with the latest Long Term Support kernel (LTS) and maintains this kernel at least for one overlapping period till the next kernel will be available. You can find the release categories and the time schedule for LTS releases also on [kernel.org](https://www.kernel.org/category/releases.html).
Garden Linux aims to integrate the latest long term release.

## Why does Garden Linux not integrate the mainline stable?
Mainline stable introduces features to the new Linux kernel, which happens every ~2 months. Some of those features affect the way e.g. container or network environment interact with the kernel and need some time to be adopted in surrounding tooling. Also some other feature introduce bugs, recognized after release and need to be reverted or other changes. In short: to avoid this we wait until a kernel version becomes a longterm stable and try to integrate always the latest long term stable and the one before to have a decent deprecation phase.   
**Garden Linux takes advantage of these patches.**

## A new long term kernel is released, when will it be integrated?
We are probably on it, but feel free to open a Github issue.

## Why does Garden Linux use Debian kernel patches and configuration?
Garden Linux :heart: Debian.

Debian is free and open source software. There are good [reasons](https://www.debian.org/intro/why_debian)
to use Debian. In the following we explain our reasons in the kernel context.

First, Debian provides an enterprise grade server operating system,
while protecting the claim to stay 100% free and open source.
Debian is rigorous when it comes to non-free software licenses,
also when it comes to the Linux Kernel. A prominent example of
what this means, is the extraction of non-free firmware from
the Linux Kernel.

Debian scans licenses and patches out everything
that violates the claim to stay 100% free. Since Garden Linux shares this
approach, we benefit from Debian patches.

Additionally, Debian provides a good kernel configuration,
which is used by Garden Linux as a base for configuration.
We extend this kernel configuration to our specific requirements during the
kernel integration process.

Furthermore, Debian kernel [patches](https://salsa.debian.org/kernel-team/linux/-/tree/master/debian/patches) are applied in most cases.

