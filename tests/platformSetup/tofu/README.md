# Platform Tests with OpenTofu

## OpenTofu module structure

`tests/platformSetup/tofu` is the [Root Module](https://opentofu.org/docs/language/modules/#the-root-module) which than hosts [Child Modules](https://opentofu.org/docs/language/modules/#child-modules) for every cloud provier in:

- `tests/platformSetup/tofu/ali`
- `tests/platformSetup/tofu/aws`
- `tests/platformSetup/tofu/azure`
- `tests/platformSetup/tofu/gcp`

The root module abstracts [Input Variables](https://opentofu.org/docs/language/values/variables/) in the `variables.tf` and calls the cloud providers child modules via [Module Blocks](https://opentofu.org/docs/language/modules/syntax/) in `main.tf`. It also defines the [Providers](https://opentofu.org/docs/language/providers/) and their default settings which are the actual APIs to build cloud provider resoures.

Each provider centric child module has a similar structure. It is in the nature of the cloud providers though, that they differ in the ways to build up resources.

Currently, `main.tf` calls the child modules with different Input Variables for each flavor. This enables us to reuse the same module code to build up different scenarios for different flavors.

## Gettings Started

### Generate OpenTofu Input Variables

To define certain aspects of what is actually built up, we need to define [OpenTofu Input Variables](https://opentofu.org/docs/language/values/variables/). We do this by providing `*.tfvars` files and providing them via the `-var-file` commandline parameter when we run `tofu apply`.

This is an example to deploy the flavor `gcp-gardener_prod_trustedboot_tpm2-amd64`:

    ❯ cat tests/platformSetup/tofu/variables.gcp-gardener_prod_trustedboot_tpm2-amd64.tfvars
    test_prefix = "bob"
    platforms = ["gcp"]
    archs = ["amd64"]
    features = ["_trustedboot", "_tpm2"]
    gcp_instance_type = "n1-standard-2"
    gcp_image_file = "gcp-gardener_prod-amd64-today-local.tar.gz"
    azure_subscription_id = "0140511c-b1ca-45b6-a407-0d9d15f4ba08"
    gcp_project_id = "sap-cp-k8s-gdnlinux-gcp-test"

> [!TIP]
> Have a look at `tests/platformSetup/tofu/variables.tf` to get all available Input Variables.

#### `tf_variables_create.py`

The script `tests/platformSetup/tofu/tf_variables_create.py` can be used to generate variables for a certain flavor or even for multiple flavors.

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

To generate sane defaults for all default flavors, just run:

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

To generate for a specific flavor and image, run:

    ❯ tests/platformSetup/tofu/tf_variables_create.py --flavor gcp-gardener_prod_trustedboot_tpm2-amd64 --image-path .build --image-file-gcp gcp-gardener_prod_tpm2_trustedboot-amd64-1695.0-30903f3a.gcpimage.tar.gz bobs
    Platform: gcp
    Architecture: amd64
    Flavor: gcp-gardener_prod_trustedboot_tpm2-amd64
    Features: ["_trustedboot", "_tpm2"]
    Created: ~/gardenlinux/tests/platformSetup/tofu/variables.gcp-gardener_prod_trustedboot_tpm2-amd64.tfvars

### Creating cloud resources with OpenTofu

Much of the logic is abstracted by the `tests/platformSetup/Makefile`. You can just run:

    ❯ make --directory=tests/platformSetup

<details>

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

</details>

Just choose any of the available targets that are based on the available flavors.

> [!WARNING]
> Before you choose a target, be sure that an Input Variables file exist with a matching name, e.g. `tests/platformSetup/tofu/variables.gcp-gardener_prod_trustedboot_tpm2-amd64.tfvars`

Targets are organized in the usual [OpenTofu plan/apply/destroy](https://opentofu.org/docs/cli/run/) fashion and extended with a `show` option that displays the resources after you built them up and a conveniant `login` target to log you in via ssh.

This means you can try out what would be deployed for your given input variables with the `*-plan` target and than `apply` and `destroy` it as you like.

#### Workspaces and State

Be aware that the make targets use [OpenTofu Workspaces](https://opentofu.org/docs/cli/workspaces/) to isolate the [State](https://opentofu.org/docs/language/state/) of the different setups that are build up. You can easily switch between workspaces for debugging purposes.

    ❯ tofu workspace list
    * default
      gcp-gardener_prod-arm64-2e22801c
      gcp-gardener_prod_trustedboot-amd64-2e22801c

    ❯ tofu workspace select gcp-gardener_prod_trustedboot-amd64-2e22801c
    Switched to workspace "gcp-gardener_prod-arm64-2e22801c".    

    ❯ tofu workspace list
      default
      gcp-gardener_prod-arm64-2e22801c
    * gcp-gardener_prod_trustedboot-amd64-2e22801c

Workspaces created by the make targets are named after the flavor and a random seed. The seed is dynamically generated by the make target and placed in a file `tests/platformSetup/.uuid` (first portion of the uuid). It is needed together with the workspaces to support parallel creation of named resources without creating a propper locking mechanism.

### Run Platform Tests

Much of the logic is abstracted by the `tests/Makefile`. You can just run:

    ❯ make --directory=tests
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

To see all available targets that you can run tests on.

The make target that provisioned the cloud resource already created a pytest configfile for a `--iaas=manual` run.

The config files are created based on a flavor specific template:

    ❯ cat tests/config/manual_aws-gardener_prod_trustedboot_tpm2-amd64.yaml.template
    manual:
      # iaas=manual, so we need a way to tell pytest on which platform we run
      platform: aws
      # mandatory, the hostname/ip-address of the host the tests should run on
      host: MY_IP
      # ssh related configuration for logging in to the VM (required)
      ssh:
        # path to the ssh private key file (required)
        ssh_key_filepath: SSH_PRIVATE_KEY
        # username
        user: SSH_USER
    
      # list of features that is used to determine the tests to run
      features:
        - aws
        - gardener
        - cloud
        - server
        - base
        - _slim      
        - _trustedboot
        - _tpm2

After choosing a target, e.g. `pytest --iaas=manual --configfile=tests/config/manual_gcp-gardener_prod_trustedboot_tpm2-amd64.yaml` will be run for the flavor you chose.

An ssh connection to the provided host will be created and the unit tests run as usual.

## Advanced Settings

### State Management

Usually OpenTofu stores it's [State](https://opentofu.org/docs/language/state/) in the [Local Backend](https://opentofu.org/docs/language/state/backends/#state-storage). This is fine for development purposes and for local tests.

In our Github Actions we use the [Backend Type: s3](https://opentofu.org/docs/language/settings/backends/s3/) to be able to recover the state if resources fail to build up and tear down (e.g. cloud API is not responding). Also, the remote state is encrypted by OpenTofu's [State and Plan Encryption](https://opentofu.org/docs/language/state/encryption/) via the [PBKDF2 key provider](https://opentofu.org/docs/language/state/encryption/#pbkdf2) and an [AES-GCM](https://opentofu.org/docs/language/state/encryption/#aes-gcm) backed static passphrase.

#### use locally encrypted state

You can also use encrypted state locally like this:

```
# export TF_ENCRYPTION env variable
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

# initialize local backend
❯ tofu init
```


#### create encrypted state backend in S3

To replicate the production setup for our Github Actions, do this:

```
# export TF_ENCRYPTION env variable
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

# initialize local backend
❯ tofu init

# create dedicated workspace for state
❯ tofu workspace select -or-create tfstate

# create S3 state resources
❯ tofu apply -var deploy_state_aws=true

# migrate to S3 backend
❯ cp backend.tf.github backend.tf

# get created bucket
❯ tofu output -raw state_aws_bucket_name

# make sure to reference correct region/bucket
❯ vim backend.tf

# migrate state
❯ tofu init -migrate-state

# switch back to default workspace
❯ tofu workspace select default
```

##### create `TF_ENCRYPTION` environment variable for Github Actions

You will also need to create an Action secret in the [Github Action secrets and variables section](https://github.com/gardenlinux/gardenlinux/settings/secrets/actions).

As a prerequisite, you have to base64 encode the `TF_ENCRYPTION` environment variable:

```
# export TF_ENCRYPTION env variable
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

# encode in base64 to put in TF_ENCRYPTION secret
❯ echo $TF_ENCRYPTION | base64 -w0
```

The environment variable `TF_ENCRYPTION` is automatically picked up by the OpenTofu execution.

##### Recover Github Action's OpenTofu State on your local workstation

Revovering the Github Action's OpenTofu State may be neccessary if the cloud provider API is unavailable or you have larger bugs in the OpenTofu resource code.

After you revovered the state, you can run apply/show/delete actions on it as usual and e.g. cleanup the resources.


```
# export TF_ENCRYPTION env variable
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


# use S3 backend
❯ cp backend.tf.github backend.tf

# initialize the s3 backend
❯ tofu init

# test if you can access the remote workspaces
❯ tofu workspace list
* default
  ali-gardener_prod-amd64-6358eb3a
  aws-gardener_prod-amd64-c029b153
  aws-gardener_prod-arm64-ba0421ac
  aws-gardener_prod_trustedboot-amd64-fbc9f06f
  aws-gardener_prod_trustedboot-arm64-4ffb777d
  aws-gardener_prod_trustedboot_tpm2-amd64-7b5d78da
  aws-gardener_prod_trustedboot_tpm2-arm64-cff3cea7
  azure-gardener_prod-amd64-e13c2174
  gcp-gardener_prod-amd64-5040a670
  gcp-gardener_prod-arm64-63b8753d
  gcp-gardener_prod_trustedboot-amd64-ebcbcebf
  gcp-gardener_prod_trustedboot-arm64-953718f1
  gcp-gardener_prod_trustedboot_tpm2-amd64-6eadb3eb
  gcp-gardener_prod_trustedboot_tpm2-arm64-27f55f58
  tfstate

# now you can select any remote workspace and interact with it's state
❯ tofu workspace select gcp-gardener_prod-amd64-5040a670

# POTENTIALY DANGEROUR OPTION - delete all remote resources and workspaces
# for i in $(tofu workspace list | grep 'ali|aws|azure|gcp' | sed 's#*##g');do bash -c "tofu workspace select $i && tofu destroy -auto-approve && tofu workspace select default && tofu workspace delete $i"; done
```
