# Gardener Kernel restart

[Gardener](https://gardener.cloud), one of the major consumers of Garden Linux, must be able to configure certain settings of the operating system before the [kubelet](https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/) comes up. Some of these settings might require a reboot/restart of the kernel.

This document describes the process how Gardener reconfigures kernel parameters that require a reboot/restart and how that restart is performed. It only applies to Garden Linux flavors with the `gardener` feature compiled in.

## Control files

Gardener will place control files to `/var/lib/gardener-gardenlinux/etc` to declare what should be set on the operating system.

**Example:** Gardener needs to be able to change the Linux Security Module (lsm) from _AppArmor_ to _SELinux_. To do so, it will place a the file `/var/lib/gardener-gardenlinux/lsm` and write either `AppArmor` or `SELinux` to it. Scripts in Garden Linux are then responsible for picking up these files and do whatever is needed to change the lsm of the system.

## The applier scripts

The scripts that pick up the control files in `/var/lib/gardener-gardenlinux/etc` themselves reside in `/var/lib/gardener-gardenlinux` and must follow the pattern `XX_script_name` where `XX` is a number. The scripts will be executed in order by the systemd unit `gardener-configure-settings.service`.
If the configuration of a system property requires a reboot, the script must create the empty file at `/var/run/gardener-gardenlinux/restart-required` (`/var/run` lives on a `tmpfs` so that this file gets discarded on a reboot).

## The restart script

If a configuration script requires a kernel restart/reboot, it needs to place the file `/var/run/gardener-gardenlinux/restart-required`. If found, the systemd unit `gardener-restart-kernel.service` will restart the kernel before the kubelet (if installed) comes up. It will not restart the system if it detects that the kubelet is already running.
_Note:_ Restarting the kernel currently means rebooting the system. Later iterations of the script should make use of `kexec` to avoid POST times on systems with lots of RAM.

## systemd units

| Unit name | Purpose |
|---|---|
| `gardener-configure-settings.service` | Invokes the scripts in `/var/lib/gardener-gardenlinux` in order. Must run _after_ Gardeners cloud-config downloader (`cloud-config-downloader.service`, gets deployed during Gardeners bootstrapping of a Kubernetes node), but _before_ `gardener-restart-kernel.service` |
| `gardener-restart-kernel.service` | Restarts the kernel if requested by one of the previous configuration script. Must run _after_ `gardener-configure-settings.service` but _before_ `kubelet.service`. |
