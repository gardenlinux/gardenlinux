# Garden Linux Binary Set
## General
This directory contains many scripts to manage the Garden Linux build process. While most of them are used in a Docker container during the Garden Linux build (e.g. `garden-build`, `garden-test`, `makepart`, ...) there are also several useful scripts (e.g. `start-vm`, `inject-sshkey`, ...) that may be used afterwards.

## Overview
By the given directory, we distinguish between scripts that are mandatory for the Garden Linux build process and scripts that are optional but very useful for handling a final Garden Linux artifact. Therefore, we describe them by the given two sections and only describe the standalone usable ones in detail.

### Mandatory for Garden Linux Build Process
| Name | Descriptions |
|--|--|
| garden-apt-get | Handles `apt-get` commands in `chroot` env |
| garden-build | Main script to build Garden Linux (creates a `chroot` env in a Docker container) |
| garden-chroot | Performs all necessary steps to integrate Garden Linux features |
| garden-config | Performs adjustments by activated `features` |
| garden-debian-sources-list | Adjusts the Garden Linux repository and pins priorities |
| garden-feat.go | Helper script to validate defined `features` (include, exclude, depends) |
| garden-fixup | Helper script to clean up uneeded files after build process |
| garden-fs | Creates the filesystem layout by `features` (creates: `fstab`) |
| garden-init | Debootstraps Garden Linux |
| garden-slimify | Creates a slimifyed version of Garden Linux |
| garden-tar | Creates a `.tar.xf` image of the build env from `chroot` env |
| garden-test | Performs basic unit tests |
| garden-version | Creates a version schema |
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

**Usage:**

`startvm /path/to/$image_name`


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