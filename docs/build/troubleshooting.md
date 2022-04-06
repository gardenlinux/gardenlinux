# Troubleshooting

In this document you find solutions for common and uncommon issues related to your build environment.
If you are facing issues with Garden Linux please open a [Github Issue](https://github.com/gardenlinux/gardenlinux/issues/new/choose).

## Build Issues
<!--  Issue Template

## <Very brief description>
## Description
... 
## <either "Solution" or "Workaround">
...
-->

### Failed to connection to Audit System during build
#### Description
Happened on Manjaro Linux with AppArmor
```
Error connecting to audit system.
```
<details>
  <summary>Extended log of failed Build</summary>
  
```
## executing exec.post
### server:
### metal:
690M    rootfs
174M    output/metal_dev-amd64-dev-local/rootfs.tar.xz
4c580d62ad38ead941ceb7584dcd89c4ee4d17be44fba15773a1b8954b013125
#### building diskimage
  found new fstab in base
  building rawfile
Error connecting to audit system.
Checking that no-one is using this disk right now ... OK

Disk output/metal_dev-amd64-dev-local/rootfs.raw: 2 MiB, 2097152 bytes, 4096 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes

>>> Script header accepted.
>>> Script header accepted.
>>> line 3: unsupported command

New situation:
Leaving.

make: *** [Makefile:148: metal-dev] Error 1
```
</details>  

#### Solution
If you are running a System with AppArmor (e.g. Manjaro Linux),
have a look at `/proc/cmdline` by running `cat /proc/cmdline`:

Make sure, the output contains the following part: `apparmor=1 security=apparmor`

Also make sure `aa-status` returns `yes`.

The Issue was a missing kernel parameter - the systemd service was not able to reach status `Active: active (exited)`.

If you are actually missing `apparmor=1 security=apparmor`, open `/etc/default/grub` and add it to `GRUB_CMDLINE_LINUX_DEFAULT`.

result:

	 GRUB_CMDLINE_LINUX_DEFAULT="quiet apparmor=1 security=apparmor udev.log_priority=3"

save and close the file, and run

	sudo update-grub

and reboot your device. now recheck `/proc/cmdline` and `aa-status`

