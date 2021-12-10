
## versions
To have reproducible builds we fix the version numbers for 
* KERNEL_RT_VERSION: Version of [Realtime Kernel Patches](https://mirrors.kernel.org/pub/linux/kernel/projects/rt/)
* KERNEL_VERSION: Version of [kernel.org's linux kernel](https://www.kernel.org)
* KERNEL_DEBIAN: Version of [Debian's older Kernel](https://salsa.debian.org/kernel-team/linux/)
* BUILDENV: Version of [Debian's Buildenvironment](https://salsa.debian.org/kernel-team/linux/)

In the case of `KERNEL_VERSION > KERNEL_DEBIAN`, we may need to patch the Buildenv. 

### Selecting a Version
Before each kernel build a softlink to the latest VERSION file is created. Example:
```bash
	rm -f $(MANUALDIR)/VERSION
	ln -s $(MANUALDIR)/linux.d/versions/VERSION-5.4 $(MANUALDIR)/VERSION
```
The linux and linux-signed scripts will use the version file that is available at `$(MANUALDIR)/VERSION`

## config

`bootstrap_kernel_build` function of `.kernel-helper` will overwrite debians `debian/config` if for the given version
a `config/$KERNEL_VERSION/config` exists. If it does not exist, we use debians config.


## patches
For each supported `$KERNEL_VERSION` we have a  subfolder of patches. 
These patches are applied by `apply_quilt_series` function before the main quilt series of debian is applied via 
`make -f debian/rules orig`.

### debian & environment patches
`debian` and `environment` patches are applied before debian patches are applied.

### kernel patches
`kernel` patches are applied by the main debian quilt process. Also patches that gardenlinux adds!
This is achieved by patching the `debian/patches/series.patch` to include additional patches.

### keep.list
By default all content of `debian/patches` comes from the KERNEL_DEBIAN version.
If the buildenvironment comes with newer patches you want to keep,
then you can specify them in the `patches/$KERNEL_VERSION/keep.list`. 
This file contains relative paths to files, starting from the `debian/patches` folder.
For example:

```
debian/export-symbols-needed-by-android-drivers.patch
```