# KDUMP

Feature that allows the creation of a crashdump whenever the dump of a system's
kernel memory needs to be taken; for example when the system panics.

Kdump uses kexec to boot a crash kernel that then has access to the old kernel's memory.

## Feature includes:
- kdump-tools
- kexec-tools
- makedumpfile

Debian defaults are ok for most usecases.
No custom kernel or initrd are used; the current kernel and initrd
are reused as crash kernel / crash initrd.

When using Garden Linux images that support in-place updates, the _usi_ feature is enabled, using this kdump feature as-is is 
not going to work correctly because of the amount of memory reserved for the dump kernel via the _crashkernel_ kernel
parameter.

When using a in-place updates enabled image, because the rootfs of the system is actually a EroFS file packaged into the 
initrd, the size of the initrd will vary greatly depending on the set of features used to build the image so it's hard to
make a recommendation on the amount of memory that should be used for the _crashkernel_.
Also, the initrd gets extracted from the UKI and made available to kdump-tools in /var/lib/kdump.

Enabling kdump on a already installed (already running) system is not supported; or experimentally, the following steps 
should be taken:
- install kdump-tools and makedumpfile
- copy the initrd to /var/lib/kdump using the name _initrd.img-$(uname -r)_
- modify the kernel cmdline by modifying _/etc/kernel/cmdline_ either directly of via _/etc/kernel/cmdline.d_ to include _crashkernel=XXXM_ option
- regenerate the boot loader entries
- reboot

#### References:
https://docs.kernel.org/admin-guide/kdump/kdump.html
https://docs.kernel.org/filesystems/erofs.html
