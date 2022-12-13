# Garden Linux Binary Set
## General
This directory contains many scripts to manage the Garden Linux build process. While most of them are used in a Docker container during the Garden Linux build (e.g. `garden-build`, `garden-feat`, `makepart`, ...) there are also several useful scripts (e.g. `start-vm`, `inject-sshkey`, ...) that may be used afterwards.

## Overview
By the given directory, we distinguish between scripts that are mandatory for the Garden Linux build process and scripts that are optional but very useful for handling a final Garden Linux artifact. Therefore, we describe them by the given two sections and only describe the standalone usable ones in detail.

### Mandatory for Garden Linux Build Process
| Name | Descriptions |
|--|--|
| garden-apt-get | Handles `apt-get` commands in `chroot` env |
| garden-build | Main script to build Garden Linux (creates a `chroot` env in a Docker container) |
| garden-chroot | Performs all necessary steps to integrate Garden Linux features |
| garden-config | Performs adjustments by activated `features` |
| garden-feat.go | Helper script to validate defined `features` (include, exclude, depends) |
| garden-fixup | Helper script to clean up uneeded files after build process |
| garden-fs | Creates the filesystem layout by `features` (creates: `fstab`) |
| garden-init | Debootstraps Garden Linux |
| garden-slimify | Creates a slimifyed version of Garden Linux |
| garden-tar | Creates a `.tar.xf` image of the build env from `chroot` env |
| garden-version | Creates a version schema |
| gen_make_targets | Generates `make` targets from the `flavour.yaml` |
| get-arch | Evaluates the base arch of the build host |
| makedisk | Creates the disks during the build process in the `chroot` env |
| makepart | Creates the partitions during the build process in the `chroot` env |
| shrink.sh | Shrinks the filesystem of a image |

### Standalone usable scripts
| Name | Descriptions |
|--|--|
| convert_raw_to_vhd | Script to convert a `.raw`  image file to a `.vhd` (VMWare) |
| inject-sshkey | Injects a SSH publickey (for a `specific user` or `root`) into a Garden Linux artifact |
| start-vm | Starts a QEMU/KVM based VM in text mode with activated SSH `hostfwd` by a given image file |
| make-ali-ami | Integrate/orchestrate `Aliyun` platform by a given image |
| make-azure-ami | Integrate/orchestrate `Azure` platform by a given image  |
| make-ec2-ami | Integrate/orchestrate `EC2` platform by a given image  |
| make-gcp-ami | Integrate/orchestrate `GCP` platform by a given image  |
| make-ova | Converts image to `.ova` file |
| make-vhd | Converts image to `.vhd` file |


## Detail
### General
This section covers the standalone tools in detail and provides a small overview of their options and how to use them.

### convert_raw_to_vhd
This script converts a given `.raw` image file into a `.vhd` image file.

**Usage:**

`convert_raw_to_vhd /path/to/$image_name.raw`

### inject-sshkey
This script allows to inject a SSH pubkey to a final Garden Linux image to ensure a SSH login is possible.

**Options:**
| Option (short) | Descriptions |
|--|--|
| image (-i) | Path to image |
| key (-k) | Path to SSH pubkey file |
| user (-u) | Username that should use the SSH pubkey *(Default: `root`)* |
| homedir (-d) | Path to users homedirectory *(Default: `/home/$user`)* |
| type (-t) | Imagetype *(Default: .raw)* |

**Usage:**

`inject-sshkey -i .build/kvm-cis-cloud.raw -u dev -k /home/vagrant/id_rsa.pub`


### start-vm
This script starts a given `.raw` or `.qcow2` image in a local QEMU/KVM VM and supports `amd64` and `arm64 builds`. Keep in mind, that running different architectures may be very slow. However, it may still be useful for validating and running unit tests. A spawned VM runs in `textmode` which a `hostfwd` (portforward) for SSH on `tcp/2222`. By the given options this allows the user to user copy/paste in the terminal, as well as connecting to the sshd. *(Hint: Custom SSH pubkeys can be injected with `inject-sshkey`.)*

**Acceleration Support:**

Currently, `start-vm` supports `KVM` and `HVF` acceleration. While `HVF` is only supported on macOS, `KVM` will mostly be used. When using `KVM` acceleration you need to ensure that `/dev/kvm` can be used by your user account. However, if `/dev/kvm` is not usable it will fallback to a non accelerated support that may still work but may be slower. Setting permissions on `/dev/kvm` can be don is several ways; for example:

```
# Adding specific user to related groups
sudo usermod -G -a kvm "$username"
sudo usermod -G -a libvirtd "$username"
```

```
# Setting permissions for all users
sudo chmod +666 /dev/kvm
```

**Network Bridge:**

