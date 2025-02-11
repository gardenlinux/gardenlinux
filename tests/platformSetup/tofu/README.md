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

#### Python virtual environment

A virtual environment with minimum dependencies is required to run the make targets and the coresponding python scripts.

```bash
$ python -m venv venv
$ pip install -r requirements.txt
```

### Understanding the Test Process

#### Quick Start - Typical Workflow

Here's the minimal sequence of commands to run a complete platform test.

Please be aware that you have to configure cloud provider authentication and settings before running the tests. Have a look at the [Cloud Provider Authentication](#cloud-provider-authentication) section for more information.

```bash
# 0. Build the image for the flavor you want to test
$ make gcp-gardener_prod-amd64-build

# 1. Generate variables for your flavor
$ make --directory=tests/platformSetup gcp-gardener_prod-amd64-config

# 2. Create cloud resources
$ make --directory=tests/platformSetup gcp-gardener_prod-amd64-apply

# 3. Run the tests
$ make --directory=tests gcp-gardener_prod-amd64-test-platform

# 4. Clean up when done
$ make --directory=tests/platformSetup gcp-gardener_prod-amd64-destroy
  ```

> [!TIP]
> You can preview changes before applying them with the `plan` command:
> ```bash
> make --directory=tests/platformSetup gcp-gardener_prod-amd64-plan
> ```

#### What Happens Behind the Scenes

When you run a platform test, this sequence occurs:

1. **Generate Input Variables** (make target calls `tests/platformSetup/tofu/tf_variables_create.py`):
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

2b. **Test Configuration** (make target calls `tests/platformSetup/tofu/tf_pytest_ssh.py`):
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
> If you don't a Google Cloud project, you can supply any mocked up value.

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
> If you don't have a subscription, you have to comment out the module "azure" in `tests/platformSetup/tofu/main.tf` and `tests/platformSetup/tofu/outputs.tf`.

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

We provide a helper script `tf_variables_create.py` to generate these files automatically.
It is called by the "-config" make targets but can also be called manually.

```bash
# use default settings
make --directory=tests/platformSetup gcp-gardener_prod-amd64-config

# write a custom test prefix and image via cname
TEST_PREFIX=myprefix \
  CNAME=gcp-gardener_prod_tpm2_trustedboot-amd64-1695.0-30903f3a \
  make --directory=tests/platformSetup \
  gcp-gardener_prod_tpm2_trustedboot-amd64-config
```

or


```bash
# Generate for a single flavor
./tests/platformSetup/tofu/tf_variables_create.py \
    --flavors gcp-gardener_prod_trustedboot_tpm2-amd64 \
    myprefix

# Generate for a specific image version
./tests/platformSetup/tofu/tf_variables_create.py \
    --flavors gcp-gardener_prod_trustedboot_tpm2-amd64 \
    --cname gcp-gardener_prod_tpm2_trustedboot-amd64-1695.0-30903f3a \
    myprefix

# Generate for multiple flavors (default set)
./tests/platformSetup/tofu/tf_variables_create.py myprefix
```

The script supports these options:

<details>
<summary>Click to see all available options</summary>

```bash
./tests/platformSetup/tofu/tf_variables_create.py --help
usage: tf_variables_create.py [-h] [--flavors FLAVORS] [--root-dir ROOT_DIR] [--image-path IMAGE_PATH] [--cname CNAME] test_prefix

Generate OpenTofu variable files based on provided test prefix, platforms, archs, and flavors.

positional arguments:
  test_prefix           The test prefix to include in the variable files.

options:
  -h, --help            show this help message and exit
  --flavors FLAVORS     Comma-separated list of flavors (default: 'ali-gardener_prod-amd64,aws-gardener_prod-amd64,azure-gardener_prod-amd64,gcp-gardener_prod-amd64').
  --root-dir ROOT_DIR   Root directory for the variable files. Defaults to the current Git repository's root.
  --image-path IMAGE_PATH
                        Base path for image files.
  --cname CNAME         Basename of image file, e.g. 'gcp-gardener_prod-arm64-1592.2-76203a30'.
```

</details>

> [!WARNING]
> Before running tests, ensure the variables file exists with the correct name, matching your test flavor (e.g., `variables.gcp-gardener_prod_trustedboot_tpm2-amd64.tfvars`)

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
make --directory=tests/platformSetup gcp-gardener_prod-amd64-plan

# Create resources
make --directory=tests/platformSetup gcp-gardener_prod-amd64-apply

# Show current state
make --directory=tests/platformSetup gcp-gardener_prod-amd64-show

# SSH into instance
make --directory=tests/platformSetup gcp-gardener_prod-amd64-login

# Clean up resources
make --directory=tests/platformSetup gcp-gardener_prod-amd64-destroy
```

#### Full Command List

<details>
<summary>Click to see all available commands</summary>

```plaintext
Usage: make [target]

general targets:
help					List available tasks of the project 

Available targets for Official Flavors:

ali-gardener_prod-amd64-plan        Run tofu plan for ali-gardener_prod-amd64
ali-gardener_prod-amd64-apply       Run tofu apply for ali-gardener_prod-amd64
ali-gardener_prod-amd64-show        Run tofu show for ali-gardener_prod-amd64
ali-gardener_prod-amd64-login       Run tofu login for ali-gardener_prod-amd64
ali-gardener_prod-amd64-destroy     Run tofu destroy for ali-gardener_prod-amd64
aws-gardener_prod-amd64-plan        Run tofu plan for aws-gardener_prod-amd64
aws-gardener_prod-amd64-apply       Run tofu apply for aws-gardener_prod-amd64
aws-gardener_prod-amd64-show        Run tofu show for aws-gardener_prod-amd64
aws-gardener_prod-amd64-login       Run tofu login for aws-gardener_prod-amd64
aws-gardener_prod-amd64-destroy     Run tofu destroy for aws-gardener_prod-amd64
aws-gardener_prod-arm64-plan        Run tofu plan for aws-gardener_prod-arm64
aws-gardener_prod-arm64-apply       Run tofu apply for aws-gardener_prod-arm64
aws-gardener_prod-arm64-show        Run tofu show for aws-gardener_prod-arm64
aws-gardener_prod-arm64-login       Run tofu login for aws-gardener_prod-arm64
aws-gardener_prod-arm64-destroy     Run tofu destroy for aws-gardener_prod-arm64
aws-gardener_prod_trustedboot-amd64-plan        Run tofu plan for aws-gardener_prod_trustedboot-amd64
aws-gardener_prod_trustedboot-amd64-apply       Run tofu apply for aws-gardener_prod_trustedboot-amd64
aws-gardener_prod_trustedboot-amd64-show        Run tofu show for aws-gardener_prod_trustedboot-amd64
aws-gardener_prod_trustedboot-amd64-login       Run tofu login for aws-gardener_prod_trustedboot-amd64
aws-gardener_prod_trustedboot-amd64-destroy     Run tofu destroy for aws-gardener_prod_trustedboot-amd64
aws-gardener_prod_trustedboot-arm64-plan        Run tofu plan for aws-gardener_prod_trustedboot-arm64
aws-gardener_prod_trustedboot-arm64-apply       Run tofu apply for aws-gardener_prod_trustedboot-arm64
aws-gardener_prod_trustedboot-arm64-show        Run tofu show for aws-gardener_prod_trustedboot-arm64
aws-gardener_prod_trustedboot-arm64-login       Run tofu login for aws-gardener_prod_trustedboot-arm64
aws-gardener_prod_trustedboot-arm64-destroy     Run tofu destroy for aws-gardener_prod_trustedboot-arm64
aws-gardener_prod_trustedboot_tpm2-amd64-plan        Run tofu plan for aws-gardener_prod_trustedboot_tpm2-amd64
aws-gardener_prod_trustedboot_tpm2-amd64-apply       Run tofu apply for aws-gardener_prod_trustedboot_tpm2-amd64
aws-gardener_prod_trustedboot_tpm2-amd64-show        Run tofu show for aws-gardener_prod_trustedboot_tpm2-amd64
aws-gardener_prod_trustedboot_tpm2-amd64-login       Run tofu login for aws-gardener_prod_trustedboot_tpm2-amd64
aws-gardener_prod_trustedboot_tpm2-amd64-destroy     Run tofu destroy for aws-gardener_prod_trustedboot_tpm2-amd64
aws-gardener_prod_trustedboot_tpm2-arm64-plan        Run tofu plan for aws-gardener_prod_trustedboot_tpm2-arm64
aws-gardener_prod_trustedboot_tpm2-arm64-apply       Run tofu apply for aws-gardener_prod_trustedboot_tpm2-arm64
aws-gardener_prod_trustedboot_tpm2-arm64-show        Run tofu show for aws-gardener_prod_trustedboot_tpm2-arm64
aws-gardener_prod_trustedboot_tpm2-arm64-login       Run tofu login for aws-gardener_prod_trustedboot_tpm2-arm64
aws-gardener_prod_trustedboot_tpm2-arm64-destroy     Run tofu destroy for aws-gardener_prod_trustedboot_tpm2-arm64
azure-gardener_prod-amd64-plan        Run tofu plan for azure-gardener_prod-amd64
azure-gardener_prod-amd64-apply       Run tofu apply for azure-gardener_prod-amd64
azure-gardener_prod-amd64-show        Run tofu show for azure-gardener_prod-amd64
azure-gardener_prod-amd64-login       Run tofu login for azure-gardener_prod-amd64
azure-gardener_prod-amd64-destroy     Run tofu destroy for azure-gardener_prod-amd64
azure-gardener_prod_trustedboot-amd64-plan        Run tofu plan for azure-gardener_prod_trustedboot-amd64
azure-gardener_prod_trustedboot-amd64-apply       Run tofu apply for azure-gardener_prod_trustedboot-amd64
azure-gardener_prod_trustedboot-amd64-show        Run tofu show for azure-gardener_prod_trustedboot-amd64
azure-gardener_prod_trustedboot-amd64-login       Run tofu login for azure-gardener_prod_trustedboot-amd64
azure-gardener_prod_trustedboot-amd64-destroy     Run tofu destroy for azure-gardener_prod_trustedboot-amd64
azure-gardener_prod_trustedboot_tpm2-amd64-plan        Run tofu plan for azure-gardener_prod_trustedboot_tpm2-amd64
azure-gardener_prod_trustedboot_tpm2-amd64-apply       Run tofu apply for azure-gardener_prod_trustedboot_tpm2-amd64
azure-gardener_prod_trustedboot_tpm2-amd64-show        Run tofu show for azure-gardener_prod_trustedboot_tpm2-amd64
azure-gardener_prod_trustedboot_tpm2-amd64-login       Run tofu login for azure-gardener_prod_trustedboot_tpm2-amd64
azure-gardener_prod_trustedboot_tpm2-amd64-destroy     Run tofu destroy for azure-gardener_prod_trustedboot_tpm2-amd64
gcp-gardener_prod-amd64-plan        Run tofu plan for gcp-gardener_prod-amd64
gcp-gardener_prod-amd64-apply       Run tofu apply for gcp-gardener_prod-amd64
gcp-gardener_prod-amd64-show        Run tofu show for gcp-gardener_prod-amd64
gcp-gardener_prod-amd64-login       Run tofu login for gcp-gardener_prod-amd64
gcp-gardener_prod-amd64-destroy     Run tofu destroy for gcp-gardener_prod-amd64
gcp-gardener_prod-arm64-plan        Run tofu plan for gcp-gardener_prod-arm64
gcp-gardener_prod-arm64-apply       Run tofu apply for gcp-gardener_prod-arm64
gcp-gardener_prod-arm64-show        Run tofu show for gcp-gardener_prod-arm64
gcp-gardener_prod-arm64-login       Run tofu login for gcp-gardener_prod-arm64
gcp-gardener_prod-arm64-destroy     Run tofu destroy for gcp-gardener_prod-arm64
gcp-gardener_prod_trustedboot-amd64-plan        Run tofu plan for gcp-gardener_prod_trustedboot-amd64
gcp-gardener_prod_trustedboot-amd64-apply       Run tofu apply for gcp-gardener_prod_trustedboot-amd64
gcp-gardener_prod_trustedboot-amd64-show        Run tofu show for gcp-gardener_prod_trustedboot-amd64
gcp-gardener_prod_trustedboot-amd64-login       Run tofu login for gcp-gardener_prod_trustedboot-amd64
gcp-gardener_prod_trustedboot-amd64-destroy     Run tofu destroy for gcp-gardener_prod_trustedboot-amd64
gcp-gardener_prod_trustedboot-arm64-plan        Run tofu plan for gcp-gardener_prod_trustedboot-arm64
gcp-gardener_prod_trustedboot-arm64-apply       Run tofu apply for gcp-gardener_prod_trustedboot-arm64
gcp-gardener_prod_trustedboot-arm64-show        Run tofu show for gcp-gardener_prod_trustedboot-arm64
gcp-gardener_prod_trustedboot-arm64-login       Run tofu login for gcp-gardener_prod_trustedboot-arm64
gcp-gardener_prod_trustedboot-arm64-destroy     Run tofu destroy for gcp-gardener_prod_trustedboot-arm64
gcp-gardener_prod_trustedboot_tpm2-amd64-plan        Run tofu plan for gcp-gardener_prod_trustedboot_tpm2-amd64
gcp-gardener_prod_trustedboot_tpm2-amd64-apply       Run tofu apply for gcp-gardener_prod_trustedboot_tpm2-amd64
gcp-gardener_prod_trustedboot_tpm2-amd64-show        Run tofu show for gcp-gardener_prod_trustedboot_tpm2-amd64
gcp-gardener_prod_trustedboot_tpm2-amd64-login       Run tofu login for gcp-gardener_prod_trustedboot_tpm2-amd64
gcp-gardener_prod_trustedboot_tpm2-amd64-destroy     Run tofu destroy for gcp-gardener_prod_trustedboot_tpm2-amd64
gcp-gardener_prod_trustedboot_tpm2-arm64-plan        Run tofu plan for gcp-gardener_prod_trustedboot_tpm2-arm64
gcp-gardener_prod_trustedboot_tpm2-arm64-apply       Run tofu apply for gcp-gardener_prod_trustedboot_tpm2-arm64
gcp-gardener_prod_trustedboot_tpm2-arm64-show        Run tofu show for gcp-gardener_prod_trustedboot_tpm2-arm64
gcp-gardener_prod_trustedboot_tpm2-arm64-login       Run tofu login for gcp-gardener_prod_trustedboot_tpm2-arm64
gcp-gardener_prod_trustedboot_tpm2-arm64-destroy     Run tofu destroy for gcp-gardener_prod_trustedboot_tpm2-arm64
```
</details>

#### Typical Workflow

1. Generate OpenTofu Input Variables for your flavor:
```bash
make --directory=tests/platformSetup gcp-gardener_prod-amd64-config
```

2. Preview the changes:
```bash
make --directory=tests/platformSetup gcp-gardener_prod-amd64-plan
```

3. Create the resources:
```bash
make --directory=tests/platformSetup gcp-gardener_prod-amd64-apply
```

4. Run your tests or log in:
```bash
make --directory=tests gcp-gardener_prod-amd64-test-platform
```

or

```bash
make --directory=tests/platformSetup gcp-gardener_prod-amd64-login
```

5. Clean up when done:
```bash
make --directory=tests/platformSetup gcp-gardener_prod-amd64-destroy
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
make --directory=tests gcp-gardener_prod-amd64-test-platform

# Run all platform tests
make --directory=tests all
```

#### Full Test Command List

<details>
<summary>Click to see all available test commands</summary>

```plaintext
Usage: make [target]

general targets:
help					List available tasks of the project                 
all					Run all platform tests                               

Available targets for Official Flavors:

ali-gardener_prod-amd64-test-platform                       Run platform tests via opentofu for ali-gardener_prod-amd64
aws-gardener_prod-amd64-test-platform                       Run platform tests via opentofu for aws-gardener_prod-amd64
aws-gardener_prod-arm64-test-platform                       Run platform tests via opentofu for aws-gardener_prod-arm64
aws-gardener_prod_trustedboot-amd64-test-platform           Run platform tests via opentofu for aws-gardener_prod_trustedboot-amd64
aws-gardener_prod_trustedboot-arm64-test-platform           Run platform tests via opentofu for aws-gardener_prod_trustedboot-arm64
aws-gardener_prod_trustedboot_tpm2-amd64-test-platform      Run platform tests via opentofu for aws-gardener_prod_trustedboot_tpm2-amd64
aws-gardener_prod_trustedboot_tpm2-arm64-test-platform      Run platform tests via opentofu for aws-gardener_prod_trustedboot_tpm2-arm64
azure-gardener_prod-amd64-test-platform                     Run platform tests via opentofu for azure-gardener_prod-amd64
azure-gardener_prod_trustedboot-amd64-test-platform         Run platform tests via opentofu for azure-gardener_prod_trustedboot-amd64
azure-gardener_prod_trustedboot_tpm2-amd64-test-platform    Run platform tests via opentofu for azure-gardener_prod_trustedboot_tpm2-amd64
gcp-gardener_prod-amd64-test-platform                       Run platform tests via opentofu for gcp-gardener_prod-amd64
gcp-gardener_prod-arm64-test-platform                       Run platform tests via opentofu for gcp-gardener_prod-arm64
gcp-gardener_prod_trustedboot-amd64-test-platform           Run platform tests via opentofu for gcp-gardener_prod_trustedboot-amd64
gcp-gardener_prod_trustedboot-arm64-test-platform           Run platform tests via opentofu for gcp-gardener_prod_trustedboot-arm64
gcp-gardener_prod_trustedboot_tpm2-amd64-test-platform      Run platform tests via opentofu for gcp-gardener_prod_trustedboot_tpm2-amd64
gcp-gardener_prod_trustedboot_tpm2-arm64-test-platform      Run platform tests via opentofu for gcp-gardener_prod_trustedboot_tpm2-arm64
```
</details>

#### Debugging Failed Tests

If tests fail, you can:

1. Check the pytest output for error messages
2. Look at the OpenTofu state: `make --directory=tests/platformSetup <flavor>-show`
3. SSH into the instance manually: `make --directory=tests/platformSetup <flavor>-login`
4. Check cloud provider logs in their respective web consoles

> [!WARNING]
> Remember to clean up resources after debugging:
> ```bash
> make --directory=tests/platformSetup <flavor>-destroy
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
  -f flavors_parse_params='--no-arch --json-by-arch --test-platform --include-only gcp-gardener_prod-amd64'
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
  -f flavors_parse_params='--no-arch --json-by-arch --test-platform --include-only "gcp-*"'
```

Common workflow parameters:

| Parameter | Description | Example Value |
|-----------|-------------|---------------|
| `--ref` | Git reference to test (branch/tag/SHA) | `feat/my-feature`, `main`, `abc123de` |
| `-f build` | Whether to build images from source | `true`, `false` |
| `-f flavors_parse_params` | Filter which flavors to test | `--no-arch --json-by-arch --test-platform --include-only "gcp-*"` |
| `-f version` | Version to test | `1312`, `latest` |

> [!NOTE]
> The `version` input is passed directly to `bin/glrd` to fetch image from S3. It supports every version string that `bin/glrd` supports.

> [!NOTE]
> The `flavors_parse_params` input is passed directly to `bin/parse_flavors.py` for flavor selection. It supports every parameter that `bin/parse_flavors.py` supports.

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
