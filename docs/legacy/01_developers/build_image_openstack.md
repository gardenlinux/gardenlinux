# Garden Linux OpenStack Images

Garden Linux can be run on OpenStack, but due to the diverse nature of OpenStack deployments, some customization may be required for your specific environment. This guide covers our reference implementations and provides guidance for adapting Garden Linux to your OpenStack setup.

## Reference Implementations

We have tested Garden Linux on two OpenStack platforms:

### SAP Converged Cloud (CC)

- OpenStack environment using VMware ESXi as hypervisor
- Requires specific customizations:
  - `open-vm-tools` for VMware integration
  - Custom disk adapter configuration
  - VMware-specific image properties

### OSISM Reference Implementation

- OpenStack environment using KVM as hypervisor
- [OSISM](https://osism.tech/) is a deployment tool that creates standardized OpenStack environments
- Fully compatible with [Sovereign Cloud Stack (SCS)](https://sovereigncloudstack.org) specifications
- Supports standard OpenStack configurations and features

## Building and Deploying Images

### For SAP Converged Cloud

1. Build the base image:

```bash
make openstack-gardener_prod-amd64-build
```

2. Convert the image for VMware compatibility:

```bash
qemu-img convert -O vmdk -o adapter_type=buslogic input.raw output.vmdk
```

3. Upload to OpenStack with VMware-specific properties:

```bash
openstack image create \
     --container-format bare \
     --disk-format vmdk \
     --property vmware_disktype="sparse" \
     --property vmware_adaptertype="ide" \
     --property hw_vif_model="VirtualVmxnet3" \
     --property vmware_ostype=otherLinux64Guest \
     gardenlinux < openstack-gardener_prod_amd64-today-local.vmdk
```

### For OSISM / SCS compliant OpenStack

1. Build the image (choose one):

```bash
# Standard image
make openstack-gardener_prod-amd64-build

# Image with TPM 2.0 and Trusted Boot support
make openstack-gardener_prod_tpm2_trustedboot-amd64-build
```

2. Upload to OpenStack with standard properties:

```bash
openstack image create \
     --container-format bare \
     --disk-format raw \
     --min-disk 3 \
     --min-ram 2048 \
     --property architecture=x86_64 \
     --property cpu_arch=x86_64 \
     --property hypervisor_type=qemu \
     --property image_description="Garden Linux Platform Test" \
     --property distro=gardenlinux \
     --property os_distro=gardenlinux \
     --property os_admin_user=gardenlinux \
     --hw_firmware_type=uefi \
     gardenlinux < openstack-gardener_prod_amd64-today-local.raw
```

For TPM 2.0 and Secure Boot support, add these properties:

```bash
     --property os_secure_boot=optional \
     --hw_tpm_version=2.0 \
     --hw_tpm_model=tpm-tsi
```

## Secureboot Support on OpenStack

Garden Linux supports Secure Boot on OpenStack platforms through our [Unified System Image (USI)](https://github.com/gardenlinux/gardenlinux/blob/main/docs/boot_modes.md#unified-system-image-usi) approach. We have verified this functionality with OpenStack 2024.1 on an [OSISM Testbed](https://osism.tech/docs/testbed).

### Prerequisites

To use Garden Linux with Secure Boot on OpenStack, your environment must meet several requirements:

1. **TPM 2.0 Support**

   - OpenStack must have the [Barbican](https://docs.openstack.org/barbican/2024.1/) key manager service deployed
   - Instance must have access to a vTPM 2.0 device
     - Nova needs to have `libvirt.swtpm_enabled=true` set.
   - Required image/flavor properties:
     ```bash
     hw_tpm_version=2.0
     hw_tpm_model=tpm-tsi
     ```
   - [Documentation](https://docs.openstack.org/nova/2024.1/admin/emulated-tpm.html)
   - [Nova Configuration Options - libvirt.swtpm_enabled](https://docs.openstack.org/nova/2024.1/configuration/config.html#libvirt.swtpm_enabled)

2. **UEFI Boot**

   - Instance must boot in UEFI mode
   - Required image/flavor property:
     ```bash
     hw_firmware_type=uefi
     ```
   - [Documentation](https://docs.openstack.org/nova/2024.1/admin/uefi.html)

3. **Secure Boot Mode**
   - Required image/flavor property:
     ```bash
     os_secure_boot=optional
     ```
   - [Documentation](https://docs.openstack.org/nova/2024.1/admin/secure-boot.html)

### How It Works

Garden Linux uses systemd's native [secure-boot-enroll](https://www.freedesktop.org/software/systemd/man/253/loader.conf.html#secure-boot-enroll) mechanism for certificate enrollment. Details are available in the [Garden Linux documentation](https://github.com/gardenlinux/gardenlinux/blob/main/docs/boot_modes.md).

1. First Boot:

   - System boots in `optional` Secure Boot mode (UEFI Setup Mode)
   - Certificates are enrolled from `EFI\loader\keys\auto` (only if running inside VM to not brick hardware, see `secure-boot-enroll = if-safe` from [secure-boot-enroll](https://www.freedesktop.org/software/systemd/man/253/loader.conf.html#secure-boot-enroll))
   - System prepares for Secure Boot

2. Subsequent Boots:
   - Certificates are loaded from instance NVRAM
   - System boots with Secure Boot enabled

### Current Limitations

While Secure Boot works in `optional` mode, there are some limitations:

1. **Required Mode Not Supported**

   - Booting with `os_secure_boot=required` currently fails with:
     ```
     Instance failed to spawn: nova.exception.SecureBootNotSupported: Secure Boot is not supported by host
     ```
   - Further investigation would be needed to get this working.

2. **Certificate Management**
   - OpenStack 2024.1 lacks API support for secureboot certificate management (other cloud providers support this)
   - Certificates must be included in the image
   - Future versions may support certificate injection via `os_nvram_template`

### Future Improvements

These topics could be improved and investigated further:

1. **Certificate Injection**

   - Working with OpenStack community to enable certificate injection via API.
   - Using custom `OVMF_VARS.fd` templates on hypervisors
   - Possible use of undocumented [`os_nvram_template` property](https://github.com/openstack/nova/blob/98226b60f3fe7b20e8d7f208c12f8d0086cd83d0/nova/virt/libvirt/config.py#L3081)
   - [OpenStack Spec](https://specs.openstack.org/openstack/nova-specs/specs/wallaby/implemented/allow-secure-boot-for-qemu-kvm-guests.html)

2. **Required Mode Support**
   - Working with OpenStack community to enable `required` mode
   - Investigating host requirements and configurations

## Testing

Currently, our OpenStack image testing consists of:

- Basic functionality testing in [chroot environments](https://github.com/gardenlinux/gardenlinux/tree/main/tests#chroot)
- OpenTofu-based [platform tests](https://github.com/gardenlinux/gardenlinux/tree/main/tests/platformSetup/tofu/modules/openstack)
  - available but not enabled in CI
