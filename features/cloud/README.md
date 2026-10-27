## Feature: cloud
### Description
<website-feature>
This feature adjusts Garden Linux for cloud functionality with cloud kernel, boot optimizations, etc.
</website-feature>

### Features
All hyperscaler & cloud platforms (e.g. `ali`, `azure`, `vmware`, `openstack`, etc.) are based on this `cloud` feature. Garden Linux artifacts with cloud functionality are highly optimized for cloud/hyperscaler environments by running on ARM64 or AMD64 hardware platforms including optimized kernel and boot options.

### Unit testing
this feature supports unit tests and ensures that all required packages are present, an autologout is configured, PAM faillock is active and the wireguard kernel module is activated.

### Meta
|||
|---|---|
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | Applies cloud-specific configuration: network defaults, module denylists, and service settings. |
| [`file.include.markers.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include.markers.yaml) ([ref](/reference/testing/test-coverage-markers)) | Maps files to test-coverage marker IDs. |
| [`info.yaml`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/info.yaml) ([ref](/reference/features/#info-yaml-file-structure)) | Declares `type: element` and included/excluded features. |
| [`pkg.include`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/pkg.include) ([ref](/reference/features/#pkg-include)) | Installs: `fdisk`, `linux-image-cloud-$arch`. |
| [`file.include/etc/kernel/entry-token`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/kernel/entry-token) ([`file.include`](/reference/features/#file-include)) | Sets the boot entry token used by systemd-boot. |
| [`file.include/etc/kernel/cmdline.d/00-default.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/kernel/cmdline.d/00-default.cfg) ([`file.include`](/reference/features/#file-include)) | Default kernel command line parameters for cloud images. |
| [`file.include/etc/kernel/cmdline.d/40-enable-swap-cgroup-accounting.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/kernel/cmdline.d/40-enable-swap-cgroup-accounting.cfg) ([`file.include`](/reference/features/#file-include)) | Enables swap cgroup accounting for memory management. |
| [`file.include/etc/kernel/cmdline.d/60-timeout.cfg`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/kernel/cmdline.d/60-timeout.cfg) ([`file.include`](/reference/features/#file-include)) | Sets the systemd boot timeout. |
| [`file.include/etc/kernel/postinst.d/00-kernel-cmdline`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/kernel/postinst.d/00-kernel-cmdline) ([`file.include`](/reference/features/#file-include)) | Regenerates the kernel command line after kernel updates. |
| [`file.include/etc/kernel/postinst.d/zz-update-syslinux`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/kernel/postinst.d/zz-update-syslinux) ([`file.include`](/reference/features/#file-include)) | Updates the syslinux bootloader after kernel installs. |
| [`file.include/etc/kernel/postrm.d/zz-update-syslinux`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/kernel/postrm.d/zz-update-syslinux) ([`file.include`](/reference/features/#file-include)) | Updates the syslinux bootloader after kernel removal. |
| [`file.include/etc/modprobe.d/disabled_firewire.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/modprobe.d/disabled_firewire.conf) ([`file.include`](/reference/features/#file-include)) | Denylists firewire kernel modules (not needed in cloud environments). |
| [`file.include/etc/modprobe.d/disabled_fs.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/modprobe.d/disabled_fs.conf) ([`file.include`](/reference/features/#file-include)) | Denylists unused filesystem modules to reduce attack surface. |
| [`file.include/etc/modprobe.d/disabled_net.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/modprobe.d/disabled_net.conf) ([`file.include`](/reference/features/#file-include)) | Denylists unused network protocol modules to reduce attack surface. |
| [`file.include/etc/modprobe.d/disabled_udf.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/modprobe.d/disabled_udf.conf) ([`file.include`](/reference/features/#file-include)) | Denylists the UDF filesystem module. |
| [`file.include/etc/modprobe.d/disabled_usb.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/modprobe.d/disabled_usb.conf) ([`file.include`](/reference/features/#file-include)) | Denylists USB storage modules (not needed in cloud environments). |
| [`file.include/etc/profile.d/50-autologout.sh`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/profile.d/50-autologout.sh) ([`file.include`](/reference/features/#file-include)) | Configures automatic session logout after inactivity. |
| [`file.include/etc/repart.d/root.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/repart.d/root.conf) ([`file.include`](/reference/features/#file-include)) | systemd-repart partition definition for the root partition (enables auto-growth). |
| [`file.include/etc/sysctl.d/20-cloud.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/sysctl.d/20-cloud.conf) ([`file.include`](/reference/features/#file-include)) | Cloud-optimized sysctl settings. |
| [`file.include/etc/sysctl.d/21-ipv4-settings.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/sysctl.d/21-ipv4-settings.conf) ([`file.include`](/reference/features/#file-include)) | IPv4 network sysctl tuning for cloud environments. |
| [`file.include/etc/sysctl.d/22-ipv6-settings.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/sysctl.d/22-ipv6-settings.conf) ([`file.include`](/reference/features/#file-include)) | IPv6 network sysctl tuning for cloud environments. |
-| [`file.include/etc/systemd/network/99-default.network`](https://github.com/gardenlinux/gardenlinux/blob/main/features/server/file.include/etc/systemd/network/99-default.network) ([`file.include`](/reference/features/#file-include)) | Default systemd-networkd DHCP configuration for all Ethernet interfaces. |
| [`file.include/etc/systemd/system/rngd.service.d/architecture.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/cloud/file.include/etc/systemd/system/rngd.service.d/architecture.conf) ([`file.include`](/reference/features/#file-include)) | Architecture-specific override for the `rngd` entropy service. |

### Related features

**Includes:**

- [`server`](/reference/features/server) — provides the server base layer (auditd, SELinux, networking, SSH).
- [`_legacy`](/reference/features/_legacy) — adds BIOS/legacy boot support for cloud images that may boot on older hypervisors.
- [`_fwcfg`](/reference/features/_fwcfg) — provides `fw_cfg`-based metadata retrieval used by some hypervisors.

**Excludes (incompatible with):**

- [`openstackMetal`](/reference/features/openstackMetal) — `cloud` and `openstackMetal` are mutually exclusive due to incompatible kernel and network configurations.

## Related topics

<RelatedTopics />