Creating a network bridge requires `root` access and additional packages like `virsh`.

`Debian`: `apt-get install libvirt-clients libvirt`

`Ubuntu`: `apt-get install libvirt-clients libvirt`

`CentOS`: `yum install libvirt-client libvirt-daemon libvirt-daemon-driver-qemu libvirt-daemon-config-network`

`macOS`: `unsupported`


Creating a bridge with `virsh`:
```
# You may need to start unit `libvirtd`

# By default, it comes with a default profile
$> virsh net-list --all
 Name      State      Autostart   Persistent
----------------------------------------------
 default   inactive   no          yes

# Start the default profile
$> virsh net-start --network default

# A new device virbr0 is up
$> ip addr show virbr0
12: virbr0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default qlen 1000
    link/ether 52:54:00:d4:dd:c1 brd ff:ff:ff:ff:ff:ff
    inet 192.168.122.1/24 brd 192.168.122.255 scope global virbr0
       valid_lft forever preferred_lft forever

# Stat QEMU bridge with bridge interface
$> bin/start-vm --bridge virbr0 .build/kvm_dev-amd64-today-local.raw
```

**Options:**
| Option (short) | Descriptions |
|--|--|
| --arch | Architecture to use [`amd64`, `arm64`] |
| --cpu | CPU type to emulate if an specific should be used |
| --mem | Memory size to use for VM |
| --uuefi | Run in `UEFI` mode instead of legacy `Bios`|
| --ueficode | Path to custom UEFI Code file |
| --uefivars | Path to custom UEFI Vars file |
| --skipkp |Skip keypress (boots directly the image) |
| --vnc | Starts a VNC server session |
| --bridge <interface> | Uses a network bridge with a defined interface (needs root) |

**Usage:**

Running same arch: `start-vm /path/to/$image_name`

Running specific arch (e.g. `aarch64`): `start-vm --arch aarch64 /path/to/$image_name`

### make-ali-ami
This script orchestrates the upload/integration of a Garden Linux image for the `ALI` platform.

**Options:**
| Option | Descriptions |
|--|--|
| Platform | Defines the platform type |
| ImageName | Image to use |
| DiskDeviceMapping.1.OSSBucket | Custom OSSBocket (mostly equal to Bucketname) |
| DiskDeviceMapping.1.Format | Image format (mostly `.qcow2`)
| RegionId | Region ID to use |

**Usage:**

`make-ali-ami --Platform=Others Linux --ImageName= --DiskDeviceMapping.1.OSSBucket= --DiskDeviceMapping.1.OSSObject= --DiskDeviceMapping.1.Format=qcow2 --DiskDeviceMapping.1.DiskImSize=5 --RegionId=EU`

### make-azure-ami
This script orchestrates the upload/integration of a Garden Linux image for the `Azure` platform.

| Option | Descriptions |
|--|--|
| resource-group | Name of the storage group to use |
| storage-account-name | Name of the storage account to use |
| image-name | Name of the image to use |
| image-path | Path to the image to use |
| subscription | Subscription to use |

**Usage:**

`make-azure-ami --storage-account-name STORAGE_ACCOUNT_NAME --image-name IMAGE_NAME --image-path IMAGE_PATH --subscription SUBSCRIPTION`

### make-ec2-ami
This script orchestrates the upload/integration of a Garden Linux image for the `EC2` platform.

| Option | Descriptions |
|--|--|
| bucket | Name of the bucket to use |
| permission-public | Option to declare as public / private |
| region | Region to use |
| image-name | Name of the image to use |
| tags | Add custom tags |


**Usage:**

`make-ec2-ami --bucket BUCKET [--permission-public PERMISSION_PUBLIC] [--distribute DISTRIBUTE] --region REGION --image-name IMAGE_NAME`

### make-gcp-ami
This script orchestrates the upload/integration of a Garden Linux image for the `GCP` platform.

| Option | Descriptions |
|--|--|
| bucket | Name of the bucket to use |
| permission-public | Option to declare as public / private |
| raw-image-path | Name of the image to use |
| region | Region to use |
| image-name | Name of the image to use |
| project | Name of the project to use |
| tags | Add custom tags |

**Usage:**

`make-gcp-ami [--region REGION] --bucket BUCKET --raw-image-path RAW_IMAGE_PATH --image-name IMAGE_NAME [--permission-public PERMISSION_PUBLIC] [--project PROJECT] [--debug] [--labels LABELS]`

### make-ova
This script converts a given `.raw` image file into a `.ova` image file.

*(Hint: This needs the Python module `mako.template`)*

**Usage:**

`make-ova /path/to/$image_name.raw`


### make-vhd
This script converts a given `.raw` image file into a `.vhd` image file.

**Usage:**

`make-vhd /path/to/$image_name.raw`
