---
title: Non-Default Install
weight: 10
disableToc: false
---


*e.g. on a bare metal system or a simple virtual machine*

## Idea
Garden Linux is usually used either with a cloud provider (aws, azure, gcp, alicloud ...) as an image in their image repositories.

Also Garden Linux has a pretty simple way to be used with any kind of PXE or HTTP boot (user feature _pxe).

But there maybe reasons to install Garden Linux on a hard disk without any of this ...

## Prerequisites

You need to have the possiblity to boot a kind of live system.
e.g. there are systems like systemrescuecd
https://www.system-rescue.org/

look there how it is booted, e.g:
- via usbstick https://www.system-rescue.org/Installing-SystemRescue-on-a-USB-memory-stick/
- or via iso disk image https://www.system-rescue.org/Download/ (use the iso specified there)

Any other live system (knoppix or see https://en.wikipedia.org/wiki/Live_CD) would also be sufficient. We need network support (to download the Garden Linux disk image) and we need the command `dd` to push to disk.

## Installation

On your build system do:

```
git clone https://github.com/gardenlinux/gardenlinux.git
cd gardenlinux
make metal-dev
```

> **WARNING**
 This is a dev build! It has autologin enabled! (It is easy to disable this afterwards, but without you will not be able to log into the box since you cannot provision any credentials, without cloud provider / ignition support)

You will find the final file e.g. 
`.build/metal/20210616/amd64/bullseye/rootfs.raw`
(20210616 is the date when built REPLACE this with current date, amd64 the platform, metal the feature)

Boot the target system into your live system ... (as described in #Prerequisites)

```
system#
```

Download the image above, e.g.
```
system# cd /tmp
system# wget http://<your ip/s3>/rootfs.raw 
```

Select the disk
```
system# lsblk -dp
NAME       MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
/dev/loop0   7:0    0   112G  0 loop
/dev/sda     8:0    0 558.4G  0 disk
/dev/sr0    11:0    1  1024M  0 rom
```
This example has only one disk. (you may have more; make sure to select the disk to boot from or boot later explicitly)
Any existing partitions on disk are ignored (parameter -d) but the full path is printed (-p) since needed.

So e.g. you may select /dev/sda (/dev/nvme0n1, /dev/hda, /dev/... depends on your box!!)

```
dd if=/tmp/rootfs.raw of=/dev/sda
```
> **WARNING**
This is a DESTRUCTIVE command for anything that is on disk `/dev/sda`. The disk will contain only Garden Linux afterwards! BE CAREFUL!

You do not need to care about partitioning etc. Garden Linux has an integrated partition auto grow. So after the first boot the disk will be properly aligned.
You also will not need to make the disk bootable, because Garden Linux comes with a default legacy boot (non-UEFI) if installed on the full disk (as we do here) AND it will also come with an UEFI partition that can be adressed via the EFI shell (not part of this document)

```
system# reboot
```

Done!

> **PS:** after boot usr is readonly (a security feature of Garden Linux)
> Remount with
> 
> `sudo mount -o remount,rw /usr`
>
>after the new system is booted. Any command like `apt` will now work as expected
 
> **PPS:** After boot you will be auto logged in. This is a security problem! Define the password for root:
> `sudo passwd`
> `New password:`
> `Retype new password:`
> and then delete the files:
> `sudo rm -rf /etc/systemd/system/getty@tty1.service.d /etc/systemd/system/serial-getty@.service.d`
> now your system is properly secured.
> 
> to add another user 
  `sudo adduser test`
  to grant sudo privileges
  `sudo adduser test wheel`
