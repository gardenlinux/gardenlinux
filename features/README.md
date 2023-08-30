# Features

## General
Each folder represents a usable Garden Linux `feature` that can be added to a final Garden Linux artifact. This allows you to build Garden Linux for different cloud platforms (e.g. `azure`, `gcp`, `container` etc.) with a different set of features like `CIS`, `read_only`, `firewall` etc. Currently, the following feature types are available:

| Feature Type | Feature Name |
|---|---|
| Platform | `ali`, `aws`, `azure`, `gcp`, `kvm`, `metal`, ... |
| Feature | `firewall`, `gardener`, `ssh`, ... |
| Modifier | `_slim`, `_readonly`, `_pxe`, `_iso`, ... |
| Element | `cis`, `fedramp`, ... |

*Keep in mind that `not all features` may be combined together. However, features may in-/exclude other features or block the build process by given exclusive/incompatible feature combinations.*

## Building a custom set of features and modifiers

Garden Linux utilizes the [gardenlinux/builder](https://github.com/gardenlinux/builder) to create customized Linux distributions. The `gardenlinux/gardenlinux` repository is maintained by the Garden Linux team, highlighting specialized "features" that are also available for other projects.

To initiate a build, navigate to the root directory of the `gardenlinux/gardenlinux` repository and use the command:

```bash
./build ${platform}-${feature}_${modifier}
```

Where:

- `${platform}` denotes the desired platform (e.g., kvm, metal, aws).
- `${feature}` represents a specific feature from the `features/` folder.
- `${modifier}` is an optional modifier from the `features/` folder, prefixed with an underscore "_".

You can combine multiple platforms, features, and modifiers as needed.

## Official Combinations

Garden Linux images are constructed during the [nightly GitHub action](https://github.com/gardenlinux/gardenlinux/blob/main/.github/workflows/nightly.yml). The following table showcases the flavors that are built and tested with each nightly run.


| Platform | feature/modifier combinations |
|----------|--------------------------------------------|
| KVM      | `kvm-gardener_prod`                        |
|          | `kvm_secureboot-gardener_prod`             |
|          | `kvm_secureboot_readonly-gardener_prod`    |
|          | `kvm_secureboot_readonly_persistence-gardener_prod` |
| Metal    | `metal-gardener_prod`                      |
|          | `metal_secureboot-gardener_prod`           |
|          | `metal_secureboot_readonly-gardener_prod`  |
|          | `metal_secureboot_readonly_persistence-gardener_prod` |
|          | `metal_pxe-gardener_prod`                  |
|          | `metal-vhost-gardener_prod`                |
| GCP      | `gcp-gardener_prod`                        |
| AWS      | `aws-gardener_prod`                        |
|          | `aws_secureboot-gardener_prod`             |
|          | `aws_secureboot_readonly-gardener_prod`    |
|          | `aws_secureboot_readonly_persistence-gardener_prod` |
| Azure    | `azure-gardener_prod`                      |
| Ali      | `ali-gardener_prod`                        |
| OpenStack| `openstack-gardener_prod`                  |
| VMware   | `vmware-gardener_prod`                     |
| Firecracker | `firecracker-gardener_prod`             |

