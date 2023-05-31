# Tests

# Table of Content
- [Tests](#tests)
- [Table of Content](#table-of-content)
- [General](#general)
- [Chart](#chart)
- [Unit Tests](#unit-tests)
  - [Prerequisites](#prerequisites)
  - [Location of Unit Tests](#location-of-unit-tests)
    - [Example](#example)
    - [Running Unit Tests](#running-unit-tests)
      - [Automated Unit Tests](#automated-unit-tests)
      - [chroot](#chroot)
      - [KVM](#kvm)
- [Integration Tests](#integration-tests)
  - [Prerequisites](#prerequisites-1)
  - [Using the tests on supported platforms](#using-the-tests-on-supported-platforms)
    - [General](#general-1)
    - [Public cloud platforms](#public-cloud-platforms)
      - [AWS](#aws)
        - [Configuration options](#configuration-options)
        - [Running the tests](#running-the-tests)
      - [Azure](#azure)
        - [Configuration options](#configuration-options-1)
        - [Running the tests](#running-the-tests-1)
      - [Aliyun](#aliyun)
        - [Configuration options](#configuration-options-2)
        - [Running the tests](#running-the-tests-2)
      - [GCP](#gcp)
        - [Configuration options](#configuration-options-3)
        - [Running the tests](#running-the-tests-3)
      - [Firecracker (MicroVM)](#firecracker-microvm)
        - [Configuration options](#configuration-options-4)
        - [Running the tests](#running-the-tests-4)
    - [Local test environments](#local-test-environments)
      - [CHROOT](#chroot-1)
        - [Configuration options](#configuration-options-5)
        - [Running the tests](#running-the-tests-5)
      - [KVM](#kvm-1)
        - [Configuration options](#configuration-options-6)
        - [Running the tests](#running-the-tests-6)
      - [Manual Testing](#manual-testing)
        - [Running the tests](#running-the-tests-7)
      - [OpenStack CC EE flavor](#openstack-cc-ee-flavor)
        - [Configuration options](#configuration-options-7)
        - [Running the tests](#running-the-tests-8)
      - [Local tests in the integration container](#local-tests-in-the-integration-container)
  - [Misc](#misc)
    - [Autoformat Using Black](#autoformat-using-black)
    - [Run Static Checks](#run-static-checks)
    - [Shellcheck](#shellcheck)

# General

Garden Linux supports integration testing on all major cloud platforms (Aliyun, AWS, Azur, GCP) as well as regular unit tests. To allow testing even without access to any cloud platform we created an universal `kvm` platform that may run locally and is accessed in the same way via a `ssh client object` as any other cloud platform. Therefore, you do not need to adjust tests to perform local integration tests. Next to this, the `KVM` and `chroot` platform are used for regular `unit tests`. All platforms share Pytest as a common base, are accessed in the same way (via a `RemoteClient` object) and are described in detail below. Beside this, you may also find additional tests that may be used for developing and contributing to fit the Garden Linux style guides.

# Chart
This chart briefly describes the process of unit-, platform/integration tests.

```mermaid
graph TD;
    Source --> obj01[Build Pipeline]
    obj01[Build Pipeline] --> obj02[Built Artifact]
    obj02[Built Artifact] -- The build pipeline automatically performs<br>unit tests on just created artifacts --> test01{Testing}
    obj03[External Artifact] -- An already present artifact can <br>be retested at any time --> test01{Testing}

    test01{Testing} -. Optional platform specific tests .-> test02{Integration Tests}
    test01{Testing} -- Basic unit tests on<br>a given artifact --> test03{Unit Tests}

    AWS --> test05{Platform Tests}
    Azure --> test05{Platform Tests}
    Aliyun --> test05{Platform Tests}
    GCP --> test05{Platform Tests}

    test02{Integration Tests} -.-> AWS --> test04{Feature Tests}
    test02{Integration Tests} -.-> Azure --> test04{Feature Tests}
    test02{Integration Tests} -.-> Aliyun --> test04{Feature Tests}
    test02{Integration Tests} -.-> GCP --> test04{Feature Tests}
    test03{Unit Tests} -- Runs always --> CHROOT --> test04{Feature Tests}
    test03{Unit Tests} -.-> KVM --> test04{Feature Tests}

    test05{Platform Tests} --> test_case01[gardenlinux.py]

    test04{Feature Tests} --> test_case02[feature/base/tests/test_*.py]
    test04{Feature Tests} --> test_case03[feature/cloud/tests/test_*.py]
    test04{Feature Tests} --> test_case04[...]
```

# Unit Tests
Unit testing are used to validate and test the functionality of Garden Linux sources and its whole feature sets. When adding a Garden Linux specific feature like `CIS`, all related `CIS` unit tests are executed. Each feature is represented by unit tests to ensure its conformity. Unit tests are defined as a default build target and will automatically run after each build. This also affects automated GitHub builds that are executed by GitHub runners but may also be executed manually on a defined artifact.

Unit tests are executed in a context of integration tests. This means that a specific platform type (`chroot`) of integration tests is used to perform regular `unit tests`. This is due to the fact that we want to achieve a common test platform based on `Pytest` and theses ones should still be executable on any platform without further adjustments.

## Prerequisites
Build the base test container with all necessary dependencies. This container image will contain all necessary packages and modules

 *Note: The `gardenlinux/base-test` will be autocreated by building Garden Linux and usually doesn't need to be execute manually:*

    make --directory=container build-base-test

The resulting container image will be tagged as `gardenlinux/base-test:<version>` with `<version>` being the version that is returned by `bin/garden-version` in this repository. All further tests run inside this container.

## Location of Unit Tests
These tests are located in a subfolder (`test`) within a feature's directory and must be prefixed with `test_`. This means, that any feature may provide a subfolder called `test` including their `unit test(s)`. `Pytest` will automatically include these files and validate if they need to run (e.g. `cis` tests will only run if the given artifact was built with this feature):

### Example
| Feature | Unit test | Test location |
|---|---|---|
| $FEATURE_NAME | test_$TEST_NAME.py | features/$FEATURE_NAME/test/test_$TEST_NAME.py |
| CIS | test_cis.py | [features/cis/test/test_cis.py](../features/cis/test/test_cis.py) |

### Running Unit Tests
Basic unit tests are executed after each build by the `chroot` platform. However, it may be necessary to run tests in a running system instead. Therefore, the `kvm` platform can be used.

#### Automated Unit Tests
As described, `chroot` tests are automatically performed after each build. By default, this doesn't include the `kvm` platform and may be added by appending `--tests	chroot,kvm` to the `build.sh`.

Example: `./built.sh kvm-dev --tests chroot,kvm`

#### chroot
`chroot` tests may also be executed on a given artifact afterwards. A full documentation regarding running the unit tests on a `chroot` platform can be found [here](https://github.com/gardenlinux/gardenlinux/tree/main/tests#chroot).

#### KVM
`kvm` tests may also be executed on a given artifact afterwards. A full documentation regarding running the unit tests on a `kvm` platform can be found [here](https://github.com/gardenlinux/gardenlinux/tree/main/tests#kvm).


# Integration Tests
## Prerequisites
Build the integration test container with all necessary dependencies. This container image will contain all necessary Python modules as well as the command line utilities by the Cloud providers (i.e. AWS, Azure and GCP). *Note: For `KVM` and `CHROOT` platforms the auto created `gardenlinux/base-test` container can be used (as documented) but will also work with the full-fledged testing container `gardenlinux/integration-test`.*

    make --directory=container build-integration-test

The resulting container image will be tagged as `gardenlinux/integration-test:<version>` with `<version>` being the version that is returned by `bin/garden-version` in this repository. All further tests run inside this container.

## Using the tests on supported platforms
### General

The integration tests require a config file containing vital information for interacting with the cloud providers. In the following sections, the configuration options are described in general and for each cloud provider individually.

Since the configuration options are provided as a structured YAML with the cloud provider name as root elements, it is possible to have everything in just one file.

### Public cloud platforms

These tests test Garden Linux on public cloud providers like Amazons AWS, Googles Cloud Platforms, Microsoft's Azure or Aliyun's Alibaba cloud. You need a valid subscription in these hyperscalers to run the tests.

#### AWS

Notes for AWS credentials:
- credentials must be supplied by having them ready in `~/.aws/config` and `~/.aws/credentials`
  - The `aws configure` command can be used to create these files.
- `~/.aws` gets mounted into the container that executes the integration tests
- While using MFA, a dedicated MFA session must be created.
  - This can be achieved by executing the following command (requires login)
    ```
    aws sts get-session-token --serial-number <MFA Device ID> --token-code <Token>
    ```
  - The returned `AccessKeyID`, `SecretAccessKey` and `SessionToken` must be stored in the `~/.aws/credentials` file.
  - It is useful to use a dedicated profile for the MFA session, which could look like this:
    ```
    [mfa]
    aws_access_key_id = <Access Key ID>
    aws_secret_access_key = <Secret Access Key>
    aws_session_token = <Session Token>
    region = <Region>
    ```
  - In order to let pytest use the correct profile, it must be assigned via the `AWS_PROFILE` environment variable during execution.

Use the following configuration file:

```yaml
aws:
    # region in which all test resources will be created (required)
    region: eu-central-1
    # machine/instance type of the test VM - not all machines are available in all regions (optional)
    instance_type: t3.micro
    # architecture of the image and VM to be used (optional)
    architecture: amd64
    # boot mode of the VM. One can choose between "uefi" and "legacy-bios" (optional)
    boot_mode: legacy-bios
    # UEFI data which is a base64 representation of the UEFI variable store
    # uefi_data: "dGVzdAo=..."

    # test name to be used for naming and/or tagging resources (optional)
    test_name: my_gardenlinux_test

    # list of features that is used to determine the tests to run
    features:
      - "base"

    # ssh related configuration for logging in to the VM (optional)
    ssh:
        # path to the ssh key file (optional)
        ssh_key_filepath: ~/.ssh/id_rsa_gardenlinux_test
        # passphrase for a secured SSH key (optional)
        passphrase:
        # name of the public ssh key object as it gets imported into EC2 (optional)
        key_name: gardenlinux-test-2
        # username used to connect to the EC2 instance (optional, must be admin on AWS)
        user: admin

    # if specified this already existing AMI will be used and no image uploaded (optional/alternatively required)
    #ami_id: ami-xxx
    # local/S3 image file to be uploaded for the test (optional/alternatively required)
    image: file:/build/aws/20210714/amd64/bullseye/rootfs.raw
    #image: s3://gardenlinux/objects/078f440a76024ccd1679481708ebfc32f5431569
    # bucket where the image will be uploaded to (optional)
    bucket: import-to-ec2-gardenlinux-validation

    # keep instance running after tests finishes (optional)
    keep_running: false
```

##### Configuration options

<details>

- **region** _(required)_: the AWS region in which all test relevant resources will be created
- **instance-type** _(optional)_: the instance type that will be used for the EC2 instance used for testing, defaults to `t3.micro` if not specified
- **architecture** _(optional)_: the architecture under which the AMI of the image to test should be registered (`amd64` or `arm64`), must match the instance type, defaults to `amd64` if not specified
- **boot_mode** _(optional)_: the boot mode that the AMI of the image should be started with. Keep in mind that Graviton (`arm64`) can only use UEFI. Choose between `uefi` and `legacy-bios`.
- **uefi_data** _(optional)_: Base64 representation of the non-volatile UEFI variable store. You can inspect and modify the UEFI data by using the python-uefivars tool on GitHub.

- **test_name** _(optional)_: a name that will be used as a prefix or tag for the resources that get created in the hyperscaler environment. Defaults to `gl-test-YYYYmmDDHHMMSS` with _YYYYmmDDHHMMSS_ being the date and time the test was started.

- **ssh_key_filepath** _(optional)_: The SSH key that will be deployed to the EC2 instance and that will be used by the test framework to log on to it. Must be the file containing the private part of an SSH keypair which needs to be generated with `openssh-keygen` beforehand. If not provided, a new SSH key with 2048 bits will be generated just for the test.
- **passphrase** _(optional)_: If the given SSH key is protected with a passphrase, it needs to be provided here.
- **key_name** _(optional)_: The SSH key gets uploaded to EC2, this is the name of the key object resource.
- **user** _(optional)_: The user that will be provisioned to the EC2 instance, which the SSH key gets assigned to and that is used by the test framework to log on the EC2 instance. Defaults to `admin`.

- **ami_id** _(optional/alternatively required)_: If the tests should get executed against an already existing AMI, this is its ID. It must exist in the region given above. Either **ami_id** or **image** must be supplied but not both.
- **image** _(optional/alternatively required)_: If the tests should be executed against a Garden Linux filesystem snapshot that resulted from (local) build, this option is the URI that points to it. The file must be of type `.raw`. Either **ami_id** or **image** must be supplied but not both.
The URI can be:
    - `file:/path/to/my/rootfs.raw`: for local files
    - `s3://mybucketname/objects/objectkey`: for files in S3

- **bucket** _(optional)_: To create an AMI/EC2 instance from a local filesystem snapshot, it needs to be uploaded to an S3 bucket first. The bucket needs to exist in the given region and its name must be provided here. If not provided, a bucket will be created in the given region.

- **keep_running** _(optional)_: if set to `true`, all tests resources, especially the VM will not get removed after the test (independent of the test result) to allow for debugging. Defaults to `False`.

</details>

##### Running the tests

Start Podman container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount AWS credential folder (usually `~/.aws`) to `/root/.aws`
- mount SSH keys that are used to log in to the virtual machine to `/root/.ssh`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with config file to `/config`

```
sudo podman run -it --rm -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.aws:/root/.aws -v $HOME/.ssh:/root/.ssh -v ~/config:/config gardenlinux/integration-test:`bin/garden-version` /bin/bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=aws --configfile=/config/myawsconfig.yaml

#### Azure

Login using the following command on your local machine (i.e. not inside of the integration test container) to authenticate to Azure and set up the API access token:

    az login

**Note:** other means of authentication, e.g. usage of service accounts should be possible.

Use the following test configuration:

```yaml
azure:
    # region/zone/location in Azure where the test resources will get created (required)
    location:
    # the Azure subscription name to be used (required/alternatively optional)
    subscription: my-subscription-id
    # the Azure subscription ID to be used (required/alternatively optional)
    subscription_id: 00123456-abcd-1234-5678-1234abcdef78
    # resource group if omitted a new group will be created (optional)
    resource_group: rg-gardenlinux-test-01
    # network security group (optional)
    nsg_name: nsg-gardenlinux-test-42
    # vm_size specifies the Azure vm size to be used for the test (optional)
    vm_size: Standard_D4_v4
    # hyperV generation to use. Possible values are 'V1' and 'V2'. Default is 'V1'
    hyper_v_generation: V1
    # architecture to use. Possible values are 'x64' and 'Arm64'. Default is 'x64'
    architecture: x64
    # enable accelerated networking for the VM on which the test runs (optional)
    accelerated_networking: false

    # test name to be used for naming and/or tagging resources (optional)
    test_name: my_gardenlinux_test

    # storage account to be used for image upload (optional)
    storage_account_name: stggardenlinuxtest01
    # local image file to be uploaded and to be tested (required/alternatively optional)
    image: file:/build/azure/20210915/amd64/bullseye/rootfs.vhd
    #image: s3://gardenlinux/objects/078f440a76024ccd1679481708ebfc32f5431569
    # region of the S3 bucket from where the image should be downloaded from (optional)
    #image_region: eu-central-1
    # already existing image in Azure to be used for testing (required/alternatively optional)
    image_name: <image name>

    # list of features that is used to determine the tests to run
    features:
      - "base"

    # ssh related configuration for logging in to the VM (optional)
    ssh:
        # path to the ssh key file (optional)
        ssh_key_filepath: ~/.ssh/id_rsa_gardenlinux_test
        # passphrase for a secured SSH key (optional)
        passphrase:
        # name of the public ssh key object as it gets imported into Azure (optional)
        ssh_key_name: gardenlinux-test-2
        # username used to connect to the Azure instance (optional)
        user: azureuser

    # keep instance running after tests finishes (optional)
    keep_running: false
```

##### Configuration options

Only three parameters are required for the test: the Azure `subscription` or `subscription_id`, the Azure `location` and the image to be tested. All other parameters are optional and can be generated at runtime.

<details>

- **location** _(required)_: the Azure region in which all test relevant resources will be created
- **subscription** _(required/optional)_: The Azure subscription (as in subscription name) which is used for creating all relevant resources and running the test. Either the subscription name or the `subscription_id` needs to be provided.
- **subscription_id** _(required/optional)_: The Azure subscription (its ID) which is used for creating all relevant resources and running the test. Either the 'subscription' name or its needs to be provided.
- **resource_group** _(optional)_: all relevant resources for the integration test will be assigned to an Azure resource group. If you want to reuse an existing resource group, you can specify it here. If left empty, a new resource group gets created for the duration of the test.
- **nsg_name** _(optional)_: The integration tests need to create a new network security group, this is its name. If you want to reuse an existing security group, specify its name here. If left empty, a new network security group will be created for the duration of the test.
- **vm_size** _(optional)_: The given size will be used for the Azure virtual machine the test runs on. Check [this document](https://docs.microsoft.com/en-us/azure/virtual-machines/sizes) for a list of possible VM sizes. Remember that the VM size will have an impact on test performance and startup times (which get tested and produce a failure should they exceed 30 seconds). The VM size also defines the CPU architecture. This setting defaults to `Standard_D4_v4` which matches the architecture `x64`, for running `Arm64` images the VM size `Standard_D4ps_v5` would be a good choice to start with.
- **hyper_v_generation** _(optional)_: Choose the HyperV generation of the virtual machine created from the image. Possible values are 'V1' or 'V2'. If not set, 'V1' will be used as a default.
    - 'V1': Boot = PCAT, Disk controllers = IDE
    - 'V2': Boot = UEFI, Disk controllers = SCSI
- **architecture** _(optional)_: Choose the architecture. Azure offers x86_64 (x64) and Arm64. Make sure to also choose a VM size that matches the architecture. When running an Arm64 image the HyperV generation needs to be 'V2'. Defaults to `x64`.
- **accelerated_networking** _(optional)_: Enables [Azure Accelerated Networking](https://docs.microsoft.com/en-us/azure/virtual-network/accelerated-networking-overview) for the VM on which the test is going to run. Defaults to `false`, thus accelerated networking disabled.

- **test_name** _(optional)_: a name that will be used as a prefix or tag for the resources that get created in the hyperscaler environment. Defaults to `gl-test-YYYYmmDDHHMMSS` with _YYYYmmDDHHMMSS_ being the date and time the test was started.

- **storage_account_name** _(optional)_: the storage account to which the image gets uploaded
- **image_name** _(optional/required)_: If the tests should get executed against an already existing Image, this is its name. Either **image_name** or **image** must be supplied but not both.
- **image** _(optional/required)_: If the tests should be executed against a Garden Linux filesystem snapshot that resulted from a local build, this option is the path that points to it. The file must be of type `.vhd`. The image will be removed from Azure once the test finishes. Either **image_name** or **image** must be supplied but not both.
The URI can be:
    - `file:/path/to/my/rootfs.vhd`: for local files
    - `s3://mybucketname/objects/objectkey`: for files in S3
- **image_region** _(optional)_: If the image comes from an S3 bucket, the bucket location to download from can be specified here. Defaults to `eu-central-1` if omitted.

- **ssh_key_filepath** _(optional)_: The SSH key that will be deployed to the Azure instance and that will be used by the test framework to log on to it. Must be the file containing the private part of an SSH keypair which needs to be generated with `openssh-keygen` beforehand. If left empty, a temporary key with 2048 bits will be generated by the test.
- **passphrase** _(optional)_: If the given SSH key is protected with a passphrase, it needs to be provided here.
- **ssh_key_name** _(optional)_: The SSH key gets uploaded to Azure, this is the name of the key object resource.
- **user** _(optional)_: The user that will be provisioned to the Azure instance, which the SSH key gets assigned to and that is used by the test framework to log on the Azure instance. If not provided, the user defaults to `azureuser`.

- **keep_running** _(optional)_: if set to `true`, all tests resources, especially the VM will not get removed after the test (independent of the test result) to allow for debugging

</details>

##### Running the tests

Start Podman container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount Azure credentials to `/root/.azure`
- mount SSH keys to `/root/.ssh`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with config file to `/config`

```
sudo podman run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.azure:/root/.azure -v $HOME/.ssh:/root/.ssh -v ~/config:/config  gardenlinux/integration-test:`bin/garden-version` bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=azure --configfile=/config/myazconfig.yaml


#### Aliyun

You need credentials as used for the aliyun command line client, e.g. a `config.json` document. Prior to running the tests the following objects must be created in the account:

- A vSwitch with a cidr range (e.g. 192.168.0.0/24)
- A security group which allows ingress traffic on TCP for SSH (default: 22) from source IP address of the test run
- a bucket for uploading the disk image files

Use the following test configuration:

```yaml
ali:
    # mandatory, aliyun credential file location (config.json)
    credential_file:

    # optional, if an image id is provided the test will not attempt
    # to upload an image
    image_id:   # m-....

    # image file (qcow2)
    image:  # image.qcow2

    # region of the S3 bucket from where the image should be downloaded from (optional)
    #image_region: eu-central-1

    # a valid instance type for the selected region
    instance_type: ecs.t5-lc1m2.large

    # mandatory, the security group id
    security_group_id:  # sg-...

    # mandatory, the vswitch id
    vswitch_id:  # vsw-...

    # mandatory, region and zone
    region_id: eu-central-1
    zone_id: eu-central-1a

    # mandatory: bucket name
    bucket:  # my-test-upload-bucket

    # optional, path in bucket
    bucket_path: integration-test

    # list of features that is used to determine the tests to run
    features:
      - "base"

    # ssh related configuration for logging in to the VM (required)
    ssh:
        # path to the ssh key file (required)
        ssh_key_filepath: ~/.ssh/id_rsa_gardenlinux_test
        # key name
        key_name: gardenlinux-test
        # passphrase for a secured SSH key (optional)
        passphrase:
        # username
        user: admin

    # keep instance running after tests finishes if set to true (optional)
    keep_running: false
```

##### Configuration options

<details>

- **credential_file**:
- **image_id**:
- **image** _(optional/required)_: If the tests should be executed against a Garden Linux filesystem snapshot that resulted from a local build, this option is the path that points to it. The file must be of type `.qcow2`. The image will be removed from Ali-Cloud once the test finishes. Either **image_id** or **image** must be supplied but not both.
The URI can be:
    - `file:/path/to/my/rootfs.qcow2`: for local files
    - `s3://mybucketname/objects/objectkey`: for files in S3
- **image_region** _(optional)_: If the image comes from an S3 bucket, the bucket location to download from can be specified here. Defaults to `eu-central-1` if omitted.
- **instance_type**: ecs.t5-lc1m2.large
- **security_group_id**:  # sg-...
- **vswitch_id**:  # vsw-...
- **region_id**: eu-central-1
- **zone_id**: eu-central-1a
- **bucket**:  # my-test-upload-bucket
- **bucket_path**: integration-test

- **test_name** _(optional)_: a name that will be used as a prefix or tag for the resources that get created in the hyperscaler environment. Defaults to `gl-test-YYYYmmDDHHMMSS` with _YYYYmmDDHHMMSS_ being the date and time the test was started.

- **ssh_key_filepath** _(required)_: The SSH key that will be deployed to the ECS instance and that will be used by the test framework to log on to it. Must be the file containing the private part of an SSH keypair which needs to be generated with `openssh-keygen` beforehand.
- **key_name** _(required)_: The SSH key gets uploaded to ECS, this is the name of the key object resource.
- **passphrase** _(optional)_: If the given SSH key is protected with a passphrase, it needs to be provided here.
- **user** _(required)_: The user that will be provisioned to the ECS instance, which the SSH key gets assigned to and that is used by the test framework to log on the ECS instance.

- **keep_running** _(optional)_: if set to `true`, all tests resources, especially the VM will not get removed after the test (independent of the test result) to allow for debugging

</details>

##### Running the tests

Start Podman container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount GCP credentials to `/root/.config`
- mount SSH keys to `/root/.ssh`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with config file to `/config`

```
sudo podman run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.config:/root/.config -v $HOME/.ssh:/root/.ssh -v ~/config:/config  gardenlinux/integration-test:`bin/garden-version` bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=ali --configfile=/config/mygcpconfig.yaml

#### GCP

Obtain credentials by using the following command to authenticate to Google Cloud Platform and set up the API access token:

    gcloud auth application-default login

Use the following test configuration:

```yaml
gcp:
    # project id (required)
    project:
    # GCP region where the test resources should be created (required)
    region: europe-west1
    # zone where the VM should be created (required)
    zone: europe-west1-d

    # upload this local image to GCE and use it for testing (optional/required)
    image: file:/build/gcp-dev/20210915/amd64/bullseye/rootfs-gcpimage.tar.gz

    # enable uefi boot, default is legacy boot (optional)
    #uefi: false
    # enable secureboot, implies uefi boot, default is off (optional)
    #secureboot: false
    secureboot_parameters:
        # paths to the secureboot keys and database, needed for secureboot (optional)
        #db_path: /gardenlinux/cert/secureboot.db.auth
        #kek_path: /gardenlinux/cert/secureboot.kek.auth
        #pk_path: /gardenlinux/cert/secureboot.pk.auth
        # the certificate type for secureboot, possible values are `BIN`, `X509`. Default is `BIN`
        #cert_file_type: BIN

    # GCE machine type (optional)
    machine_type: n1-standard-2

    # test name to be used for naming and/or tagging resources (optional)
    test_name: my_gardenlinux_test

    # list of features that is used to determine the tests to run
    features:
      - "base"

    # ssh related configuration for logging in to the VM (required)
    ssh:
        # path to the ssh key file (required)
        ssh_key_filepath: ~/.ssh/id_rsa_gardenlinux_test
        # passphrase for a secured SSH key (optional)
        passphrase:
        # username used to connect to the Azure instance (required)
        user: gardenlinux

    # keep instance running after tests finishes (optional)
    keep_running: false
```

##### Configuration options

<details>

- **project** _(required)_: the GCP project which is used for creating all relevant resources and running the tests
- **zone** _(required)_: the GCP zone in which all test relevant resources will be created

- **service_account_json_path** _(optional)_: If a service account JSON file is provided, it will be used to authenticate to GCP instead of using an access token.

- **image_name** _(optional/required)_: If the tests should get executed against an already existing Image, this is its name. Either **image_name** or **image** must be supplied but not both.
- **image** _(optional/required)_: If the tests should be executed against a Garden Linux filesystem snapshot that resulted from a local build, this option is the path that points to it. The file must be of type `.tar.gz`. Either **image_name** or **image** must be supplied but not both.
The URI can be:
    - `file:/path/to/my/rootfs.tar.gz`: for local files
    - `s3://mybucketname/objects/objectkey`: for files in S3
- **image_region** _(optional)_: If the image comes from an S3 bucket, the bucket location to download from can be specified here. Defaults to `eu-central-1` if omitted.

- **bucket** _(optional)_: To create a GCE machine image from a local filesystem snapshot, it needs to be uploaded to a GCS bucket first. The will be created on the fly and a name will be generated if this field is left empty.

- **uefi** _(optional)_: To enable UEFI boot, by default legacy boot is used. Default is `false`

- **secureboot** _(optional)_: To enable secureboot, if secureboot is enabled UEFI boot will be used, no matter how the `uefi` option is set. For secureboot it is important that the path options to the keys and database are set properly. Default is `false`. 
- **db_path** _(optional)_: The path to the signature database for secureboot. Default is `/gardenlinux/cert/secureboot.db.auth`
- **kek_path** _(optional)_: The path to the key exchange key for secureboot. Default is `/gardenlinux/cert/secureboot.kek.auth`
- **pk_path** _(optional)_: The path to the platform key for secureboot. Default is `/gardenlinux/cert/secureboot.pk.auth`
- **cert_file_type** _(optional)_: The type of the certificate, allowed values are `BIN` or `X509`. Default is `BIN`

- **machine_type** _(optional)_: The GCE machine type to be used to create the GCE instance for the test. Defaults to `n1-standard-2` if not given.

- **ssh_key_filepath** _(required)_: The SSH key that will be deployed to the GCE instance and that will be used by the test framework to log on to it. Must be the file containing the private part of an SSH keypair which needs to be generated with `openssh-keygen` beforehand.
- **passphrase** _(optional)_: If the given SSH key is protected with a passphrase, it needs to be provided here.
- **user** _(required)_: The user that will be provisioned to the GCE instance, which the SSH key gets assigned to and that is used by the test framework to log on the Azure instance.

- **keep_running** _(optional)_: if set to `true`, all tests resources, especially the VM will not get removed after the test (independent of the test result) to allow for debugging

</details>

##### Running the tests

Start Podman container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount GCP credentials to `/root/.config`
- mount SSH keys to `/root/.ssh`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with config file to `/config`

```
sudo podman run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.config:/root/.config -v $HOME/.ssh:/root/.ssh -v ~/config:/config  gardenlinux/integration-test:`bin/garden-version` bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=gcp --configfile=/config/mygcpconfig.yaml

#### Firecracker (MicroVM)

Firecracker tests are designed to run directly on your platform. Currently, AMD64 and ARM64 architectures are supported **without any further cross platform support**.

**Notes**:
Firecracker is currently limited to Linux base platforms only. Additionally, hardware acceleration is needed. Make sure, `/dev/kvm` is usable.

Use the following test configuration:

```yaml
firecracker:
    # Path to a final artifacts. This includes the Kernel
    # and a filesystem image
    kernel: /gardenlinux/.build/firecracker.vmlinux
    image: /gardenlinux/.build/firecracker.ext4
    # The filesystem image can optionally turned to readonly
    # if necessary (optional)
    # Default: False
    readonly: False
    # Filesystem mount path to mount filesystem image for further
    # includes and adjustments (optional)
    # Default: tmpdir
    image_mount: /tmp/image_mount

    # Network configurations for microvm and host system
    # including additional bridge interface definitions. In default,
    # this runs within a container. Therefore, these options can mostly
    # be used as defaults and do not need any further adjustments
    network:
        # Firecracker / microvm
        ip_vm: 169.254.0.21           # Optional (Default: 169.254.0.21)
        port_ssh_vm: 2222             # Optional (Default: 2222)
        netmask_vm: 255.255.255.252   # Optional (Default: 255.255.255.252)
        if_vm: eth0                   # Optional (Default: eth0)
        mac_vm: 02:FC:00:00:00:05     # Optional (Default: 02:FC:00:00:00:05)

        # Hostsystem
        ip_host: 169.254.0.22         # Optional: (Default: 169.254.0.22)
        netmask_host: 255.255.255.252 # Optional (Default: 255.255.255.252)
        if_host: eth0                 # Optional (Default: eth0)
        if_tap_host: tap0             # Optional (Default: tap0)
        if_bridge_host: br0           # Optional (Default: br0)

    # Keep machine running after performing tests
    # for further debugging (optional)
    # Default: false
    #keep_running: false

    # List of features that is used to determine the tests to run
    features:
      - "base"

    # SSH configuration (required)
    ssh:
        # Defines if a new SSH key should be generated (optional)
        # Default: true
        ssh_key_generate: true

        # Defines path where to look for a given key
        # or to save the new generated one. Take care
        # that you do NOT overwrite your key. (required)
        ssh_key_filepath: /tmp/ssh_priv_key

        # Defines if a passphrase for a given key is needed (optional)
        #passphrase: xxyyzz

        # Defines the user for SSH login (required)
        # Default: root
        user: root
```

##### Configuration options

<details>

- **kernel** _(required)_: If the tests should get executed against an already existing image, this is its kernel name.
- **image** _(required)_: If the tests should get executed against an already existing image, this is its filesystem image name.
- **readonly** _(optional)_: Defines if the filesystem image should be mounted as readonly.
- **image_mount** _(optional)_: Defines the path where the image should be mounted (and where it can be modified).
- **ip_vm** _(optional)_: Defines the used IP address within the Firecracker/microvm instance.
- **port_ssh_vm** _(optional)_: Defines the used SSH port within the Firecracker/microvm instance.
- **netmask_vm** _(optional)_: Defines the used netmask (mostly /30) within the Firecracker/microvm instance.
- **if_vm** _(optional)_: Defines the local interface within the Firecracker/microvm instance.
- **mac_vm** _(optional)_: Defines the MAC address for the local interface within the Firecracker/microvm instance.
- **ip_host** _(optional)_: Defines the IP address on the host system.
- **netmask_host** _(optional)_: Defines the netmask (mostly /30) on the host system.
- **if_host** _(optional)_: Defines the regular uplink interface on the host system.
- **if_tap_host** _(optional)_: Defines the tap device on the host system to create.
- **if_bridge_host** _(optional)_: Defines the bridge device on the host system to create.
- **keep_running** _(optional)_: if set to `true`, all tests resources, especially the VM will not get removed after the test (independent of the test result) to allow for debugging

</details>

##### Running the tests

Start Podman container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- add `/dev/kvm` device to Container (or run privileged mode)
- run in privileged mode for KVM device and network interface mappings

```
sudo podman run -it --rm --privileged -v `pwd`:/gardenlinux gardenlinux/integration-test:`bin/garden-version` bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=firecracker --configfile=/config/myfirecrackerconfig.yaml


### Local test environments

These tests flavours will make use of chroot, KVM virtual machines or OpenStack environments and thus can be used locally without a paid subscription to a public cloud provider.

#### CHROOT

CHROOT tests are designed to run directly on your platform within a `chroot` environment and boosts up the time for the integration tests that do not need any target platform.

Notes:
 * CHROOT will run inside your `integration-test` Docker container
 * Podman container needs `SYS_ADMIN`, `MKNOD`, `AUDIT_WRITE` and `NET_RAW` capability
 * Temporary SSH keys are auto generated and injected

Use the following configuration file to proceed; only the path to the TAR image needs to be adjusted:

```yaml
chroot:
    # Path to a final artifact. Represents the .tar.xz archive image file (required)
    image: /gardenlinux/.build/kvm_dev-amd64-dev-local.tar.xz

    # IP or hostname of target machine (required)
    # Default: 127.0.0.1
    ip: 127.0.0.1

    # port for remote connection (required)
    # Default: 2223
    port: 2222

    # list of features that is used to determine the tests to run
    features:
      - "base"

    # SSH configuration (required)
    ssh:
        # Defines path where to look for a given key
        # or to save the new generated one. Take care
        # that you do NOT overwrite your key. (required)
        ssh_key_filepath: /tmp/ssh_priv_key

        # Defines the user for SSH login (required)
        # Default: root
        user: root
```

##### Configuration options

<details>

- **features** _(optional)_: If not set, the feature tests will be skipped, if set it must contain a list of features. The tests defined in the listed features will be used. The features used to build the image can be found in the _image\_name_.os-release file in the output directory.
- **ssh_key_filepath** _(required)_: The SSH key that will be injected to the *chroot* and that will be used by the test framework to log on to it. In default, you do **not** need to provide or mount your real SSH key; a new one will be generated and injected by every new run. However, if you really want, a present one can be defined - take care that this will not be overwritten and set `ssh_key_generate` to false.
- **user** _(required)_: The user that will be used for the connection.
</details>

##### Running the tests

Start Podman container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with configfile to `/config`
- NOTE: The testing SSHd expects the regular `authorized_keys` file to be named as `test_authorized_keys`

```
sudo podman run --cap-add SYS_ADMIN,MKNOD,AUDIT_WRITE,NET_RAW --security-opt apparmor=unconfined -it --rm -v `pwd`:/gardenlinux gardenlinux/base-test:`bin/garden-version` /bin/bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=chroot --configfile=/config/mychrootconfig.yaml


#### KVM

KVM tests are designed to run directly on your platform. Currently, AMD64 and ARM64 architectures are supported.
Notes:
 * KVM/QEMU will run inside your `integration-test` Docker container
 * (Default) New temporary SSH keys are auto generated and injected
 * (Default: amd64) AMD64 and ARM64 architectures are supported

Use the following configuration file to proceed; only the path to the image needs to be adjusted:

```yaml
kvm:
    # Path to a final artifact. Represents the .raw image file (required)
    image: /gardenlinux/.build/kvm_dev-amd64-dev-local.raw

    # IP or hostname of target machine (optional)
    # Default: 127.0.0.1
    #ip: 127.0.0.1

    # port for remote connection (required)
    # Default: 2223
    port: 2223

    # Keep machine running after performing tests
    # for further debugging (optional)
    # Default: false
    #keep_running: false

    # list of features that is used to determine the tests to run
    features:
      - "base"

    # Architecture to boot
    # Default: amd64
    #arch: amd64

    # Hardware accelerator (kvm, hvf, none)
    # Default: Will be auto detected (Fallback: None)
    #accel: kvm

    # SSH configuration (required)
    ssh:
        # Defines if a new SSH key should be generated (optional)
        # Default: true
        ssh_key_generate: true

        # Defines path where to look for a given key
        # or to save the new generated one. Take care
        # that you do NOT overwrite your key. (required)
        ssh_key_filepath: /tmp/ssh_priv_key

        # Defines if a passphrase for a given key is needed (optional)
        #passphrase: xxyyzz

        # Defines the user for SSH login (required)
        # Default: root
        user: root
```

##### Configuration options

<details>

- **features** _(optional)_: If not set, the feature tests will be skipped, if set it must contain a list of features. The tests defined in the listed features will be used. The features used to build the image can be found in the _image\_name_.os-release file in the output directory.
- **ssh_key_filepath** _(required)_: The SSH key that will be injected to the .raw image file and that will be used by the test framework to log on to it. In default, you do **not** need to provide or mount your real SSH key; a new one will be generated and injected by every new run. However, if you really want, a present one can be defined - take care that this will not be overwritten and set `ssh_key_generate` to false.
- **arch** _(optional)_: The architecture under which the AMI of the image to test should be registered (`amd64` or `arm64`), must match the instance type, defaults to `amd64` if not specified.
- **accel** _(optional)_: The hardware accelerator to use (`kvm`, `hvf`, `none`). Default: Will be auto detected (Fallback: None).
- **passphrase** _(optional)_: If the given SSH key is protected with a passphrase, it needs to be provided here.
- **user** _(required)_: The user that will be used for the connection.
- **keep_running** _(optional)_: If set to `true`, all tests resources, especially the VM will not get removed after the test (independent of the test result) to allow further debugging. Default: `False`.

</details>

##### Running the tests

Start Podman container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount /boot and /lib/modules for guestfish support (required for KVM tools)
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with configfile to `/config`
- mount SSH keys that are used to log in to the virtual machine to `/root/.ssh` (Optional: only needed when no SSH keys should be autogenerated)
- KVM: For `KVM` accel we need to run `Podman` with `--device=/dev/kvm` option
- NOTE: The testing SSHd expects the regular `authorized_keys` file to be named as `test_authorized_keys`

**With SSH autogeneration**
This is the default and recommended way.
```
sudo podman run -it --rm --device=/dev/kvm -v /boot/:/boot -v /lib/modules:/lib/modules -v `pwd`:/gardenlinux gardenlinux/base-test:`bin/garden-version` /bin/bash
```

**Without SSH autogeneration**
Use this only when really needed.
```
sudo podman run -it --rm --device=/dev/kvm -v `pwd`:/gardenlinux -v /boot/:/boot -v /lib/modules:/lib/modules -v `pwd`/.build/:/build -v $HOME/.ssh:/root/.ssh -v ~/config:/config gardenlinux/base-test:`bin/garden-version` /bin/bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=kvm --configfile=/config/mykvmconfig.yaml


#### Manual Testing

So for some reason, you do not want to test Garden Linux by using a tool that automatically sets up the testbed in a cloud environment for you.

You rather want to set up a host running Garden Linux yourself, create a user in it, somehow slip in an SSH public key and have a hostname/ip-address you can use to connect. Now all you want is to have the tests run on that host. This section about _Manual testing_ is for you then.

Use the following (very simple) test configuration:

```yaml
manual:
    # mandatory, the hostname/ip-address of the host the tests should run on
    host:

    # ssh related configuration for logging in to the VM (required)
    ssh:
        # path to the ssh private key file (required)
        ssh_key_filepath: ~/.ssh/id_rsa_gardenlinux_test
        # passphrase for a secured SSH key (optional)
        passphrase:
        # username
        user: admin
```

##### Running the tests

Start Podman container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount SSH keys to `/root/.ssh`
- mount directory with configfile to `/config`

```
sudo podman run -it --rm  -v `pwd`:/gardenlinux -v $HOME/.ssh:/root/.ssh -v ~/config:/config  gardenlinux/integration-test:`bin/garden-version` bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=manual --configfile=/config/myconfig.yaml


#### OpenStack CC EE flavor

Obtain credentials by downloading an OpenStack RC file and source it after adding your password to it. Alternatively you could statically add the password to it (environment variable `OS_PASSWORD`) and specify that file in the configuration.

**Note** that the test will not attempt to create networks, security groups, or attached floating IPs to the virtual machines. The security group and network must exist and most likely the test will have to be executed from a machine in the same network.

Use the following test configuration:

```yaml
openstack_ccee:
    # the OpenStack RC filename
    credentials:

    # if an image id is provided the test will not attempt
    # to upload an image
    # image_id: e3685bf1-2b6d-4291-86af-d4a73d54c6bd

    # image file (a vmdk)
    image: <image-file.vmdk>

    # image name is optional, if not provided a name will be chosen
    image_name: integration-test

    # OpenStack flavor (`openstack flavor list`)
    flavor: g_c1_m2

    # security group (must exist)
    security_group: gardenlinux-sg

    # network name (must exist)
    network_name: gardenlinux

    # list of features that is used to determine the tests to run
    features:
      - "base"

    # ssh related configuration for logging in to the VM (required)
    ssh:
        # path to the ssh key file (required)
        ssh_key_filepath: ~/.ssh/id_rsa_gardenlinux_test
        # key name in OpenStack
        key_name: gardenlinux_integration_test
        # passphrase for a secured SSH key (optional)
        passphrase:
        # username used to connect to the Azure instance (required)
        user: gardenlinux

    # keep instance running after tests finishes (optional)
    keep_running: false
```

##### Configuration options

<details>

- **credentials** _(optional)_: the openstack rc file downloaded from the UI with the password added. If unset the test runtime will read the values from the environment

- **image_name** _(optional)_: the image name for the uploaded image. If unset a generic name will be used.
- **image_id** _(optional)_: if specified the tests will use an existing image for the test. No image will be uploaded
- **image** _(optional/required)_: if no **image_id** is specified this must reference the image `vmdk` file.
- **flavor** _(required)_: an existing flavor name (installation specific)
- **security_group** _(required)_: the security group name for the virtual machine
- **network_name** _(required)_: the network name for the virtual machine
- **ssh_key_filepath** _(required)_: The SSH key that will be deployed to the GCE instance and that will be used by the test framework to log on to it. Must be the file containing the private part of an SSH keypair which needs to be generated with `openssh-keygen` beforehand.
- **passphrase** _(optional)_: If the given SSH key is protected with a passphrase, it needs to be provided here.
- **user** _(required)_: The user that will be provisioned to the GCE instance, which the SSH key gets assigned to and that is used by the test framework to log on the Azure instance.

- **keep_running** _(optional)_: if set to `true`, all tests resources, especially the VM will not get removed after the test (independent of the test result) to allow for debugging

</details>

##### Running the tests

Start Podman container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount GCP credentials to `/root/.config`
- mount SSH keys to `/root/.ssh`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with configfile to `/config`

```
sudo podman run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.config:/root/.config -v $HOME/.ssh:/root/.ssh -v ~/config:/config  gardenlinux/integration-test:`bin/garden-version` bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=openstack-ccee --configfile=/config/mygcpconfig.yaml


#### Local tests in the integration container

Sometimes it is neccessary to run tests locally for build results and not in a chroot or kvm environment that is accessed via ssh. This can be achieved by using the build results in the base-test container with the `local` configuration for `pytest`.

The following describes the configuration needed to run local tests.

```yaml
local:
    # configuration parameters for tests separated by features
    oci:
      # Path to a final artifact. Represents the .tar.xz archive image file (required)
      image: /build/kvm_dev_oci-amd64-today-local.oci.tar.xz
      kernel: /build/kvm_dev_oci-amd64-today-local.vmlinuz

    garden_feat:

```

##### Configuration options

<details>

- **oci** contains the configuration options for local test `test_oci`
    - **image** the build result image used within the tests
    - **kernel** the name for the builded kernel

- **garden_feat** contains the configuration option for the `test_garden_feat` test. This is just an example since the `test_garden_feat` test does not have any configuration options

Check the [readme](local/README.md) for detailed configuration options of all the local tests.
</details>

##### Running the tests

Start Podman container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with configfile to `/config`

```
sudo podman run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v ~/config:/config  gardenlinux/base-test:`bin/garden-version` bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=local --configfile=/config/mylocalconfig.yaml

NOTE: With the `-k EXPRESSION` you can filter the tests by name to only run the tests you want, instead of all local tests. See `pytest --help` for more information.

## Misc
Within this section further tests are listed that may help developing and contributing on Garden Linux. These tests are disjunct from the Garden Linux code itself and may only perform validation on code (like `Shellcheck` or `autopep`).

### Autoformat Using Black

in order to auto format the source code run

    pipenv run black .

### Run Static Checks

    pipenv run flake8 .

### Shellcheck
Shellcheck is a static analysis tool and allows to analyses and validate given scripts. Tests must be executed explicitly via `pytest shellcheck`. This tool is disjunct from Garden Linux itself and can run on any files within the test container. For more details see Shellcheck [shellcheck/README.md](shellcheck/README.md).

    pytest shellcheck --severity=error
