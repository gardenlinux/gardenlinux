# Cross Architecture Build

Cross architecture builds require *binfmt_misc* support to be enabled in the kernel of your build system (usually the case for most modern distros).
You will also need to setup a qemu-user-static binfmt handler for the cross build target architecture using the [fix binary](https://www.kernel.org/doc/html/latest/admin-guide/binfmt-misc.html#:~:text=F%20%2D%20fix%20binary) flag.

On debian, this can be setup by simply installing the `qemu-user-static` and `binfmt-support` packages.
This will install binfmt handlers for most cpu architectures.


## Cross Architecture Package Build

To build packages for a foreign architecture run `make` inside the `packages` directory with `ARCH=TARGET_ARCH`, where `TARGET_ARCH` may be `arm64` or `amd64`.

For example, to build all arm64 packages on an x86 build machine, run

```shell
make -j $(nproc) ARCH=arm64 all
```

Cross architecture package builds only build architecture dependent binary packages.
So to also build architecture independent packages (i.e. packages with a `_all.deb` suffix) you need to run a native build as well.

**Note:** `linux-5.10-signed` requires both architecture dependent and independent packages from the `linux-5.10` build.
Therefore, to cross build `linux-5.10-signed` you first need to build `linux-5.10` both native and for the foreign build architecture.

```shell
make linux-5.10 && make ARCH=arm64 linux-5.10 && make ARCH=arm64 linux-5.10-signed
```

**TODO:** figure out a way to make this dependency on native linux-5.10 build automatic in the Makefile


## Cross Architecture Image Build

To build Garden Linux images for a foreign architecture run `make` with `ARCH=TARGET_ARCH`, where `TARGET_ARCH` may be `arm64` or `amd64`.

To use locally build packages also supply the `USE_LOCAL_PKGS=1` option.

For example, to build all Garden Linux flavours for an arm64 target on a x86 build machine, run

```shel
make -j $(nproc) ARCH=arm64 USE_LOCAL_PKGS=1 all
```
