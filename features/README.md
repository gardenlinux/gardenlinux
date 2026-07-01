# Features

## General
Each folder represents a usable Garden Linux `feature` that can be added to a final Garden Linux artifact. This allows you to build Garden Linux for different cloud platforms (e.g. `azure`, `gcp`, `container` etc.) with a different set of features like `cis`, `firewall` etc. The three feature types are defined in [ADR 0034](https://github.com/gardenlinux/gardenlinux/blob/main/docs/reference/adr/0034-feature-terminology.md):

| Feature type | Description | Examples |
|---|---|---|
| `platform` | Deployment target (cloud provider, hypervisor, or hardware environment). Exactly one platform feature must be present in a well-formed build. | `ali`, `aws`, `azure`, `baremetal`, `gcp`, `kvm`, ... |
| `element` | Functional component or capability added on top of the platform. Multiple elements may be present. | `cis`, `fedramp`, `firewall`, `gardener`, `metal`, `ssh`, ... |
| `flag` | Lightweight modifier. Identified by a leading `_` in the feature name. | `_fips`, `_iso`, `_pxe`, `_prod`, `_readonly`, `_slim`, ... |

*Keep in mind that `not all features` may be combined together. However, features may in-/exclude other features or block the build process by given exclusive/incompatible feature combinations.*

## Building a custom set of features

Garden Linux uses the [gardenlinux/builder](https://github.com/gardenlinux/builder) to create customized Linux distributions. The `gardenlinux/gardenlinux` repository is maintained by the Garden Linux team and provides specialized features that are also available for other projects.

The build command takes a **flavor** (`{cname}-{arch}`) as its argument — the version is resolved automatically by the script. For a full explanation of the naming hierarchy — cname, flavor, versioned flavor, and artifact base name — see [ADR 0035](https://github.com/gardenlinux/gardenlinux/blob/main/docs/reference/adr/0035-cname-flavor-artifact-naming.md) and the [Builder documentation](https://github.com/gardenlinux/builder/blob/main/docs/how-to/building-images.md).

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

To e.g. build an the AWS image `aws-gardener_prod_trustedboot_tpm2-amd64`, you have to define the corresponding features and architecture like this.

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
