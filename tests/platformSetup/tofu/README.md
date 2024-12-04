# Platform Tests with OpenTofu

## OpenTofu Module Structure

`tests/platformSetup/tofu` is the [Root Module](https://opentofu.org/docs/language/modules/#the-root-module), which hosts [Child Modules](https://opentofu.org/docs/language/modules/#child-modules) for each cloud provider:

- `tests/platformSetup/tofu/ali`
- `tests/platformSetup/tofu/aws`
- `tests/platformSetup/tofu/azure`
- `tests/platformSetup/tofu/gcp`

The root module abstracts [Input Variables](https://opentofu.org/docs/language/values/variables/) in `variables.tf` and calls the cloud provider child modules via [Module Blocks](https://opentofu.org/docs/language/modules/syntax/) in `main.tf`. It also defines the [Providers](https://opentofu.org/docs/language/providers/) and their default settings, which serve as the APIs to build cloud provider resources.

Each provider-centric child module has a similar structure. However, due to the nature of the cloud providers, they differ in how resources are built.

Currently, `main.tf` calls the child modules with different Input Variables for each flavor, enabling reuse of the same module code to build different scenarios for different flavors.


## Getting Started

### Generate OpenTofu Input Variables

To define what is actually built, you need to create [OpenTofu Input Variables](https://opentofu.org/docs/language/values/variables/). This is done by providing `*.tfvars` files and passing them via the `-var-file` command-line parameter when running `tofu apply`.

For example, to deploy the flavor `gcp-gardener_prod_trustedboot_tpm2-amd64`:

```bash
❯ cat tests/platformSetup/tofu/variables.gcp-gardener_prod_trustedboot_tpm2-amd64.tfvars
test_prefix = "bob"
platforms = ["gcp"]
archs = ["amd64"]
features = ["_trustedboot", "_tpm2"]
gcp_instance_type = "n1-standard-2"
gcp_image_file = "gcp-gardener_prod-amd64-today-local.tar.gz"
azure_subscription_id = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
gcp_project_id = "xxxxxxxx"
```

> [!TIP]
> Refer to `tests/platformSetup/tofu/variables.tf` to see all available Input Variables.


#### `tf_variables_create.py`

The script `tests/platformSetup/tofu/tf_variables_create.py` can generate variables for specific flavors or multiple flavors.

Usage:

```bash
❯ tests/platformSetup/tofu/tf_variables_create.py --help
usage: tf_variables_create.py [-h] [--flavors FLAVORS] [--root-dir ROOT_DIR] [--image-path IMAGE_PATH] [--cname CNAME] [--image-file-ali IMAGE_FILE_ALI] [--image-file-aws IMAGE_FILE_AWS] [--image-file-azure IMAGE_FILE_AZURE] [--image-file-gcp IMAGE_FILE_GCP] test_prefix

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
  --image-file-ali IMAGE_FILE_ALI
                        Specific ALI image file.
  --image-file-aws IMAGE_FILE_AWS
                        Specific AWS image file.
  --image-file-azure IMAGE_FILE_AZURE
                        Specific Azure image file.
  --image-file-gcp IMAGE_FILE_GCP
                        Specific GCP image file.
```

Example to generate sane defaults for all default flavors:

```bash
❯ tests/platformSetup/tofu/tf_variables_create.py bobs
Platform: ali
Architecture: amd64
Flavor: ali-gardener_prod-amd64
Features: []
Created: ~/gardenlinux/tests/platformSetup/tofu/variables.ali-gardener_prod-amd64.tfvars
Platform: aws
Architecture: amd64
Flavor: aws-gardener_prod-amd64
Features: []
Created: ~/gardenlinux/tests/platformSetup/tofu/variables.aws-gardener_prod-amd64.tfvars
Platform: azure
Architecture: amd64
Flavor: azure-gardener_prod-amd64
Features: []
Created: ~/gardenlinux/tests/platformSetup/tofu/variables.azure-gardener_prod-amd64.tfvars
Platform: gcp
Architecture: amd64
Flavor: gcp-gardener_prod-amd64
Features: []
Created: ~/gardenlinux/tests/platformSetup/tofu/variables.gcp-gardener_prod-amd64.tfvars
```

Example to generate variables for a specific flavor and image:

```bash
❯ tests/platformSetup/tofu/tf_variables_create.py --flavor gcp-gardener_prod_trustedboot_tpm2-amd64 --image-path .build --image-file-gcp gcp-gardener_prod_tpm2_trustedboot-amd64-1695.0-30903f3a.gcpimage.tar.gz bobs
Platform: gcp
Architecture: amd64
Flavor: gcp-gardener_prod_trustedboot_tpm2-amd64
Features: ["_trustedboot", "_tpm2"]
Created: ~/gardenlinux/tests/platformSetup/tofu/variables.gcp-gardener_prod_trustedboot_tpm2-amd64.tfvars
```

### Creating Cloud Resources with OpenTofu

Much of the logic is abstracted by the `tests/platformSetup/Makefile`. To run:

```bash
❯ make --directory=tests/platformSetup
```

<details>

```plaintext
Usage: make [target]

general targets:
help					List available tasks of the project 

platform-specific targets:
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

> [!WARNING]
> Ensure an Input Variables file exists with a matching name, e.g., `tests/platformSetup/tofu/variables.gcp-gardener_prod_trustedboot_tpm2-amd64.tfvars`.

Targets follow the typical [OpenTofu plan/apply/destroy](https://opentofu.org/docs/cli/run/) flow, extended with `show` to display resources and `login` to log in via SSH.

### Workspaces and State

Make targets use [OpenTofu Workspaces](https://opentofu.org/docs/cli/workspaces/) to isolate [State](https://opentofu.org/docs/language/state/). Workspaces created by make targets are named after the flavor and a random seed stored in `tests/platformSetup/.uuid` (first portion of the uuid). It is needed together with the workspaces to support parallel creation of named resources without creating a propper locking mechanism.

Switch between workspaces for debugging:

```bash
❯ tofu workspace list
❯ tofu workspace select gcp-gardener_prod_trustedboot-amd64-2e22801c
```


### Run Platform Tests

The `tests/Makefile` abstracts much of the logic. Run:

```bash
❯ make --directory=tests
```

<details>

```plaintext
Usage: make [target]

general targets:
help					List available tasks of the project                 
all					Run all platform tests                               

platform-specific targets:
ali-gardener_prod-amd64-test-platform                       Run platform tests via opentofu for ali-gardener_prod-amd64
aws-gardener_prod-amd64-test-platform                       Run platform tests via opentofu for aws-gardener_prod-amd64
aws-gardener_prod-arm64-test-platform                       Run platform tests via opentofu for aws-gardener_prod-arm64
aws-gardener_prod_trustedboot-amd64-test-platform           Run platform tests via opentofu for aws-gardener_prod_trustedboot-amd64
aws-gardener_prod_trustedboot-arm64-test-platform           Run platform tests via opentofu for aws-gardener_prod_trustedboot-arm64
aws-gardener_prod_trustedboot_tpm2-amd64-test-platform      Run platform tests via opentofu for aws-gardener_prod_trustedboot_tpm2-amd64
aws-gardener_prod_trustedboot_tpm2-arm64-test-platform      Run platform tests via opentofu for aws-gardener_prod_trustedboot_tpm2-arm64
azure-gardener_prod-amd64-test-platform                     Run platform tests via opentofu for azure-gardener_prod-amd64
gcp-gardener_prod-amd64-test-platform                       Run platform tests via opentofu for gcp-gardener_prod-amd64
gcp-gardener_prod-arm64-test-platform                       Run platform tests via opentofu for gcp-gardener_prod-arm64
gcp-gardener_prod_trustedboot-amd64-test-platform           Run platform tests via opentofu for gcp-gardener_prod_trustedboot-amd64
gcp-gardener_prod_trustedboot-arm64-test-platform           Run platform tests via opentofu for gcp-gardener_prod_trustedboot-arm64
gcp-gardener_prod_trustedboot_tpm2-amd64-test-platform      Run platform tests via opentofu for gcp-gardener_prod_trustedboot_tpm2-amd64
gcp-gardener_prod_trustedboot_tpm2-arm64-test-platform      Run platform tests via opentofu for gcp-gardener_prod_trustedboot_tpm2-arm64
```

</details>


## Advanced Settings

### State Management

Usually, OpenTofu stores its [State](https://opentofu.org/docs/language/state/) in the [Local Backend](https://opentofu.org/docs/language/state/backends/#state-storage). This is fine for development purposes and for local tests.

In our Github Actions we use the [Backend Type: s3](https://opentofu.org/docs/language/settings/backends/s3/) to be able to recover the state if resources fail to build up and tear down (e.g. cloud API is not responding). Also, the remote state is encrypted by OpenTofu's [State and Plan Encryption](https://opentofu.org/docs/language/state/encryption/) via the [PBKDF2 key provider](https://opentofu.org/docs/language/state/encryption/#pbkdf2) and an [AES-GCM](https://opentofu.org/docs/language/state/encryption/#aes-gcm) backed static passphrase.

#### Use Locally Encrypted State

Set the `TF_ENCRYPTION` environment variable and initialize the local backend:

```bash
❯ export TF_ENCRYPTION='''{
  "key_provider": {
    "pbkdf2": {
      "passphrase": {
        "passphrase": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
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
❯ tofu init
```

#### Create Encrypted State Backend in S3

To replicate the production setup for our Github Actions:

1. Set the `TF_ENCRYPTION` environment variable and initialize the local backend:

```bash
❯ export TF_ENCRYPTION='''{
  "key_provider": {
    "pbkdf2": {
      "passphrase": {
        "passphrase": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
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

❯ tofu init
```

2. Create a dedicated workspace for the State

```bash
❯ tofu workspace select -or-create tfstate
```

3. Create the S3 state resources

```bash
❯ tofu apply -var deploy_state_aws=true
```

4. Migrate to the S3 backend

```bash
❯ cp backend.tf.github backend.tf
```

5. Get the created Bucket

```bash
❯ tofu output -raw state_aws_bucket_name
```

6. Make sure to reference correct Region and Bucket

```bash
❯ vim backend.tf
```

7. Migrate your local State to S3

```bash
❯ tofu init -migrate-state
```

8. Switch back to the default Workspace

```bash
❯ tofu workspace select default
```

#### Recover GitHub Action's OpenTofu State Locally

Follow these steps:

1. Set the `TF_ENCRYPTION` environment variable

```bash
❯ export TF_ENCRYPTION='''{
  "key_provider": {
    "pbkdf2": {
      "passphrase": {
        "passphrase": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
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

2. Switch to the S3 backend and initialize it

```bash
❯ cp backend.tf.github backend.tf
❯ tofu init
```

3. Test if you can list and select the remote S3 state

```bash
❯ tofu workspace list
❯ tofu workspace select gcp-gardener_prod-amd64-5040a670
```

> [!WARNING]
> Cleanup remote resources if needed. This will potentially remove all resources.

```bash
❯ for i in $(tofu workspace list | grep 'ali|aws|azure|gcp' | sed 's#*##g'); do tofu workspace select $i && tofu destroy -auto-approve && tofu workspace select default && tofu workspace delete $i; done
```
