<this file currently exists for the upcoming gardenlinux.io website>

### Garden Linux provides:

- better organisation for a high count of machines
- unified Images
- additional Security
- a way to define Machines in your network in a declarative way (Infrastructure as Code)

--- 

The Approach of Garden Linux is building the Linux Image with all necessary upgrades and configuration prior the first boot. This way you can be sure, all machines running your build are really the same.

It is advised to boot Garden Linux via `PXE`-boot - that way each machine gets it's own folder with all configuration on the PXE-Server. This folder structure can be created from another source of truth, adapted by scripts... define your machines by code.

By placing your data on an extra partition, you can easily delete and recreate machines - even with additional Read-Only Permissions on sensible folders like `/usr`, which brings you more security.

You can even integrate the Garden Linux buildprocess into a pipeline, which always serves the latest Garden Linux Build for all of your machines.
