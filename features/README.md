# Features

## General
Each folder represents a usable Garden Linux `feature` that can be added to a final Garden Linux artifact. This allows you to build Garden Linux for different cloud platforms (e.g. `azure`, `gcp`, `container` etc.) with a different set of features like `CIS`, `read_only`, `firewall` etc. Currently, the following feature types are available:

| Feature Type | Feature Name |
|---|---|
| platform | `ali`, `aws`, `azure`, `gcp`, `kvm`, `metal`, ... |
| flag | `firewall`, `gardener`, `ssh`, `_prod`, `_slim`, `_readonly`, `_pxe`, `_iso`, ... |
| Element | `cis`, `fedramp`, ... |

*Keep in mind that `not all features` may be combined together. However, features may in-/exclude other features or block the build process by given exclusive/incompatible feature combinations.*

## Building a custom set of features

Garden Linux utilizes the [gardenlinux/builder](https://github.com/gardenlinux/builder) to create customized Linux distributions and their flavors. The `gardenlinux/gardenlinux` repository is maintained by the Garden Linux team, highlighting specialized "features" that are also available for other projects.

To initiate a build, navigate to the root directory of the `gardenlinux/gardenlinux` repository and use the command:

```bash
./build ${platform}-${feature1}-${feature2}-${feature3}-${arch}
```

Where:

- `${platform}` denotes the desired platform (e.g., kvm, metal, aws). It should be the first part of the flavor that is built.
- `${featureX}` represents one or more specific features from the `features/` folder. Features are appended and seperated by a hyphen `-` or (if the feature starts with an underscore `_`) by an underscore.
- `${arch}` optinally you can reference a certain architecture `amd64` or `arm64`. It should be the last part of the flavor that is built.

You can combine multiple platforms and features as needed.

## Official Published Flavors

Flavors are combinations of features. Garden Linux is built via the [nightly GitHub action](https://github.com/gardenlinux/gardenlinux/blob/main/.github/workflows/nightly.yml). The following table showcases the flavors that are built and tested with each nightly run.

| Platform   | Architecture       | Flavor                                  |
|------------|--------------------|------------------------------------------|
| ali        | amd64              | `ali-gardener_prod-amd64`                   |
| aws        | amd64              | `aws-gardener_prod-amd64`                   |
| aws        | arm64              | `aws-gardener_prod-arm64`                   |
| aws        | amd64              | `aws-gardener_prod_trustedboot_tpm2-amd64`                   |
| aws        | arm64              | `aws-gardener_prod_trustedboot_tpm2-arm64`                   |
| azure      | amd64              | `azure-gardener_prod-amd64`                   |
| azure      | arm64              | `azure-gardener_prod-arm64`                   |
| azure      | amd64              | `azure-gardener_prod_trustedboot_tpm2-amd64`                   |
| azure      | amd64              | `azure-gardener_prod_trustedboot_tpm2-arm64`                   |
| bare       | amd64              | `bare-libc-amd64`                   |
| bare       | arm64              | `bare-libc-arm64`                   |
| bare       | amd64              | `bare-nodejs-amd64`                   |
| bare       | arm64              | `bare-nodejs-arm64`                   |
| bare       | amd64              | `bare-python-amd64`                   |
| bare       | arm64              | `bare-python-arm64`                   |
| bare       | amd64              | `bare-sapmachine-amd64`                   |
| bare       | arm64              | `bare-sapmachine-arm64`                   |
| container  | amd64              | `container-amd64`                   |
| container  | arm64              | `container-arm64`                   |
| gcp        | amd64              | `gcp-gardener_prod-amd64`                   |
| gcp        | arm64              | `gcp-gardener_prod-arm64`                   |
| gcp        | amd64              | `gcp-gardener_prod_trustedboot_tpm2-amd64`                   |
| gcp        | arm64              | `gcp-gardener_prod_trustedboot_tpm2-arm64`                   |
| gdch       | amd64              | `gdch-gardener_prod-amd64`                   |
| gdch       | arm64              | `gdch-gardener_prod-arm64`                   |
| kvm        | amd64              | `kvm-gardener_prod-amd64`                   |
| kvm        | arm64              | `kvm-gardener_prod-arm64`                   |
| kvm        | amd64              | `kvm-gardener_prod_trustedboot_tpm2-amd64`                   |
| kvm        | arm64              | `kvm-gardener_prod_trustedboot_tpm2-arm64`                   |
| metal      | amd64              | `metal-gardener_prod-amd64`                   |
| metal      | arm64              | `metal-gardener_prod-arm64`                   |
| metal      | amd64              | `metal-gardener_prod_trustedboot_tpm2-amd64`                   |
| metal      | arm64              | `metal-gardener_prod_trustedboot_tpm2-arm64`                   |
| metal      | amd64              | `metal-gardener_prod_pxe-amd64`                   |
| metal      | arm64              | `metal-gardener_prod_pxe-arm64`                   |
| metal      | amd64              | `metal-gardener_prod-vhost-amd64`                   |
| metal      | arm64              | `metal-gardener_prod-vhost-arm64`                   |
| openstack  | amd64              | `openstack-gardener_prod-amd64`                   |
| openstack  | arm64              | `openstack-gardener_prod-arm64`                   |
| openstackbaremetal | amd64              | `openstackbaremetal-gardener_prod-amd64`                   |
| openstackbaremetal | arm64              | `openstackbaremetal-gardener_prod-arm64`                   |
| vmware     | amd64              | `vmware-gardener_prod-amd64`                   |
| vmware     | arm64              | `vmware-gardener_prod-arm64`                   |

The table can be created like this:

```
❯ bin/gl-flavors-parse --markdown-table-by-platform --publish
```

### `flavors.yaml`

The `flavors.yaml` file is used to define which flavors are to be build, tested and published.

To e.g. build an the AWS image `aws-gardener_prod_trustedboot_tpm2-amd64`, you have to define the coresponding features and architecture like this.

```
---
targets:
  - name: aws
    category: public-cloud
    flavors:
      - features:
          - gardener
          - _prod
          - _trustedboot
          - _tpm2
        arch: amd64
        build: true
        test: true
        test-platform: true
        publish: true
```

The `build`, `test`, `test-platform` and `publish` values are picked up by the respective github actions and will automatically include or exclude a flavor from them.

### `bin/flavor_parse.py`

This script is used to generate input for github actions.

```
# get all flavors for the publishing related workflows

❯ bin/gl-flavors-parse --no-arch --json-by-arch --publish
{
  "amd64": [
    "ali-gardener_prod-amd64",
    "aws-gardener_prod-amd64",
    "aws-gardener_prod_trustedboot_tpm2-amd64",
    "azure-gardener_prod-amd64",
    "azure-gardener_prod_trustedboot_tpm2-amd64",
    "bare-libc-amd64",
    "bare-nodejs-amd64",
    "bare-python-amd64",
    "bare-sapmachine-amd64",
    "container-amd64",
    "gcp-gardener_prod-amd64",
    "gcp-gardener_prod_trustedboot_tpm2-amd64",
    "gdch-gardener_prod-amd64",
    "kvm-gardener_prod-amd64",
    "kvm-gardener_prod_trustedboot_tpm2-amd64",
    "metal-gardener_prod-amd64",
    "metal-gardener_prod_trustedboot_tpm2-amd64",
    "metal-gardener_prod_pxe-amd64",
    "metal-gardener_prod-vhost-amd64",
    "openstack-gardener_prod-amd64",
    "openstackbaremetal-gardener_prod-amd64",
    "vmware-gardener_prod-amd64"
  ],
  "arm64": [
    "aws-gardener_prod-arm64",
    "aws-gardener_prod_trustedboot_tpm2-arm64",
    "azure-gardener_prod-arm64",
    "bare-libc-arm64",
    "bare-nodejs-arm64",
    "bare-python-arm64",
    "bare-sapmachine-arm64",
    "container-arm64",
    "gcp-gardener_prod-arm64",
    "gcp-gardener_prod_trustedboot_tpm2-arm64",
    "gdch-gardener_prod-arm64",
    "kvm-gardener_prod-arm64",
    "kvm-gardener_prod_trustedboot_tpm2-arm64",
    "metal-gardener_prod-arm64",
    "metal-gardener_prod_trustedboot_tpm2-arm64",
    "metal-gardener_prod_pxe-arm64",
    "metal-gardener_prod-vhost-arm64",
    "openstack-gardener_prod-arm64",
    "openstackbaremetal-gardener_prod-arm64",
    "vmware-gardener_prod-arm64"
  ]
}
```
