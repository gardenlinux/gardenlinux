# Tutorial: How to  build a package

In this tutorial we're going to show how to build a package for the Garden Linux with the build
system. In the end, you should be able to build any package that is located within the Garden Linux
organization repositories.


We begin with the basics, cloning the tool to build packages. And then we build a single package as
an example. 

It does not show you how to compose a package and/or how the actual package system is intended in
its design.

## package-build

For this we need ``git``, a modern version of ``bash`` and ``podman``. Docker is not supported.


```bash
git clone https://github.com/gardenlinux/package-build.git
cd package-build
```


Test that the you can execute it:

```bash
./build
```

You should get now an error message saying: ``unbound variable``, this is expected.

    ++ realpath ./build
    ++ dirname /private/tmp/package-build/build
    + src_dir=/private/tmp/package-build
    + container=
    + arch=amd64
    + skip_source=
    + skip_binary=
    + build=binary
    + build_dep_dir=
    + leave_artifacts=
    + edit=
    + '[' 0 -gt 0 ']'
    ./build: line 56: $1: unbound variable
    + dir=

Now we need to place a target package we want to build.

## Building a package

We recommend using a separate folder next to the package-build directory because checking out a
separate repository within the package-build folder will confuse the git control structure. It’s
possible to download the zip file only, which this tutorial does not cover.

To make the target package available within the package-build folder, we're going to use a softlink.

```bash
cd ..
git clone https://github.com/gardenlinux/package-linux.git
cd package-build
ln -s ../package-linux/ ./package-linux
```

Now the package builder can be invoked with the parameter slash package-linux, and it will start a
container, fetch the sources, apply our changes, and build the package, and in the end you will have
a package within the ``.build`` folder of the ``package-linux``.


```bash
./build package-linux
```

Once the build is completed, you can find the Debian packages within the ``.build`` folder within
the ``package-linux`` folder.


    ls -l package-linux/.build/
    total 3737944
    -rw-r--r--  1 user  staff     1156700 Jan 20 11:18 bpftool_7.7.0+6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff      996840 Jan 20 11:18 bpftool-dbgsym_7.7.0+6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff      934396 Jan 20 11:18 hyperv-daemons_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff       48720 Jan 20 11:18 hyperv-daemons-dbgsym_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff      919176 Jan 20 11:18 libcpupower-dev_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff      926808 Jan 20 11:18 libcpupower1_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff       33024 Jan 20 11:18 libcpupower1-dbgsym_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff       21153 Jan 20 11:18 linux_6.18.5-1gl1_arm64.buildinfo
    -rw-r--r--  1 user  staff       16521 Jan 20 11:18 linux_6.18.5-1gl1_arm64.changes
    -rw-r--r--  1 user  staff     1378868 Jan 20 10:21 linux_6.18.5-1gl1.debian.tar.xz
    -rw-r--r--  1 user  staff       36296 Jan 20 10:21 linux_6.18.5-1gl1.dsc
    -rw-r--r--  1 user  staff   157376312 Jan 20 11:18 linux_6.18.5.orig.tar.xz
    -rw-r--r--  1 user  staff     1581800 Jul  9  2025 linux_6.6.56-0gl0~bp1592.debian.tar.xz
    -rw-r--r--  1 user  staff       14652 Jul  9  2025 linux_6.6.56-0gl0~bp1592.dsc
    -rw-r--r--  1 user  staff   142933768 Jul  9  2025 linux_6.6.56.orig.tar.xz
    -rw-r--r--  1 user  staff      922052 Jan 20 11:18 linux-base-6.18.5-arm64_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff      922048 Jan 20 11:18 linux-base-6.18.5-cloud-arm64_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff         932 Jan 20 11:18 linux-base-arm64_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff         936 Jan 20 11:18 linux-base-cloud-arm64_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff     1506584 Jan 20 11:18 linux-bpf-dev_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff     1012480 Jan 20 11:18 linux-config-6.18_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff      956840 Jan 20 11:18 linux-cpupower_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff       66616 Jan 20 11:18 linux-cpupower-dbgsym_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff     1983144 Jan 20 11:18 linux-headers-6.18.5-arm64_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff     1516940 Jan 20 11:18 linux-headers-6.18.5-cloud-arm64_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff     9411732 Jan 20 11:18 linux-headers-6.18.5-common_6.18.5-1gl1_all.deb
    -rw-r--r--  1 user  staff        1156 Jan 20 11:18 linux-headers-arm64_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff        1156 Jan 20 11:18 linux-headers-cloud-arm64_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff    62491760 Jan 20 11:18 linux-image-6.18.5-arm64_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff  1002951104 Jan 20 11:18 linux-image-6.18.5-arm64-dbg_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff    21268168 Jan 20 11:18 linux-image-6.18.5-cloud-arm64_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff   318094280 Jan 20 11:18 linux-image-6.18.5-cloud-arm64-dbg_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff        1428 Jan 20 11:18 linux-image-arm64_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff        1164 Jan 20 11:18 linux-image-arm64-dbg_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff        1440 Jan 20 11:18 linux-image-cloud-arm64_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff        1172 Jan 20 11:18 linux-image-cloud-arm64-dbg_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff     1347176 Jan 20 11:18 linux-kbuild-6.18.5_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff     1979080 Jan 20 11:18 linux-kbuild-6.18.5-dbgsym_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff     2391664 Jan 20 11:18 linux-libc-dev_6.18.5-1gl1_all.deb
    -rw-r--r--  1 user  staff       12260 Jan 20 11:18 linux-libc-dev-amd64-cross_6.18.5-1gl1_all.deb
    -rw-r--r--  1 user  staff       11804 Jan 20 11:18 linux-libc-dev-arm64-cross_6.18.5-1gl1_all.deb
    -rw-r--r--  1 user  staff      947604 Jan 20 11:18 linux-misc-tools_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff      103004 Jan 20 11:18 linux-misc-tools-dbgsym_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff        1100 Jan 20 11:18 linux-source_6.18.5-1gl1_all.deb
    -rw-r--r--  1 user  staff   158282460 Jan 20 11:18 linux-source-6.18_6.18.5-1gl1_all.deb
    -rw-r--r--  1 user  staff      948268 Jan 20 11:18 rtla_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff      109968 Jan 20 11:18 rtla-dbgsym_6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff      950332 Jan 20 11:18 usbip_2.0+6.18.5-1gl1_arm64.deb
    -rw-r--r--  1 user  staff      151496 Jan 20 11:18 usbip-dbgsym_2.0+6.18.5-1gl1_arm64.deb

