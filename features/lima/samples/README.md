# Garden Linux lima sample manifests

This directory contains sample manifests for lima with Garden Linux as the operating system.

[`gardenlinux-rootless-podman.yaml`](./gardenlinux-rootless-podman.yaml)
installs and configures podman so it can be used by a non-root user to run containers.

[`gardenlinux-containerd.yaml`](./gardenlinux-containerd.yaml)
installs the Garden Linux build of containerd which we maintain.

[`gardenlinux-tpm.yaml`](./gardenlinux-tpm.yaml)
exposes an emulated TPM 2.0 device to the guest via swtpm (requires `swtpm` on the host and `vmType: qemu`).
Installs `tpm2-tools` in the guest so the TPM can be used for key storage, attestation, or workload identity.
