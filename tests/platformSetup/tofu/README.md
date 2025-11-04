# Platform Testing Infrastructure

This directory contains the infrastructure code used to automatically set up test environments across different cloud providers (AWS, Google Cloud, Azure, and Alibaba Cloud).

## Table of Contents

- [What is OpenTofu?](#what-is-opentofu)
- [OpenTofu Module Structure](#opentofu-module-structure)
- [OpenTofu in a Nutshell](#opentofu-in-a-nutshell)
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
    - [Tooling](#tooling)
    - [Python virtual environment](#python-virtual-environment)
  - [Understanding the Test Process](#understanding-the-test-process)
    - [Quick Start - Typical Workflow](#quick-start---typical-workflow)
    - [What Happens Behind the Scenes](#what-happens-behind-the-scenes)
  - [Cloud Provider Authentication](#cloud-provider-authentication)
    - [Amazon Web Services (AWS)](#amazon-web-services-aws)
    - [Google Cloud Platform (GCP)](#google-cloud-platform-gcp)
    - [Microsoft Azure](#microsoft-azure)
    - [Alibaba Cloud (ALI)](#alibaba-cloud-ali)
    - [Verifying Authentication](#verifying-authentication)
  - [Generate OpenTofu Input Variables](#generate-opentofu-input-variables)
    - [Manual Creation](#manual-creation)
    - [Automated Generation](#automated-generation)
  - [Creating Cloud Resources with OpenTofu](#creating-cloud-resources-with-opentofu)
    - [Available Commands](#available-commands)
    - [Full Command List](#full-command-list)
  - [Run Platform Tests](#run-platform-tests)
    - [Available Test Commands](#available-test-commands)
    - [Full Test Command List](#full-test-command-list)
    - [Debugging Failed Tests](#debugging-failed-tests)
  - [Workspaces and State Management](#workspaces-and-state-management)
    - [Understanding State](#understanding-state)
    - [Using Workspaces](#using-workspaces)
    - [How We Use Workspaces](#how-we-use-workspaces)
    - [State Storage](#state-storage)
- [Advanced Settings](#advanced-settings)
  - [Enhanced State Management](#enhanced-state-management)
    - [Using Encrypted Local State](#using-encrypted-local-state)
    - [Setting Up Remote State in S3](#setting-up-remote-state-in-s3)
    - [Recover GitHub Action's OpenTofu State Locally](#recover-github-actions-opentofu-state-locally)
- [Updating OpenTofu or Provider Versions](#updating-opentofu-or-providerversions)
- [GitHub Actions](#github-actions)
  - [Available Workflows](#available-workflows)
    - [nightly.yml - Automated Nightly Tests](#nightlyyml---automated-nightly-tests)
    - [tests-only.yml - On-Demand Testing](#tests-onlyyml---on-demand-testing)
- [Appendix](#appendix)
  - [OpenTofu in a Nutshell](#opentofu-in-a-nutshell)
    - [OpenTofu Configuration Language (HCL)](#opentofu-configuration-language-hcl)
    - [Basic HCL Syntax](#basic-hcl-syntax)
    - [Providers](#providers)
    - [Resource Types](#resource-types)
    - [Input and Output Values](#input-and-output-values)
    - [Data Sources](#data-sources)
    - [File Extensions and Organization](#file-extensions-and-organization)
    - [OpenTofu Commands](#opentofu-commands)

## What is OpenTofu?

OpenTofu is an infrastructure-as-code tool that allows us to define cloud resources (like virtual machines, networks, etc.) in code rather than clicking through web interfaces. When we run OpenTofu, it:

1. Reads our code that describes what we want
2. Figures out what needs to be created/changed
3. Makes those changes in the cloud automatically

This automation makes our testing process reliable and reproducible.

## OpenTofu Module Structure

Our OpenTofu test infrastructure is organized into modules:

- `tests/platformSetup/tofu` is the [Root Module](https://opentofu.org/docs/language/modules/#the-root-module)
- Inside this are [Child Modules](https://opentofu.org/docs/language/modules/#child-modules) for each cloud provider:
  ```
  tests/platformSetup/tofu/
  ├── .terraform.lock.hcl   # Terraform lock file
  ├── main.tf               # Main configuration file
  ├── outputs.tf            # Output definitions
  ├── providers.tf          # Provider definitions
  ├── variables.tf          # Variable definitions
  └── modules/              # Reusable modules
      ├── ali/              # Alibaba Cloud-specific resources
      ├── aws/              # AWS-specific resources
      ├── azure/            # Azure-specific resources
      └── gcp/              # Google Cloud-specific resources
          ├── main.tf       # GCP Main configuration file
          ├── variables.tf  # GCP Variable definitions
          └── outputs.tf    # GCP Output definitions
  ```

The root module:

- Configures boilerplate code and calls the cloud provider child modules in `main.tf`
- Defines common input variables in `variables.tf`
- Defines output variables in `outputs.tf`
- Defines providers in `providers.tf`
- Locks providers in `.terraform.lock.hcl`

## OpenTofu in a nutshell

Have a look at the [OpenTofu in a nutshell](./opentofu_in_a_nutshell.md) to get a general understanding of OpenTofu.

## Getting Started

### Requirements

#### Tooling

These tools are required on the local workstation and Github Actions.

- Python 3.11
- GNU Make
- `uuidgen`
- podman

##### Installation on debian based systems

```bash
$ sudo apt-get update
$ sudo apt-get install python3 python-is-python3 python3-venv make uuid-runtime podman
```

##### Installation on macOS

```bash
$ brew install python git make coreutils gnu-sed gnu-getopt podman vfkit
```

#### Python virtual environment

A virtual environment with minimum dependencies is required to run the make targets and the coresponding python scripts.

##### manual installation

```bash
# create virtual environment
$ python -m venv venv

# activate virtual environment
$ source venv/bin/activate

# install dependencies
$ pip install -r requirements.txt
```

##### use direnv

Direnv is a tool for managing environment variables for your project. It can be used to automatically load the virtual environment.

```bash
# Installation on debian based systems
$ sudo apt-get update
$ sudo apt-get install direnv

# Installation on macOS
$ brew install direnv

# add hook to bashrc
$ echo "eval \"\$(direnv hook bash)\"" >> ~/.bashrc

# add hook to zshrc
$ echo "eval \"\$(direnv hook zsh)\"" >> ~/.zshrc

# create .envrc file to load the virtual environment
$ echo "layout python3" > .envrc

# allow the .envrc file
$ direnv allow
```

### Understanding the Test Process

#### Quick Start - Typical Workflow

Here's the minimal sequence of commands to run a complete platform test.

Please be aware that you have to configure cloud provider authentication and settings before running the tests. Have a look at the [Cloud Provider Authentication](#cloud-provider-authentication) section for more information.

```bash
# 0. Build the image for the flavor you want to test
$ make gcp-gardener_prod-amd64-build

# 1. Generate variables for your flavor
$ make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-config

# 2. Create cloud resources
$ make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-apply

# 3. Run the tests
$ make --directory=tests gcp-gardener_prod-amd64-tofu-test-platform

# 4. Clean up when done
$ make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-destroy
  ```

> [!TIP]
> You can preview changes before applying them with the `plan` command:
> ```bash
> make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-plan
> ```

#### What Happens Behind the Scenes

When you run a platform test, this sequence occurs:

1. **Generate Input Variables** (make target calls `tests/platformSetup/platformSetup.py`):
   - Creates OpenTofu configuration files
   - Defines cloud resources to create
   - Sets up test parameters

2a. **Infrastructure Setup** (OpenTofu):
   - Configures networking
   - Sets up security groups/firewall rules
   - Uploads Garden Linux images
   - Creates virtual machines
   - Uploads SSH keys
   - Waits for SSH port to become available

2b. **Test Configuration** (make target calls `tests/platformSetup/platformSetup.py`):
    - Generates pytest configuration from OpenTofu output
    - Creates SSH connection script

3a. **Test Execution** (make target calls `pytest` via `tests/platformSetup/manual.py`):
   - Runs test suite
   - Collects test results
   - Reports success/failure

3b. **SSH Connection** (`tests/helper/sshclient.py`):
   - Establishes SSH connection
   - Handles connection retries if needed

4. **Infrastructure Cleanup** (OpenTofu):
   - Destroys all cloud resources

## Detailed Component Documentation

### Cloud Provider Authentication

Before running tests, you need to authenticate with the cloud providers you want to test against. Each provider has its own authentication method.

#### Amazon Web Services (AWS)

You can set up [IAM user credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-authentication-user.html) in two ways:

```bash
# Option 1: Interactive setup (Recommended for beginners)
$ aws configure
# This will prompt you for:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region
# - Default output format

# Option 2: Direct environment variables
$ export AWS_ACCESS_KEY_ID=my-access-key-id
$ export AWS_SECRET_ACCESS_KEY=my-access-key
```

> [!NOTE]
> For AWS, you can also use SSO authentication if your organization supports it.
> If you don't have AWS credentials, you can just leave those variables empty.

#### Google Cloud Platform (GCP)

GCP authentication requires both project setup and [user authentication via gcloud CLI](https://cloud.google.com/docs/authentication/gcloud):

```bash
# 1. Set your project ID (needed for OpenTofu)
$ export TF_VAR_gcp_project_id=my-gcp-project-id

# 2. First-time setup (only needed once)
$ gcloud init
$ gcloud config set project ${TF_VAR_gcp_project_id}

# 3. Authenticate your user account
$ gcloud auth application-default login

# 4. Set up project quotas
$ gcloud auth application-default \
  set-quota-project ${TF_VAR_gcp_project_id}
```

> [!NOTE]
> The Project ID can be found in the Google Cloud portal under Project info.
> If you don't have a Google Cloud project, the `Makefile` will set up a mocked value for you.

#### Microsoft Azure

You can set up [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli) authentication:

```bash
# 1. Log in to Azure (opens a web browser)
$ az login

# 2. Set your subscription ID (needed for OpenTofu)
$ export ARM_SUBSCRIPTION_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

> [!NOTE]
> The subscription ID can be found in the Azure portal under Subscriptions.
> If you don't have a subscription, you have to switch to the `azure_disabled` module in `tests/platformSetup/tofu/main.tf`.

#### Alibaba Cloud (ALI)

You can set up a [AccessKey pair](https://www.alibabacloud.com/help/en/cli/configure-credentials#0da5d08f581wn) in two ways:

```bash
# Option 1: Interactive setup
$ aliyun configure
# This will prompt you for your access key details

# Option 2: Direct environment variables
$ export ALIBABA_CLOUD_ACCESS_KEY_ID=my-access-key-id
$ export ALIBABA_CLOUD_ACCESS_KEY_SECRET=my-access-key-secret
$ export ALIBABA_CLOUD_REGION_ID=my-region-id  # e.g., 'eu-central-1'
```

> [!NOTE]
> If you don't have Alibaba Cloud credentials, you can just leave those variables empty.

### Verifying Authentication

After setting up authentication, you can verify it works:

```bash
# AWS
$ aws sts get-caller-identity

# GCP
$ gcloud auth list

# Azure
$ az account show

# Alibaba Cloud
$ aliyun sts GetCallerIdentity
```

If any of these commands fail, double-check your credentials and ensure you have the necessary permissions in your cloud account.

### Generate OpenTofu Input Variables

OpenTofu needs to know what resources to create. We define this using [Input Variables](https://opentofu.org/docs/language/values/variables/) in `.tfvars` files. These files tell OpenTofu:
- Which cloud provider to use
- Which image to use
- Which architecture to use
- What type and size of virtual machine to create
- Which features to enable
- And other configuration details

#### Manual Creation

You can create these files manually. Here's an example for testing a GCP instance with TPM and Trusted Boot:

```bash
cat tests/platformSetup/tofu/variables.gcp-gardener_prod_trustedboot_tpm2-amd64.tfvars
test_prefix = "bobs"                    # Prefix for resource names
flavors = [
  {
    "name": "gcp-gardener_prod_trustedboot_tpm2-amd64",  # Test configuration name
    "platform": "gcp",                                    # Cloud provider
    "features": [                                         # Enabled features
      "gardener",
      "_prod",
      "_trustedboot",
      "_tpm2"
    ],
    "arch": "amd64",                                     # CPU architecture
    "instance_type": "n1-standard-2",                    # VM size
    "image_file": "gcp-gardener_prod_trustedboot_tpm2-amd64-1708.0-2ed27597.gcpimage.tar.gz"
  }
]
```

> [!TIP]
> See all available options in `tests/platformSetup/tofu/variables.tf`

#### Automated Generation

We provide a helper script `platformSetup.py` to generate these files automatically.
It is called by the "-tofu-config" make targets but can also be called manually.

```bash
# use default settings
make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-config

# write a custom test prefix and image via IMAGE_NAME (cname)
TEST_PREFIX=myprefix IMAGE_NAME=gcp-gardener_prod_tpm2_trustedboot-amd64-1695.0-30903f3a \
  make --directory=tests/platformSetup \
  gcp-gardener_prod_tpm2_trustedboot-amd64-tofu-config
```

or


```bash
# Generate for a single flavor
./tests/platformSetup/platformSetup.py \
    --flavors gcp-gardener_prod_trustedboot_tpm2-amd64 \
    --provisioner tofu \
    --test-prefix myprefix \
    --create-tfvars

# Generate for a specific image version via providing the image cname
./tests/platformSetup/platformSetup.py \
    --flavors gcp-gardener_prod_trustedboot_tpm2-amd64 \
    --image-name gcp-gardener_prod_tpm2_trustedboot-amd64-1695.0-30903f3a \
    --provisioner tofu \
    --test-prefix myprefix \
    --create-tfvars
```

The script supports these options:

<details>
<summary>Click to see all available options</summary>

```bash
tests/platformSetup/platformSetup.py --help
usage: platformSetup.py [-h] --flavor FLAVOR --provisioner {qemu,tofu} [--image-path IMAGE_PATH] [--image_name IMAGE_NAME] [--test-prefix TEST_PREFIX] [--create-tfvars]

Generate pytest config files and SSH login scripts for platform tests.

options:
  -h, --help            show this help message and exit
  --flavor FLAVOR       The flavor to be tested (e.g., 'kvm-gardener_prod-amd64').
  --provisioner {qemu,tofu}
                        Provisioner to use: 'qemu' for local testing or 'tofu' for Cloud Provider testing.
  --image-path IMAGE_PATH
                        Base path for image files.
  --image-name IMAGE_NAME
                        Image name or cname style image reference: (e.g.,
                        cname: 'kvm-gardener_prod-amd64-1312.0-80ffcc87',
                        ali image: 'm-01234567890123456',
                        aws ami: 'ami-01234567890123456',
                        azure community gallery version: '/communityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/images/gardenlinux-gen2/versions/1443.18.0',
                        gcp image: 'projects/sap-se-gcp-gardenlinux/global/images/gardenlinux-gcp-gardener-prod-arm64-1443-18-97fd20ac'.  
  --test-prefix TEST_PREFIX
                        Test prefix for OpenTofu variable files.
  --create-tfvars       Create OpenTofu variables file.
```

</details>

> [!WARNING]
> Before running tests, ensure the variables file exists with the correct name, matching your test flavor (e.g., `variables.gcp-gardener_prod_trustedboot_tpm2-amd64.tfvars`)

#### Use existing published cloud images from the official gardenlinux releases

You can boot published cloud images from the official gardenlinux releases like e.g. [Release 1592.11](https://github.com/gardenlinux/gardenlinux/releases/tag/1592.11) by referencing the image path and image name in the `IMAGE_PATH` and `IMAGE_NAME` variables.

<details>
<summary>Click to see examples from the 1592.11 release page</summary>

### Alibaba Cloud (amd64)
```
- Region: cn-qingdao, Image-Id: m-m5egu859pen1zirm4oq7
- Region: cn-beijing, Image-Id: m-2zebu8dwbdsd6ljfjbt7
- Region: cn-zhangjiakou, Image-Id: m-8vb18b30std75xs4e63k
- Region: cn-huhehaote, Image-Id: m-hp3hpzgj2jg5nqy5sllx
- Region: cn-wulanchabu, Image-Id: m-0jl3o5dikabfhps47mg0
- Region: cn-hangzhou, Image-Id: m-bp1ffh0bkq6i7bdhe11n
- Region: cn-shanghai, Image-Id: m-uf64proklduqsghxhkc4
- Region: cn-nanjing, Image-Id: m-gc7718hb45i4xytz886l
- Region: cn-shenzhen, Image-Id: m-wz9hu13t40i0ih2igs81
- Region: cn-heyuan, Image-Id: m-f8z3fvro5mv6gewgovou
- Region: cn-guangzhou, Image-Id: m-7xvhd1sqjby03cycevu2
- Region: cn-fuzhou, Image-Id: m-gw03srokeh5268byc50w
- Region: cn-wuhan-lr, Image-Id: m-n4a7547miqvtbjpgxsg7
- Region: cn-chengdu, Image-Id: m-2vc6nu46u6yabe5s96do
- Region: cn-hongkong, Image-Id: m-j6c366a8ihn8e72g16l5
- Region: ap-northeast-1, Image-Id: m-6we41a4lp5x4gl2eg2rd
- Region: ap-northeast-2, Image-Id: m-mj7bb6u3hj4v60hyxpqb
- Region: ap-southeast-1, Image-Id: m-t4nexdp6lmgor0763h81
- Region: ap-southeast-3, Image-Id: m-8psf3khbhzofwz2hl9ea
- Region: ap-southeast-6, Image-Id: m-5ts9qtdazm1czjgadfk9
- Region: ap-southeast-5, Image-Id: m-k1a6j280bbsyxsnqlh5o
- Region: ap-southeast-7, Image-Id: m-0jo6wvx6k0etq17hhw0i
- Region: us-east-1, Image-Id: m-0xi876dy339wiuwvjnr0
- Region: us-west-1, Image-Id: m-rj9e925ny58dp11v5vcr
- Region: na-south-1, Image-Id: m-4hfj619kkh88ezi5qzqj
- Region: eu-west-1, Image-Id: m-d7oa2wbjsbs0jdlokq30
- Region: me-east-1, Image-Id: m-eb3iftxj7q49q54sw8l4
- Region: eu-central-1, Image-Id: m-gw82i8237f8c6sav1trn
```
### Amazon Web Services (amd64)
```
- Region: ap-south-1, Image-Id: ami-08a5221cfb4df1b32
- Region: eu-north-1, Image-Id: ami-04e0ffde54151d623
- Region: eu-west-3, Image-Id: ami-04ba476445b7dff9e
- Region: eu-south-1, Image-Id: ami-043de2b173e7e1056
- Region: eu-west-2, Image-Id: ami-098765bac39f081a5
- Region: eu-west-1, Image-Id: ami-0bac327257f5cae45
- Region: ap-northeast-3, Image-Id: ami-047be2850a852d279
- Region: ap-northeast-2, Image-Id: ami-0ed22e4e328986fd6
- Region: ap-northeast-1, Image-Id: ami-0fb1d5ee7cd03245c
- Region: me-central-1, Image-Id: ami-021b692bec37efee7
- Region: ca-central-1, Image-Id: ami-0dfb434faa3c0e9d6
- Region: sa-east-1, Image-Id: ami-0c918cc893cb42347
- Region: ap-southeast-1, Image-Id: ami-0fdc0feff84bbd1a2
- Region: ap-southeast-2, Image-Id: ami-0dccb41da9a560d1d
- Region: us-east-1, Image-Id: ami-0244a702c2f6284ff
- Region: us-east-2, Image-Id: ami-01280f1c3598309cc
- Region: us-west-1, Image-Id: ami-05323ef910f11c78b
- Region: us-west-2, Image-Id: ami-03489819870ecd18d
- Region: eu-central-1, Image-Id: ami-07f977508ed36098e
- Region: cn-north-1, Image-Id: ami-02f50bda7856ad7b1
- Region: cn-northwest-1, Image-Id: ami-0f292fde668b1b237
```
### Google Cloud Platform (amd64)
```
gcp_image_name: gardenlinux-gcp-ff804026cbe7b5f2d6f729e4-1592-11-9ce205a2
```
### Microsoft Azure (amd64)
```
# all regions (community gallery image):
Hyper V: V1, Azure Cloud: public, Image Id: /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme/Versions/1592.11.0
Hyper V: V2, Azure Cloud: public, Image Id: /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-gen2/Versions/1592.11.0
Hyper V: V1, Azure Cloud: china, Image Id: /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme/Versions/1592.11.0
Hyper V: V2, Azure Cloud: china, Image Id: /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme-gen2/Versions/1592.11.0
```
### Amazon Web Services (arm64)
```
- Region: ap-south-1, Image-Id: ami-0a4928d6e1fdb8669
- Region: eu-north-1, Image-Id: ami-0aa3bbb0314892ec9
- Region: eu-west-3, Image-Id: ami-02af249755256a978
- Region: eu-south-1, Image-Id: ami-0026defa7f91d9a42
- Region: eu-west-2, Image-Id: ami-0fc5a594766b2bf87
- Region: eu-west-1, Image-Id: ami-02ce5251e5a389f35
- Region: ap-northeast-3, Image-Id: ami-0028602988ff70085
- Region: ap-northeast-2, Image-Id: ami-09afb8d0e27b713fa
- Region: ap-northeast-1, Image-Id: ami-05d9471d212d827f6
- Region: me-central-1, Image-Id: ami-0db4179b239b607bd
- Region: ca-central-1, Image-Id: ami-07156beeeb52ce0d4
- Region: sa-east-1, Image-Id: ami-007450dc4d9a06247
- Region: ap-southeast-1, Image-Id: ami-07694a33c7f0729df
- Region: ap-southeast-2, Image-Id: ami-0d52079a549e9c94b
- Region: us-east-1, Image-Id: ami-0ceb70de5ee6ccfd5
- Region: us-east-2, Image-Id: ami-01d5dde0ebb8e35a8
- Region: us-west-1, Image-Id: ami-0f153f506de6df9b6
- Region: us-west-2, Image-Id: ami-01b674933e46a45b3
- Region: eu-central-1, Image-Id: ami-06a9ce5920796430b
- Region: cn-north-1, Image-Id: ami-0cf609af2a62a3b15
- Region: cn-northwest-1, Image-Id: ami-02ba2049f549e0d91
```
### Google Cloud Platform (arm64)
```
gcp_image_name: gardenlinux-gcp-c8504d3c3e67cf2fc7c3408c-1592-11-9ce205a2
```
### Microsoft Azure (arm64)
```
# all regions (community gallery image):
Hyper V: V2, Azure Cloud: public, Image Id: /CommunityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/Images/gardenlinux-nvme-arm64-gen2/Versions/1592.11.0
Hyper V: V2, Azure Cloud: china, Image Id: /CommunityGalleries/gardenlinux-8e6518fb-9ae0-4f66-abfd-9a06997e2492/Images/gardenlinux-nvme-arm64-gen2/Versions/1592.11.0
```

</details>

To get the default regions OpenTofu deploys instances to, you can run:

```bash
grep -A3 _region tests/platformSetup/tofu/variables.tf
```

<details>
<summary>Click to see output</summary>

```bash
variable "ali_region" {
  description = "AWS region"
  default     = "eu-west-1" # London
}
--
variable "aws_region" {
  description = "AWS region"
  default     = "eu-central-1"
}
--
variable "azure_region" {
  description = "Azure region"
  default     = "westeurope"
}
--
variable "gcp_region" {
  description = "GCP region"
  default     = "europe-west4"
}
--
variable "gcp_region_storage" {
  description = "GCP storage region"
  default     = "europe-west4"
}
--
variable "openstack_region" {
  description = "OpenStack region"
  default     = "RegionOne"
}
```

</details>

Now reference the image path and image name in the `IMAGE_PATH` and `IMAGE_NAME` variables when calling the `tofu-config` make targets.

```bash
# use an existing image for ali
IMAGE_PATH=cloud:// IMAGE_NAME=m-d7oa2wbjsbs0jdlokq30 \
  make --directory=tests/platformSetup \
  ali-gardener_prod-amd64-tofu-config

# use an existing image for aws
IMAGE_PATH=cloud:// IMAGE_NAME=ami-07f977508ed36098e \
  make --directory=tests/platformSetup \
  aws-gardener_prod-amd64-tofu-config

# use an existing image for azure
IMAGE_PATH=cloud:// IMAGE_NAME=/communityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/images/gardenlinux-gen2/versions/1592.11.0 \
  make --directory=tests/platformSetup \
  azure-gardener_prod-amd64-tofu-config

# use an existing image for gcp
IMAGE_PATH=cloud:// IMAGE_NAME=projects/sap-se-gcp-gardenlinux/global/images/gardenlinux-gcp-ff804026cbe7b5f2d6f729e4-1592-11-9ce205a2 \
  make --directory=tests/platformSetup \
  gcp-gardener_prod-amd64-tofu-config
```

After creating the OpenTofu variables file, you can create the cloud resources with the `tofu-apply` make targets as usual.

### Creating Cloud Resources with OpenTofu

Once you have your authentication and variables set up, you can create the cloud resources. We provide a Makefile to simplify this process.

#### Available Commands

View all available flavors and targets with:

```bash
make --directory=tests/platformSetup help
```

Each flavor has five basic commands:

- `plan` - Preview what OpenTofu will create/change
- `apply` - Create/update the resources
- `show` - Display current resources
- `login` - SSH into the created instance
- `destroy` - Remove all created resources

For example, for `gcp-gardener_prod-amd64`:
```bash
# Preview changes
make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-plan

# Create resources
make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-apply

# Show current state
make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-show

# SSH into instance
make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-login

# Clean up resources
make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-destroy
```

#### Full Command List

<details>
<summary>Click to see all available commands</summary>

```plaintext
make --directory=tests/platformSetup

Usage: make [target]

general targets:
help					List available tasks of the project                                     

Available Resource Provisioning targets for Official Flavors:

Qemu Provisioner Provisioning targets:
  ali-gardener_prod-amd64-qemu-apply                                            Create qemu resources for ali-gardener_prod-amd64
  ali-gardener_prod-amd64-qemu-login                                            Login to qemu ali-gardener_prod-amd64
  ali-gardener_prod-amd64-qemu-destroy                                          Destroy qemu resources for ali-gardener_prod-amd64
  aws-gardener_prod-amd64-qemu-apply                                            Create qemu resources for aws-gardener_prod-amd64
  aws-gardener_prod-amd64-qemu-login                                            Login to qemu aws-gardener_prod-amd64
  aws-gardener_prod-amd64-qemu-destroy                                          Destroy qemu resources for aws-gardener_prod-amd64
  aws-gardener_prod-arm64-qemu-apply                                            Create qemu resources for aws-gardener_prod-arm64
  aws-gardener_prod-arm64-qemu-login                                            Login to qemu aws-gardener_prod-arm64
  aws-gardener_prod-arm64-qemu-destroy                                          Destroy qemu resources for aws-gardener_prod-arm64
  aws-gardener_prod_tpm2_trustedboot-amd64-qemu-apply                           Create qemu resources for aws-gardener_prod_tpm2_trustedboot-amd64
  aws-gardener_prod_tpm2_trustedboot-amd64-qemu-login                           Login to qemu aws-gardener_prod_tpm2_trustedboot-amd64
  aws-gardener_prod_tpm2_trustedboot-amd64-qemu-destroy                         Destroy qemu resources for aws-gardener_prod_tpm2_trustedboot-amd64
  aws-gardener_prod_tpm2_trustedboot-arm64-qemu-apply                           Create qemu resources for aws-gardener_prod_tpm2_trustedboot-arm64
  aws-gardener_prod_tpm2_trustedboot-arm64-qemu-login                           Login to qemu aws-gardener_prod_tpm2_trustedboot-arm64
  aws-gardener_prod_tpm2_trustedboot-arm64-qemu-destroy                         Destroy qemu resources for aws-gardener_prod_tpm2_trustedboot-arm64
  aws-gardener_prod_trustedboot-amd64-qemu-apply                                Create qemu resources for aws-gardener_prod_trustedboot-amd64
  aws-gardener_prod_trustedboot-amd64-qemu-login                                Login to qemu aws-gardener_prod_trustedboot-amd64
  aws-gardener_prod_trustedboot-amd64-qemu-destroy                              Destroy qemu resources for aws-gardener_prod_trustedboot-amd64
  aws-gardener_prod_trustedboot-arm64-qemu-apply                                Create qemu resources for aws-gardener_prod_trustedboot-arm64
  aws-gardener_prod_trustedboot-arm64-qemu-login                                Login to qemu aws-gardener_prod_trustedboot-arm64
  aws-gardener_prod_trustedboot-arm64-qemu-destroy                              Destroy qemu resources for aws-gardener_prod_trustedboot-arm64
  azure-gardener_prod-amd64-qemu-apply                                          Create qemu resources for azure-gardener_prod-amd64
  azure-gardener_prod-amd64-qemu-login                                          Login to qemu azure-gardener_prod-amd64
  azure-gardener_prod-amd64-qemu-destroy                                        Destroy qemu resources for azure-gardener_prod-amd64
  azure-gardener_prod-arm64-qemu-apply                                          Create qemu resources for azure-gardener_prod-arm64
  azure-gardener_prod-arm64-qemu-login                                          Login to qemu azure-gardener_prod-arm64
  azure-gardener_prod-arm64-qemu-destroy                                        Destroy qemu resources for azure-gardener_prod-arm64
  azure-gardener_prod_tpm2_trustedboot-amd64-qemu-apply                         Create qemu resources for azure-gardener_prod_tpm2_trustedboot-amd64
  azure-gardener_prod_tpm2_trustedboot-amd64-qemu-login                         Login to qemu azure-gardener_prod_tpm2_trustedboot-amd64
  azure-gardener_prod_tpm2_trustedboot-amd64-qemu-destroy                       Destroy qemu resources for azure-gardener_prod_tpm2_trustedboot-amd64
  azure-gardener_prod_trustedboot-amd64-qemu-apply                              Create qemu resources for azure-gardener_prod_trustedboot-amd64
  azure-gardener_prod_trustedboot-amd64-qemu-login                              Login to qemu azure-gardener_prod_trustedboot-amd64
  azure-gardener_prod_trustedboot-amd64-qemu-destroy                            Destroy qemu resources for azure-gardener_prod_trustedboot-amd64
  gcp-gardener_prod-amd64-qemu-apply                                            Create qemu resources for gcp-gardener_prod-amd64
  gcp-gardener_prod-amd64-qemu-login                                            Login to qemu gcp-gardener_prod-amd64
  gcp-gardener_prod-amd64-qemu-destroy                                          Destroy qemu resources for gcp-gardener_prod-amd64
  gcp-gardener_prod-arm64-qemu-apply                                            Create qemu resources for gcp-gardener_prod-arm64
  gcp-gardener_prod-arm64-qemu-login                                            Login to qemu gcp-gardener_prod-arm64
  gcp-gardener_prod-arm64-qemu-destroy                                          Destroy qemu resources for gcp-gardener_prod-arm64
  gcp-gardener_prod_tpm2_trustedboot-amd64-qemu-apply                           Create qemu resources for gcp-gardener_prod_tpm2_trustedboot-amd64
  gcp-gardener_prod_tpm2_trustedboot-amd64-qemu-login                           Login to qemu gcp-gardener_prod_tpm2_trustedboot-amd64
  gcp-gardener_prod_tpm2_trustedboot-amd64-qemu-destroy                         Destroy qemu resources for gcp-gardener_prod_tpm2_trustedboot-amd64
  gcp-gardener_prod_tpm2_trustedboot-arm64-qemu-apply                           Create qemu resources for gcp-gardener_prod_tpm2_trustedboot-arm64
  gcp-gardener_prod_tpm2_trustedboot-arm64-qemu-login                           Login to qemu gcp-gardener_prod_tpm2_trustedboot-arm64
  gcp-gardener_prod_tpm2_trustedboot-arm64-qemu-destroy                         Destroy qemu resources for gcp-gardener_prod_tpm2_trustedboot-arm64
  gcp-gardener_prod_trustedboot-amd64-qemu-apply                                Create qemu resources for gcp-gardener_prod_trustedboot-amd64
  gcp-gardener_prod_trustedboot-amd64-qemu-login                                Login to qemu gcp-gardener_prod_trustedboot-amd64
  gcp-gardener_prod_trustedboot-amd64-qemu-destroy                              Destroy qemu resources for gcp-gardener_prod_trustedboot-amd64
  gcp-gardener_prod_trustedboot-arm64-qemu-apply                                Create qemu resources for gcp-gardener_prod_trustedboot-arm64
  gcp-gardener_prod_trustedboot-arm64-qemu-login                                Login to qemu gcp-gardener_prod_trustedboot-arm64
  gcp-gardener_prod_trustedboot-arm64-qemu-destroy                              Destroy qemu resources for gcp-gardener_prod_trustedboot-arm64
  kvm-gardener_prod-amd64-qemu-apply                                            Create qemu resources for kvm-gardener_prod-amd64
  kvm-gardener_prod-amd64-qemu-login                                            Login to qemu kvm-gardener_prod-amd64
  kvm-gardener_prod-amd64-qemu-destroy                                          Destroy qemu resources for kvm-gardener_prod-amd64
  kvm-gardener_prod-arm64-qemu-apply                                            Create qemu resources for kvm-gardener_prod-arm64
  kvm-gardener_prod-arm64-qemu-login                                            Login to qemu kvm-gardener_prod-arm64
  kvm-gardener_prod-arm64-qemu-destroy                                          Destroy qemu resources for kvm-gardener_prod-arm64
  kvm-gardener_prod_tpm2_trustedboot-amd64-qemu-apply                           Create qemu resources for kvm-gardener_prod_tpm2_trustedboot-amd64
  kvm-gardener_prod_tpm2_trustedboot-amd64-qemu-login                           Login to qemu kvm-gardener_prod_tpm2_trustedboot-amd64
  kvm-gardener_prod_tpm2_trustedboot-amd64-qemu-destroy                         Destroy qemu resources for kvm-gardener_prod_tpm2_trustedboot-amd64
  kvm-gardener_prod_tpm2_trustedboot-arm64-qemu-apply                           Create qemu resources for kvm-gardener_prod_tpm2_trustedboot-arm64
  kvm-gardener_prod_tpm2_trustedboot-arm64-qemu-login                           Login to qemu kvm-gardener_prod_tpm2_trustedboot-arm64
  kvm-gardener_prod_tpm2_trustedboot-arm64-qemu-destroy                         Destroy qemu resources for kvm-gardener_prod_tpm2_trustedboot-arm64
  kvm-gardener_prod_trustedboot-amd64-qemu-apply                                Create qemu resources for kvm-gardener_prod_trustedboot-amd64
  kvm-gardener_prod_trustedboot-amd64-qemu-login                                Login to qemu kvm-gardener_prod_trustedboot-amd64
  kvm-gardener_prod_trustedboot-amd64-qemu-destroy                              Destroy qemu resources for kvm-gardener_prod_trustedboot-amd64
  kvm-gardener_prod_trustedboot-arm64-qemu-apply                                Create qemu resources for kvm-gardener_prod_trustedboot-arm64
  kvm-gardener_prod_trustedboot-arm64-qemu-login                                Login to qemu kvm-gardener_prod_trustedboot-arm64
  kvm-gardener_prod_trustedboot-arm64-qemu-destroy                              Destroy qemu resources for kvm-gardener_prod_trustedboot-arm64

Tofu Provisioner Provisioning targets:
  ali-gardener_prod-amd64-tofu-config                                           Create tofu config for ali-gardener_prod-amd64
  ali-gardener_prod-amd64-tofu-plan                                             Run tofu plan for ali-gardener_prod-amd64
  ali-gardener_prod-amd64-tofu-apply                                            Run tofu apply for ali-gardener_prod-amd64
  ali-gardener_prod-amd64-tofu-show                                             Run tofu show for ali-gardener_prod-amd64
  ali-gardener_prod-amd64-tofu-login                                            Run tofu login for ali-gardener_prod-amd64
  ali-gardener_prod-amd64-tofu-destroy                                          Run tofu destroy for ali-gardener_prod-amd64
  aws-gardener_prod-amd64-tofu-config                                           Create tofu config for aws-gardener_prod-amd64
  aws-gardener_prod-amd64-tofu-plan                                             Run tofu plan for aws-gardener_prod-amd64
  aws-gardener_prod-amd64-tofu-apply                                            Run tofu apply for aws-gardener_prod-amd64
  aws-gardener_prod-amd64-tofu-show                                             Run tofu show for aws-gardener_prod-amd64
  aws-gardener_prod-amd64-tofu-login                                            Run tofu login for aws-gardener_prod-amd64
  aws-gardener_prod-amd64-tofu-destroy                                          Run tofu destroy for aws-gardener_prod-amd64
  aws-gardener_prod-arm64-tofu-config                                           Create tofu config for aws-gardener_prod-arm64
  aws-gardener_prod-arm64-tofu-plan                                             Run tofu plan for aws-gardener_prod-arm64
  aws-gardener_prod-arm64-tofu-apply                                            Run tofu apply for aws-gardener_prod-arm64
  aws-gardener_prod-arm64-tofu-show                                             Run tofu show for aws-gardener_prod-arm64
  aws-gardener_prod-arm64-tofu-login                                            Run tofu login for aws-gardener_prod-arm64
  aws-gardener_prod-arm64-tofu-destroy                                          Run tofu destroy for aws-gardener_prod-arm64
  aws-gardener_prod_tpm2_trustedboot-amd64-tofu-config                          Create tofu config for aws-gardener_prod_tpm2_trustedboot-amd64
  aws-gardener_prod_tpm2_trustedboot-amd64-tofu-plan                            Run tofu plan for aws-gardener_prod_tpm2_trustedboot-amd64
  aws-gardener_prod_tpm2_trustedboot-amd64-tofu-apply                           Run tofu apply for aws-gardener_prod_tpm2_trustedboot-amd64
  aws-gardener_prod_tpm2_trustedboot-amd64-tofu-show                            Run tofu show for aws-gardener_prod_tpm2_trustedboot-amd64
  aws-gardener_prod_tpm2_trustedboot-amd64-tofu-login                           Run tofu login for aws-gardener_prod_tpm2_trustedboot-amd64
  aws-gardener_prod_tpm2_trustedboot-amd64-tofu-destroy                         Run tofu destroy for aws-gardener_prod_tpm2_trustedboot-amd64
  aws-gardener_prod_tpm2_trustedboot-arm64-tofu-config                          Create tofu config for aws-gardener_prod_tpm2_trustedboot-arm64
  aws-gardener_prod_tpm2_trustedboot-arm64-tofu-plan                            Run tofu plan for aws-gardener_prod_tpm2_trustedboot-arm64
  aws-gardener_prod_tpm2_trustedboot-arm64-tofu-apply                           Run tofu apply for aws-gardener_prod_tpm2_trustedboot-arm64
  aws-gardener_prod_tpm2_trustedboot-arm64-tofu-show                            Run tofu show for aws-gardener_prod_tpm2_trustedboot-arm64
  aws-gardener_prod_tpm2_trustedboot-arm64-tofu-login                           Run tofu login for aws-gardener_prod_tpm2_trustedboot-arm64
  aws-gardener_prod_tpm2_trustedboot-arm64-tofu-destroy                         Run tofu destroy for aws-gardener_prod_tpm2_trustedboot-arm64
  aws-gardener_prod_trustedboot-amd64-tofu-config                               Create tofu config for aws-gardener_prod_trustedboot-amd64
  aws-gardener_prod_trustedboot-amd64-tofu-plan                                 Run tofu plan for aws-gardener_prod_trustedboot-amd64
  aws-gardener_prod_trustedboot-amd64-tofu-apply                                Run tofu apply for aws-gardener_prod_trustedboot-amd64
  aws-gardener_prod_trustedboot-amd64-tofu-show                                 Run tofu show for aws-gardener_prod_trustedboot-amd64
  aws-gardener_prod_trustedboot-amd64-tofu-login                                Run tofu login for aws-gardener_prod_trustedboot-amd64
  aws-gardener_prod_trustedboot-amd64-tofu-destroy                              Run tofu destroy for aws-gardener_prod_trustedboot-amd64
  aws-gardener_prod_trustedboot-arm64-tofu-config                               Create tofu config for aws-gardener_prod_trustedboot-arm64
  aws-gardener_prod_trustedboot-arm64-tofu-plan                                 Run tofu plan for aws-gardener_prod_trustedboot-arm64
  aws-gardener_prod_trustedboot-arm64-tofu-apply                                Run tofu apply for aws-gardener_prod_trustedboot-arm64
  aws-gardener_prod_trustedboot-arm64-tofu-show                                 Run tofu show for aws-gardener_prod_trustedboot-arm64
  aws-gardener_prod_trustedboot-arm64-tofu-login                                Run tofu login for aws-gardener_prod_trustedboot-arm64
  aws-gardener_prod_trustedboot-arm64-tofu-destroy                              Run tofu destroy for aws-gardener_prod_trustedboot-arm64
  azure-gardener_prod-amd64-tofu-config                                         Create tofu config for azure-gardener_prod-amd64
  azure-gardener_prod-amd64-tofu-plan                                           Run tofu plan for azure-gardener_prod-amd64
  azure-gardener_prod-amd64-tofu-apply                                          Run tofu apply for azure-gardener_prod-amd64
  azure-gardener_prod-amd64-tofu-show                                           Run tofu show for azure-gardener_prod-amd64
  azure-gardener_prod-amd64-tofu-login                                          Run tofu login for azure-gardener_prod-amd64
  azure-gardener_prod-amd64-tofu-destroy                                        Run tofu destroy for azure-gardener_prod-amd64
  azure-gardener_prod-arm64-tofu-config                                         Create tofu config for azure-gardener_prod-arm64
  azure-gardener_prod-arm64-tofu-plan                                           Run tofu plan for azure-gardener_prod-arm64
  azure-gardener_prod-arm64-tofu-apply                                          Run tofu apply for azure-gardener_prod-arm64
  azure-gardener_prod-arm64-tofu-show                                           Run tofu show for azure-gardener_prod-arm64
  azure-gardener_prod-arm64-tofu-login                                          Run tofu login for azure-gardener_prod-arm64
  azure-gardener_prod-arm64-tofu-destroy                                        Run tofu destroy for azure-gardener_prod-arm64
  azure-gardener_prod_tpm2_trustedboot-amd64-tofu-config                        Create tofu config for azure-gardener_prod_tpm2_trustedboot-amd64
  azure-gardener_prod_tpm2_trustedboot-amd64-tofu-plan                          Run tofu plan for azure-gardener_prod_tpm2_trustedboot-amd64
  azure-gardener_prod_tpm2_trustedboot-amd64-tofu-apply                         Run tofu apply for azure-gardener_prod_tpm2_trustedboot-amd64
  azure-gardener_prod_tpm2_trustedboot-amd64-tofu-show                          Run tofu show for azure-gardener_prod_tpm2_trustedboot-amd64
  azure-gardener_prod_tpm2_trustedboot-amd64-tofu-login                         Run tofu login for azure-gardener_prod_tpm2_trustedboot-amd64
  azure-gardener_prod_tpm2_trustedboot-amd64-tofu-destroy                       Run tofu destroy for azure-gardener_prod_tpm2_trustedboot-amd64
  azure-gardener_prod_trustedboot-amd64-tofu-config                             Create tofu config for azure-gardener_prod_trustedboot-amd64
  azure-gardener_prod_trustedboot-amd64-tofu-plan                               Run tofu plan for azure-gardener_prod_trustedboot-amd64
  azure-gardener_prod_trustedboot-amd64-tofu-apply                              Run tofu apply for azure-gardener_prod_trustedboot-amd64
  azure-gardener_prod_trustedboot-amd64-tofu-show                               Run tofu show for azure-gardener_prod_trustedboot-amd64
  azure-gardener_prod_trustedboot-amd64-tofu-login                              Run tofu login for azure-gardener_prod_trustedboot-amd64
  azure-gardener_prod_trustedboot-amd64-tofu-destroy                            Run tofu destroy for azure-gardener_prod_trustedboot-amd64
  gcp-gardener_prod-amd64-tofu-config                                           Create tofu config for gcp-gardener_prod-amd64
  gcp-gardener_prod-amd64-tofu-plan                                             Run tofu plan for gcp-gardener_prod-amd64
  gcp-gardener_prod-amd64-tofu-apply                                            Run tofu apply for gcp-gardener_prod-amd64
  gcp-gardener_prod-amd64-tofu-show                                             Run tofu show for gcp-gardener_prod-amd64
  gcp-gardener_prod-amd64-tofu-login                                            Run tofu login for gcp-gardener_prod-amd64
  gcp-gardener_prod-amd64-tofu-destroy                                          Run tofu destroy for gcp-gardener_prod-amd64
  gcp-gardener_prod-arm64-tofu-config                                           Create tofu config for gcp-gardener_prod-arm64
  gcp-gardener_prod-arm64-tofu-plan                                             Run tofu plan for gcp-gardener_prod-arm64
  gcp-gardener_prod-arm64-tofu-apply                                            Run tofu apply for gcp-gardener_prod-arm64
  gcp-gardener_prod-arm64-tofu-show                                             Run tofu show for gcp-gardener_prod-arm64
  gcp-gardener_prod-arm64-tofu-login                                            Run tofu login for gcp-gardener_prod-arm64
  gcp-gardener_prod-arm64-tofu-destroy                                          Run tofu destroy for gcp-gardener_prod-arm64
  gcp-gardener_prod_tpm2_trustedboot-amd64-tofu-config                          Create tofu config for gcp-gardener_prod_tpm2_trustedboot-amd64
  gcp-gardener_prod_tpm2_trustedboot-amd64-tofu-plan                            Run tofu plan for gcp-gardener_prod_tpm2_trustedboot-amd64
  gcp-gardener_prod_tpm2_trustedboot-amd64-tofu-apply                           Run tofu apply for gcp-gardener_prod_tpm2_trustedboot-amd64
  gcp-gardener_prod_tpm2_trustedboot-amd64-tofu-show                            Run tofu show for gcp-gardener_prod_tpm2_trustedboot-amd64
  gcp-gardener_prod_tpm2_trustedboot-amd64-tofu-login                           Run tofu login for gcp-gardener_prod_tpm2_trustedboot-amd64
  gcp-gardener_prod_tpm2_trustedboot-amd64-tofu-destroy                         Run tofu destroy for gcp-gardener_prod_tpm2_trustedboot-amd64
  gcp-gardener_prod_tpm2_trustedboot-arm64-tofu-config                          Create tofu config for gcp-gardener_prod_tpm2_trustedboot-arm64
  gcp-gardener_prod_tpm2_trustedboot-arm64-tofu-plan                            Run tofu plan for gcp-gardener_prod_tpm2_trustedboot-arm64
  gcp-gardener_prod_tpm2_trustedboot-arm64-tofu-apply                           Run tofu apply for gcp-gardener_prod_tpm2_trustedboot-arm64
  gcp-gardener_prod_tpm2_trustedboot-arm64-tofu-show                            Run tofu show for gcp-gardener_prod_tpm2_trustedboot-arm64
  gcp-gardener_prod_tpm2_trustedboot-arm64-tofu-login                           Run tofu login for gcp-gardener_prod_tpm2_trustedboot-arm64
  gcp-gardener_prod_tpm2_trustedboot-arm64-tofu-destroy                         Run tofu destroy for gcp-gardener_prod_tpm2_trustedboot-arm64
  gcp-gardener_prod_trustedboot-amd64-tofu-config                               Create tofu config for gcp-gardener_prod_trustedboot-amd64
  gcp-gardener_prod_trustedboot-amd64-tofu-plan                                 Run tofu plan for gcp-gardener_prod_trustedboot-amd64
  gcp-gardener_prod_trustedboot-amd64-tofu-apply                                Run tofu apply for gcp-gardener_prod_trustedboot-amd64
  gcp-gardener_prod_trustedboot-amd64-tofu-show                                 Run tofu show for gcp-gardener_prod_trustedboot-amd64
  gcp-gardener_prod_trustedboot-amd64-tofu-login                                Run tofu login for gcp-gardener_prod_trustedboot-amd64
  gcp-gardener_prod_trustedboot-amd64-tofu-destroy                              Run tofu destroy for gcp-gardener_prod_trustedboot-amd64
  gcp-gardener_prod_trustedboot-arm64-tofu-config                               Create tofu config for gcp-gardener_prod_trustedboot-arm64
  gcp-gardener_prod_trustedboot-arm64-tofu-plan                                 Run tofu plan for gcp-gardener_prod_trustedboot-arm64
  gcp-gardener_prod_trustedboot-arm64-tofu-apply                                Run tofu apply for gcp-gardener_prod_trustedboot-arm64
  gcp-gardener_prod_trustedboot-arm64-tofu-show                                 Run tofu show for gcp-gardener_prod_trustedboot-arm64
  gcp-gardener_prod_trustedboot-arm64-tofu-login                                Run tofu login for gcp-gardener_prod_trustedboot-arm64
  gcp-gardener_prod_trustedboot-arm64-tofu-destroy                              Run tofu destroy for gcp-gardener_prod_trustedboot-arm64
```
</details>

#### Typical Workflow

1. Generate OpenTofu Input Variables for your flavor:
```bash
make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-config
```

2. Preview the changes:
```bash
make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-plan
```

3. Create the resources:
```bash
make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-apply
```

4. Run your tests or log in:
```bash
make --directory=tests gcp-gardener_prod-amd64-tofu-test-platform
```

or

```bash
make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-login
```

5. Clean up when done:
```bash
make --directory=tests/platformSetup gcp-gardener_prod-amd64-tofu-destroy
```

> [!TIP]
> The `plan` command is safe to run anytime - it only shows what would happen without making any changes.

> [!WARNING]
> Ensure an Input Variables file exists with a matching name, e.g., `tests/platformSetup/tofu/variables.gcp-gardener_prod_trustedboot_tpm2-amd64.tfvars`.

Targets follow the typical [OpenTofu plan/apply/destroy](https://opentofu.org/docs/cli/run/) flow, extended with `show` to display resources and `login` to log in via SSH.

### Workspaces and State Management

#### Understanding State

OpenTofu keeps track of all resources it creates in what's called a "state". This state includes:

- What resources exist
- Their current settings
- Dependencies between resources
- And other metadata

Think of state as OpenTofu's record of what it has built in the cloud. Without this record, OpenTofu wouldn't know what resources it manages or how to modify them.

#### Using Workspaces

[OpenTofu Workspaces](https://opentofu.org/docs/cli/workspaces/) allow you to maintain multiple states for the same configuration. In our case, we use workspaces to:

- Test different Garden Linux flavors simultaneously
- Keep track of resources for each flavor separately
- Allow parallel testing without resource naming conflicts
- Allow safe and consistent cleanup of resources

For example, you might have:

- One workspace testing AMD64 on GCP
- Another workspace testing ARM64 on AWS
- A third workspace testing the `tpm` and `trustedboot` features on Azure

Each workspace maintains its own state, so the resources don't interfere with each other.

#### How We Use Workspaces

Our make targets automatically create and manage workspaces. Each workspace name combines:

1. The flavor being tested (e.g., `gcp-gardener_prod-amd64`)
2. A random seed from `tests/platformSetup/.uuid` which is generated by the `Makefile`

This combination ensures unique resource names when multiple tests run in parallel.

To work with workspaces manually:
```bash
# List all workspaces
tofu workspace list
  default
* gcp-gardener_prod-amd64-2e22801c
  aws-gardener_prod-arm64-2e22801c

# Switch to a specific workspace
tofu workspace select gcp-gardener_prod-amd64-2e22801c

# See what resources exist in current workspace
tofu show
```

> [!TIP]
> The asterisk (*) in the workspace list shows your current active workspace.

#### State Storage

By default, OpenTofu stores state locally in your project directory. This works well for individual development but has limitations:

- State files might contain sensitive data
- Local files can be lost or corrupted
- Team members can't share state easily

For these reasons, we use different state storage methods:

1. **Local Development** (default):
   - State stored in `.terraform/terraform.tfstate`
   - Simple to use and good for testing
   - Can be encrypted (see Advanced Settings)

2. **GitHub Actions**:
   - Uses Amazon S3 for reliable remote storage
   - Encrypted state for security
   - Allows state recovery if tests fail
   - Enables parallel testing across multiple runners

> [!NOTE]
> See the Advanced Settings section for details on setting up encrypted or remote state storage.

### Run Platform Tests

Once the cloud resources are created with OpenTofu, we use pytest to run automated tests on the instances. The `tests/Makefile` handles this process by:

1. Using the instance created by OpenTofu to run the tests
2. Establishing SSH connections to the instances
3. Running the Garden Linux pytest test suite

#### Available Test Commands

```bash
make --directory=tests help
```

Each flavor has a test target that:

- Connects to the instance using `tests/helper/sshclient.py`
- Runs the test suite via pytest by calling `tests/platformSetup/manual.py`
- Reports test results

For example:
```bash
# Run tests for a single flavor
make --directory=tests gcp-gardener_prod-amd64-tofu-test-platform

# Run all platform tests
make --directory=tests all
```

#### Full Test Command List

<details>
<summary>Click to see all available test commands</summary>

```plaintext
make --directory=tests

Usage: make [target]

general targets:
help					List available tasks of the project                                     
all					Run all platform tests                                                   

Available Platform Test targets for Official Flavors:

Qemu Provisioner Platform Tests targets:
  ali-gardener_prod-amd64-qemu-test-platform                                    Run platform tests build with Qemu for ali-gardener_prod-amd64
  aws-gardener_prod-amd64-qemu-test-platform                                    Run platform tests build with Qemu for aws-gardener_prod-amd64
  aws-gardener_prod-arm64-qemu-test-platform                                    Run platform tests build with Qemu for aws-gardener_prod-arm64
  aws-gardener_prod_tpm2_trustedboot-amd64-qemu-test-platform                   Run platform tests build with Qemu for aws-gardener_prod_tpm2_trustedboot-amd64
  aws-gardener_prod_tpm2_trustedboot-arm64-qemu-test-platform                   Run platform tests build with Qemu for aws-gardener_prod_tpm2_trustedboot-arm64
  aws-gardener_prod_trustedboot-amd64-qemu-test-platform                        Run platform tests build with Qemu for aws-gardener_prod_trustedboot-amd64
  aws-gardener_prod_trustedboot-arm64-qemu-test-platform                        Run platform tests build with Qemu for aws-gardener_prod_trustedboot-arm64
  azure-gardener_prod-amd64-qemu-test-platform                                  Run platform tests build with Qemu for azure-gardener_prod-amd64
  azure-gardener_prod-arm64-qemu-test-platform                                  Run platform tests build with Qemu for azure-gardener_prod-arm64
  azure-gardener_prod_tpm2_trustedboot-amd64-qemu-test-platform                 Run platform tests build with Qemu for azure-gardener_prod_tpm2_trustedboot-amd64
  azure-gardener_prod_trustedboot-amd64-qemu-test-platform                      Run platform tests build with Qemu for azure-gardener_prod_trustedboot-amd64
  gcp-gardener_prod-amd64-qemu-test-platform                                    Run platform tests build with Qemu for gcp-gardener_prod-amd64
  gcp-gardener_prod-arm64-qemu-test-platform                                    Run platform tests build with Qemu for gcp-gardener_prod-arm64
  gcp-gardener_prod_tpm2_trustedboot-amd64-qemu-test-platform                   Run platform tests build with Qemu for gcp-gardener_prod_tpm2_trustedboot-amd64
  gcp-gardener_prod_tpm2_trustedboot-arm64-qemu-test-platform                   Run platform tests build with Qemu for gcp-gardener_prod_tpm2_trustedboot-arm64
  gcp-gardener_prod_trustedboot-amd64-qemu-test-platform                        Run platform tests build with Qemu for gcp-gardener_prod_trustedboot-amd64
  gcp-gardener_prod_trustedboot-arm64-qemu-test-platform                        Run platform tests build with Qemu for gcp-gardener_prod_trustedboot-arm64
  kvm-gardener_prod-amd64-qemu-test-platform                                    Run platform tests build with Qemu for kvm-gardener_prod-amd64
  kvm-gardener_prod-arm64-qemu-test-platform                                    Run platform tests build with Qemu for kvm-gardener_prod-arm64
  kvm-gardener_prod_tpm2_trustedboot-amd64-qemu-test-platform                   Run platform tests build with Qemu for kvm-gardener_prod_tpm2_trustedboot-amd64
  kvm-gardener_prod_tpm2_trustedboot-arm64-qemu-test-platform                   Run platform tests build with Qemu for kvm-gardener_prod_tpm2_trustedboot-arm64
  kvm-gardener_prod_trustedboot-amd64-qemu-test-platform                        Run platform tests build with Qemu for kvm-gardener_prod_trustedboot-amd64
  kvm-gardener_prod_trustedboot-arm64-qemu-test-platform                        Run platform tests build with Qemu for kvm-gardener_prod_trustedboot-arm64

Tofu Provisioner Platform Tests targets:
  ali-gardener_prod-amd64-tofu-test-platform                                    Run platform tests build with OpenTofu for ali-gardener_prod-amd64
  aws-gardener_prod-amd64-tofu-test-platform                                    Run platform tests build with OpenTofu for aws-gardener_prod-amd64
  aws-gardener_prod-arm64-tofu-test-platform                                    Run platform tests build with OpenTofu for aws-gardener_prod-arm64
  aws-gardener_prod_tpm2_trustedboot-amd64-tofu-test-platform                   Run platform tests build with OpenTofu for aws-gardener_prod_tpm2_trustedboot-amd64
  aws-gardener_prod_tpm2_trustedboot-arm64-tofu-test-platform                   Run platform tests build with OpenTofu for aws-gardener_prod_tpm2_trustedboot-arm64
  aws-gardener_prod_trustedboot-amd64-tofu-test-platform                        Run platform tests build with OpenTofu for aws-gardener_prod_trustedboot-amd64
  aws-gardener_prod_trustedboot-arm64-tofu-test-platform                        Run platform tests build with OpenTofu for aws-gardener_prod_trustedboot-arm64
  azure-gardener_prod-amd64-tofu-test-platform                                  Run platform tests build with OpenTofu for azure-gardener_prod-amd64
  azure-gardener_prod-arm64-tofu-test-platform                                  Run platform tests build with OpenTofu for azure-gardener_prod-arm64
  azure-gardener_prod_tpm2_trustedboot-amd64-tofu-test-platform                 Run platform tests build with OpenTofu for azure-gardener_prod_tpm2_trustedboot-amd64
  azure-gardener_prod_trustedboot-amd64-tofu-test-platform                      Run platform tests build with OpenTofu for azure-gardener_prod_trustedboot-amd64
  gcp-gardener_prod-amd64-tofu-test-platform                                    Run platform tests build with OpenTofu for gcp-gardener_prod-amd64
  gcp-gardener_prod-arm64-tofu-test-platform                                    Run platform tests build with OpenTofu for gcp-gardener_prod-arm64
  gcp-gardener_prod_tpm2_trustedboot-amd64-tofu-test-platform                   Run platform tests build with OpenTofu for gcp-gardener_prod_tpm2_trustedboot-amd64
  gcp-gardener_prod_tpm2_trustedboot-arm64-tofu-test-platform                   Run platform tests build with OpenTofu for gcp-gardener_prod_tpm2_trustedboot-arm64
  gcp-gardener_prod_trustedboot-amd64-tofu-test-platform                        Run platform tests build with OpenTofu for gcp-gardener_prod_trustedboot-amd64
  gcp-gardener_prod_trustedboot-arm64-tofu-test-platform                        Run platform tests build with OpenTofu for gcp-gardener_prod_trustedboot-arm64
```
</details>

#### Debugging Failed Tests

If tests fail, you can:

1. Check the pytest output for error messages
2. Look at the OpenTofu state: `make --directory=tests/platformSetup <flavor>-tofu-show`
3. SSH into the instance manually: `make --directory=tests/platformSetup <flavor>-tofu-login`
4. Check cloud provider logs in their respective web consoles

> [!WARNING]
> Remember to clean up resources after debugging:
> ```bash
> make --directory=tests/platformSetup <flavor>-tofu-destroy
> ```

## Advanced Settings

### Enhanced State Management

As discussed in the [State Management section](#understanding-state), OpenTofu uses state files to track resources. While local state works for development, there are more robust options for team environments or our Github Actions.

#### Using Encrypted Local State

For better security when using local state, you can enable encryption:

Configure encryption and initialize:

```bash
# Set up encryption configuration
$ export TF_ENCRYPTION='''{..}'''

# Initialize OpenTofu with encryption
$ tofu init
```

<details>
<summary>Click to see complete command</summary>

```bash
# Set up encryption configuration
$ export TF_ENCRYPTION='''{
  "key_provider": {
    "pbkdf2": {
      "passphrase": {
        "passphrase": "your-secure-passphrase"
      } 
    }
  },
  "method": {
    "aes_gcm": {
      "method": {
         "keys": "${key_provider.pbkdf2.passphrase}"
      }
    }
  },
  "state": {
    "method": "${method.aes_gcm.method}",
    "enforced": true
  },
  "plan": {
    "method": "${method.aes_gcm.method}",
    "enforced": true
  }
}'''

# Initialize OpenTofu with encryption
$ tofu init
```

</details>

#### Setting Up Remote State in S3

For team environments (like our GitHub Actions), we use Amazon S3 with encryption. Here's how to set it up:

1. Configure encryption and initialize:

```bash
# Set up encryption configuration
$ export TF_ENCRYPTION='''{..}'''

# Initialize OpenTofu with encryption
$ tofu init
```

<details>
<summary>Click to see complete command</summary>

```bash
# Set up encryption configuration
$ export TF_ENCRYPTION='''{
  "key_provider": {
    "pbkdf2": {
      "passphrase": {
        "passphrase": "your-secure-passphrase"
      } 
    }
  },
  "method": {
    "aes_gcm": {
      "method": {
         "keys": "${key_provider.pbkdf2.passphrase}"
      }
    }
  },
  "state": {
    "method": "${method.aes_gcm.method}",
    "enforced": true
  },
  "plan": {
    "method": "${method.aes_gcm.method}",
    "enforced": true
  }
}'''
```

</details>

2. Create S3 resources:
```bash
# Create a workspace for state management
$ tofu workspace select -or-create tfstate

# Create the S3 bucket and related resources
$ tofu apply -var deploy_state_aws=true

# Get the bucket name
$ tofu output -raw state_aws_bucket_name
```

3. Switch to S3 backend:
```bash
# Copy the GitHub Actions backend configuration
$ cp backend.tf.github backend.tf

# Edit backend.tf to use your bucket and region
$ vim backend.tf

# Migrate your state to S3
$ tofu init -migrate-state
```

4. Return to default workspace:
```bash
$ tofu workspace select default
```

> [!NOTE]
> The S3 backend provides:
>
> - Encrypted state storage using [AES-GCM](https://opentofu.org/docs/language/state/encryption/#aes-gcm)
> - State recovery for failed tests
> - Support for parallel testing
> - Team collaboration capabilities
>
> For more details on state encryption and backends, see:
>
> - [State and Plan Encryption](https://opentofu.org/docs/language/state/encryption/)
> - [S3 Backend Configuration](https://opentofu.org/docs/language/settings/backends/s3/)

#### Recover GitHub Action's OpenTofu State Locally

Sometimes you might need to access or recover the state from our GitHub Actions pipeline, for example:

- To debug failed tests
- To clean up stuck resources
- To investigate test environments

Here's how to access the remote state:

1. Configure encryption and initialize:

```bash
# Set up encryption configuration
$ export TF_ENCRYPTION='''{..}'''

# Initialize OpenTofu with encryption
$ tofu init
```

<details>
<summary>Click to see complete command</summary>

1. Set up encryption (using the same configuration as GitHub Actions):
```bash
export TF_ENCRYPTION='''{
  "key_provider": {
    "pbkdf2": {
      "passphrase": {
        "passphrase": "our-secure-passphrase"
      } 
    }
  },
  "method": {
    "aes_gcm": {
      "method": {
         "keys": "${key_provider.pbkdf2.passphrase}"
      }
    }
  },
  "state": {
    "method": "${method.aes_gcm.method}",
    "enforced": true
  },
  "plan": {
    "method": "${method.aes_gcm.method}",
    "enforced": true
  }
}'''
```

</details>

2. Configure S3 backend access:

```bash
# Copy the GitHub Actions backend configuration
$ cp backend.tf.github backend.tf

# Initialize OpenTofu with the S3 backend
$ tofu init
```

3. Access the remote state:

```bash
# List all available workspaces
$ tofu workspace list

# Switch to a specific workspace (example)
$ tofu workspace select gcp-gardener_prod-amd64-5040a670

# View the state
$ tofu show
```

##### Cleaning Up Remote Resources

> [!WARNING]
> The cleanup command will destroy ALL resources in ALL workspaces. Use with caution!

If you need to clean up resources from failed tests:

```bash
# Clean up a single workspace
$ tofu workspace select my-workspace
$ tofu destroy
$ tofu workspace select default
$ tofu workspace delete my-workspace

# Clean up all workspaces (USE WITH CAUTION!)
$ for i in $(tofu workspace list | grep 'ali|aws|azure|gcp' | sed 's#*##g'); do
    echo "Cleaning up workspace: $i"
    tofu workspace select $i && \
    tofu destroy -auto-approve && \
    tofu workspace select default && \
    tofu workspace delete $i
  done
```

## Updating OpenTofu or Provider Versions

To upgrade to a newer OpenTofu version or update a provider, follow these steps carefully.

1. **If the provider is forked:**

   * Update the version in
     `tests/images/platform-test/tofu/Containerfile`
   * Check and adjust settings in
     `tests/images/platform-test/tofu/.terraformrc`

2. **Update version constraints:**

   * Edit `tests/platformSetup/tofu/providers.tf` to pin the new OpenTofu and provider versions
     * Look at [OpenTofu - Providers - Version Constraints](https://opentofu.org/docs/language/providers/requirements/#version-constraints) for the correct syntax.

3. **Upgrade the lockfile:**

   ```bash
   $ cd tests/platformSetup/tofu/
   $ tofu init [-upgrade]
   ```

   This will update `tests/platformSetup/tofu/.terraform.lock.hcl`

### Local Testing

You can test your changes locally by building the image and running the relevant make targets:

```bash
# Build and tag the updated tofu image
$ make --directory=tests/images build-platform-test-tofu
$ podman tag ghcr.io/gardenlinux/gardenlinux/platform-test-tofu:nightly \
            ghcr.io/gardenlinux/gardenlinux/platform-test-tofu:latest

# Run the usual platform setup make targets
$ make --directory=tests/platformSetup azure-gardener_prod-amd64-tofu-config
$ make --directory=tests/platformSetup azure-gardener_prod-amd64-tofu-plan
```

### Final Steps

If your local tests pass:

* Commit your changes
* Open a pull request

Once your PR is merged into `main`, the `ghcr.io/gardenlinux/gardenlinux/platform-test-tofu:latest` image will be **automatically built and pushed**.

## GitHub Actions

Our GitHub Actions workflows use the same make targets as manual testing, providing a consistent interface across local development and CI/CD. This makes debugging and reproducing issues much simpler.

### Available Workflows

We have two main workflows for platform testing:

#### nightly.yml - Automated Nightly Tests

This workflow automatically tests all Garden Linux flavors that have platform testing enabled:

- Runs every night
- Tests all flavors with `test-platform: true` in `flavors.yaml`
- Uses remote state in S3 for reliability
- Runs tests in parallel across multiple runners


#### tests-only.yml - On-Demand Testing

This workflow enables testing specific Garden Linux flavors and versions on demand. It's particularly useful for:

- Testing specific branches during development
- Validating changes before merging
- Testing individual flavors or cloud providers
- Testing old versions of Garden Linux

The workflow supports two main testing paths:

1. Testing existing images from S3:
```bash
# Test specific version and flavor using existing S3 image
gh workflow run "platform tests only" \
  # directly passed to bin/glrd to commit and fetch image from S3
  -f version=1312 \
  # directly passed to bin/parse_flavors.py
  -f flavors_parse_params_test='--no-arch --json-by-arch --test-platform --include-only gcp-gardener_prod-amd64'
```

2. Building and testing new images:
```bash
# Build and test from current branch
gh workflow run "platform tests only" \
  # build images from current commit
  -f build=true \
  # build from specific branch
  --ref feat/my-feature \

# Build and test specific cloud provider
gh workflow run "platform tests only" \
  # build images from current commit
  -f build=true \
  # build from specific branch
  --ref feat/my-feature \
  # run tests for all GCP flavors and architectures
  -f flavors_parse_params_test='--no-arch --json-by-arch --test-platform --include-only "gcp-*"'
```

Common workflow parameters:

| Parameter | Description | Example Value |
|-----------|-------------|---------------|
| `--ref` | Git reference to test (branch/tag/SHA) | `feat/my-feature`, `main`, `abc123de` |
| `-f build` | Whether to build images from source | `true`, `false` |
| `-f flavors_parse_params_test` | Filter which flavors to test | `--no-arch --json-by-arch --test-platform --include-only "gcp-*"` |
| `-f version` | Version to test | `1312`, `latest` |

> [!NOTE]
> The `version` input is passed directly to `bin/glrd` to fetch image from S3. It supports every version string that `bin/glrd` supports.

> [!NOTE]
> The `flavors_parse_params_test` input is passed directly to `bin/parse_flavors.py` for flavor selection. It supports every parameter that `bin/parse_flavors.py` supports.

> [!TIP]
> To monitor the workflow:
> ```bash
> # View workflow status
> gh run list --workflow="platform tests only"
> 
> # Watch specific run
> gh run watch
> ```

## Appendix

### OpenTofu in a Nutshell

#### OpenTofu Configuration Language (HCL)

OpenTofu uses HashiCorp Configuration Language (HCL) to define infrastructure. Here's how it works:

##### Basic HCL Syntax

Resources are defined using blocks:

```hcl
# Define a Google Cloud VM instance
resource "google_compute_instance" "test_instance" {
  name         = "test-instance"
  machine_type = "n1-standard-2"
  zone         = "europe-west3-a"

  boot_disk {
    initialize_params {
      image = "garden-linux-image"
    }
  }

  network_interface {
    network = "default"
  }
}
```

Official documentation: [Resources](https://opentofu.org/docs/language/resources/syntax)

##### Providers

Providers are plugins that allow OpenTofu to interact with cloud platforms and other services:

```hcl
# Configure the AWS Provider
provider "aws" {
  region = "eu-central-1"
}

# Configure the Google Cloud Provider
provider "google" {
  project = "my-project"
  region  = "europe-west3"
}

# Configure multiple provider instances
provider "aws" {
  alias  = "us_east"
  region = "us-east-1"
}

provider "aws" {
  alias  = "eu_west"
  region = "eu-west-1"
}
```

Official documentation: [Providers](https://opentofu.org/docs/language/providers)

##### Resource Types

Each cloud provider has its own resource types:

```hcl
# AWS EC2 Instance
resource "aws_instance" "test_instance" {
  ami           = "ami-12345678"
  instance_type = "t2.micro"
}

# Azure Virtual Machine
resource "azurerm_virtual_machine" "test_instance" {
  name                  = "test-instance"
  location              = "westeurope"
  resource_group_name   = "test-group"
  vm_size               = "Standard_DS1_v2"
}

# Alibaba Cloud ECS Instance
resource "alicloud_instance" "test_instance" {
  instance_name = "test-instance"
  instance_type = "ecs.t5-lc1m1.small"
}
```

Official documentation: [Resource Types](https://opentofu.org/docs/language/resources/syntax#resource-types)

##### Input and Output Values

Input Variables and Output Values make configurations reusable:

```hcl
# Define input variables
variable "instance_type" {
  description = "The type of instance to create"
  type        = string
  default     = "t2.micro"
}

# Use variables in resources
resource "aws_instance" "test_instance" {
  instance_type = var.instance_type
}

# Define outputs
output "instance_ip" {
  description = "The public IP of the instance"
  value       = aws_instance.test_instance.public_ip
}
```

Official documentation: [Input Variables](https://opentofu.org/docs/language/values/variables/) and [Output Values](https://opentofu.org/docs/language/values/outputs/)

##### Data Sources

Data sources let you query existing resources:

```hcl
# Look up an existing VPC
data "aws_vpc" "default" {
  default = true
}

# Use the VPC ID in a resource
resource "aws_instance" "test_instance" {
  subnet_id = data.aws_vpc.default.id
}
```

Official documentation: [Data Sources](https://opentofu.org/docs/language/data-sources)

##### File Extensions and Organization

OpenTofu files use specific extensions and naming conventions:

- `.tf` - Main OpenTofu configuration files
- `.tfvars` - Variable definition files
- `.tfstate` - State files (generated)
- `.tfplan` - Plan files (generated)
- `.hcl` - HashiCorp Configuration Language files (like `.terraform.lock.hcl`)

Official documentation: [Files and Directories](https://opentofu.org/docs/language/files)

##### OpenTofu Commands

OpenTofu has several core commands for managing infrastructure:

###### `tofu plan`

Shows what changes will be made:

```bash
$ tofu plan
Terraform will perform the following actions:

  # google_compute_instance.test_instance will be created
  + resource "google_compute_instance" "test_instance" {
      + name         = "test-vm"
      + machine_type = "n1-standard-2"
      ...
    }

Plan: 1 to add, 0 to change, 0 to destroy.
```

###### `tofu apply`

Creates or updates resources:

```bash
$ tofu apply
google_compute_instance.test_instance: Creating...
google_compute_instance.test_instance: Creation complete after 45s

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

Outputs:
instance_ip = "35.198.142.123"
```

###### `tofu show`

Displays the current state:

```bash
$ tofu show
# google_compute_instance.test_instance:
resource "google_compute_instance" "test_instance" {
    id           = "projects/my-project/zones/europe-west3-a/instances/test-vm"
    name         = "test-vm"
    machine_type = "n1-standard-2"
    ...
}
```

###### `tofu destroy`

Removes all resources:

```bash
$ tofu destroy
google_compute_instance.test_instance: Destroying...
google_compute_instance.test_instance: Destruction complete after 32s

Destroy complete! Resources: 1 destroyed.
```

Official documentation: [Command Line Interface](https://opentofu.org/docs/cli/run)
