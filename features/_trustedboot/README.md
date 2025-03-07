# Trustedboot

See [GardenLinux Boot Modes](../../docs/boot_modes.md) for high level docs.

## How to Build & Test on macOS

1. make sure you have build the secureboot certificate chain (`./cert/build`)
2. build an image with the `_trustedboot` flag enabled and optionally the `_tpm2` flag, e.g. `./build kvm_dev_trustedboot_tpm2`
3. get a version of edk2 with secureboot support:
   ```
   mkdir edk2
   podman run --rm -v "$PWD/edk2:/mnt" debian:testing bash -c 'apt update && apt install -y qemu-efi-aarch64 && cp /usr/share/AAVMF/AAVMF_CODE.secboot.fd /usr/share/AAVMF/AAVMF_VARS.fd /mnt/'
   ```
4. boot with `start-vm` (be sure to add the `,qcow=4G` part which is vital to make the disk large enough for the repartition):
   ```
   ./bin/start-vm --ueficode edk2/AAVMF_CODE.secboot.fd --uefivars edk2/AAVMF_VARS.fd --tpm2 disk.qcow2,qcow=4G
   ```



[^1]: https://0pointer.net/blog/fitting-everything-together.html
[^2]: https://uapi-group.org/specifications/specs/unified_kernel_image/
