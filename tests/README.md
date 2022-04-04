# Tests

## Table of Content
- [Full Integration Tests Including Image Upload](#Full-Integration-Tests-Including-Image-Upload)
  * [General](#General)
  * [Unit Tests](#Unit-Tests)
  * [Prerequisites](#Prerequisites)
- [Examples for Supported Platforms](#Examples-for-Supported-Platforms)
  * [General](#General)
  * [Aliyun](#Aliyun)
  * [AWS](#AWS)
  * [Azure](#Azure)
  * [CHROOT](#CHROOT)
  * [GCP](#GCP)
  * [KVM](#KVM)
  * [OpenStack CC EE flavor](#OpenStack-CC-EE-flavor)
  * [Manual Testing](#Manual-Testing)
- [Misc](#Misc)
  * [Autoformat Using Black](#Autoformat-Using-Black)
  * [Run Static Checks](#Run-Static-Checks)
  * [Shellcheck](#Shellcheck)

## Full Integration Tests Including Image Upload

## General

Garden Linux supports integration testing on all major cloud platforms (Alicloud, AWS, Azur, GCP). To allow testing even without access to any cloud platform we created an universal `kvm` platform that may run locally and is accessed in the same way via a `ssh client object` as any other cloud platform. Therefore, you do not need to adjust tests to perform local integration tests. All platformes are described in detail below. Beside this, you may also find additional tests that may be used for developing and contributing to fit the Garden Linux style guides.

## Unit Tests

**Corner case**: When it comes to unit testing these tests will be executed in a context of integration tests. This means that a specific platform type (`chroot`) of integration tests is used to perform regular `unit tests`. This is due to the fact that we want to achive a common test platform based on `Pytest` and theses ones should still be executable on any platform without further adjustments. However, these tests are still located in a subfolder (`test`) within the features directory and must be prefixed with `test_`. This means, that any feature may provide a subfolder called `test` including their `unit test(s)`. `Pytest` will automaticly include these files and validate if they need to run (e.g. `cis` tests will only run if the given artifact was built with this feature).

**Location of Unit Tests:**

`features/$FEATUR_NAME/test/test_$TEST_NAME.py`

**Example:**

| Feature | Unit test | Test location |
|---|---|---|
| $FEATURE_NAME | test_$TEST_NAME.py | features/$FEATUR_NAME/test/test_$TEST_NAME.py |
| CIS | test_cis.py | [features/cis/test/test_cis.py](../features/cis/test/test_cis.py) |


## Prerequisites

Build the integration test container with all necessary dependencies. This container image will contain all necessary Python modules as well as the command line utilities by the Cloud providers (i.e. AWS, Azure and GCP) and KVM/QEMU.

    make --directory=docker build-integration-test

The resulting container image will be tagged as `gardenlinux/integration-test:<version>` with `<version>` being the version that is returned by `bin/garden-version` in this repository. All fruther tests run inside this container.

## Examples for Supported Platforms

### General

The integration tests require a config file containing vital information for interacting with the cloud providers. In the following sections, the configuration options are described in general and for each cloud provider individually.

Since the configuration options are provided as a structured YAML with the cloud provider name as root elements, it is possible to have everything in just one file.

### Aliyun

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

    # a valid instance type for the selected region
    instance_type: ecs.t5-lc1m2.large

    # mandatory, the security group id
    security_group_id:  # sg-...

    # mandatory, the vswtich id
    vswitch_id:  # vsw-...

    # mandatory, region and zone
    region_id: eu-central-1
    zone_id: eu-central-1a

    # mandatory: bucket name
    bucket:  # my-test-upload-bucket

    # optional, path in bucket 
    bucket_path: integration-test

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

#### Configuration options

<details>

- **credential_file**: 
- **image_id**:
- **image**:
- **instance_type**: ecs.t5-lc1m2.large
- **security_group_id**:  # sg-...
- **vswitch_id**:  # vsw-...
- **region_id**: eu-central-1
- **zone_id**: eu-central-1a
- **bucket**:  # my-test-upload-bucket
- **bucket_path**: integration-test

- **ssh_key_filepath** _(required)_: The SSH key that will be deployed to the ECS instance and that will be used by the test framework to log on to it. Must be the file containing the private part of an SSH keypair which needs to be generated with `openssh-keygen` beforehand.
- **key_name** _(required)_: The SSH key gets uploaded to ECS, this is the name of the key object resource.
- **passphrase** _(optional)_: If the given SSH key is protected with a passphrase, it needs to be provided here.
- **user** _(required)_: The user that will be provisioned to the ECS instance, which the SSH key gets assigned to and that is used by the test framework to log on the ECS instance.

- **keep_running** _(optional)_: if set to `true`, all tests resources, especially the VM will not get removed after the test (independent of the test result) to allow for debugging

</details>

#### Running the tests

Start docker container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount GCP credentials to `/root/.config`
- mount SSH keys to `/root/.ssh`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with configfile to `/config`

```
docker run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.config:/root/.config -v $HOME/.ssh:/root/.ssh -v ~/config:/config  gardenlinux/integration-test:`bin/garden-version` bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=ali --configfile=/config/mygcpconfig.yaml integration/


### AWS

Notes for AWS credentials:
- credentials must be supplied by having them ready in `~/.aws/config` and `~/.aws/credentials`
- `~/.aws` gets mounted into the container that executes the integration tests

Use the following configuration file:

```yaml
aws:
    # region in which all test resources will be created (required)
    region: eu-central-1
    # machine/instance type of the test VM - not all machines are available in all regions (optional)
    instance_type: t3.micro

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
    # bucket where the image will be uploded to (optional)
    bucket: import-to-ec2-gardenlinux-validation

    # keep instance running after tests finishes (optional)
    keep_running: false
```

#### Configuration options

<details>

- **region** _(required)_: the AWS region in which all test relevant resources will be created 
- **instanc-type** _(optional)_: the instance type that will be used for the EC2 instance used for testing, defaults to `t3.micro` if not specified

- **ssh_key_filepath** _(optional)_: The SSH key that will be deployed to the EC2 instance and that will be used by the test framework to log on to it. Must be the file containing the private part of an SSH keypair which needs to be generated with `openssh-keygen` beforehand. If not provided, a new SSH key with 2048 bits will be generated just for the test.
- **passphrase** _(optional)_: If the given SSH key is protected with a passphrase, it needs to be provided here.
- **key_name** _(optional)_: The SSH key gets uploaded to EC2, this is the name of the key object resource.
- **user** _(optional)_: The user that will be provisioned to the EC2 instance, which the SSH key gets assigned to and that is used by the test framework to log on the EC2 instance. Defaults to `admin`.

- **ami_id** _(optional/alternatively required)_: If the tests should get executed against an already existing AMI, this is its ID. It must exist in the region given above. Either **ami_id** or **image** must be supplied but not both.
- **image** _(optional/alternatively required)_: If the tests should be executed against a Garden Linux filesystem snapshot that resulted from (local) build, this option is the URI that points to it. The file must be of type `.raw`. Either **ami_id** or **image** must be supplied but not both.
The URI can be:
    - `file:/path/to/my/rootfs.raw`: for local files, in that case
    - `s3://mybucketname/objects/objectkey`: for files in S3

- **bucket** _(optional)_: To create an AMI/EC2 instance from a local filesystem snapshot, it needs to be uploaded to an S3 bucket first. The bucket needs to exist in the given region and its name must be provided here. If not provided, a bucket will be created in the given region.

- **keep_running** _(optional)_: if set to `true`, all tests resources, especially the VM will not get removed after the test (independent of the test result) to allow for debugging. Defaults to `False`.

</details>

#### Running the tests

Start docker container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount AWS credential folder (usually `~/.aws`) to `/root/.aws`
- mount SSH keys that are used to log in to the virtual machine to `/root/.ssh`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with configfile to `/config`

```
docker run -it --rm -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.aws:/root/.aws -v $HOME/.ssh:/root/.ssh -v ~/config:/config gardenlinux/integration-test:`bin/garden-version` /bin/bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=aws --configfile=/config/myawsconfig.yaml integration/

### Azure

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
    # resource group if ommitted a new group will be created (optional)
    resource_group: rg-gardenlinux-test-01
    # network security group (optional)
    nsg_name: nsg-gardenlinux-test-42

    # storage account to be used for image upload (optional)
    storage_account_name: stggardenlinuxtest01
    # local image file to be uploaded and to be tested (required/alternatively optional)
    image: file:/build/azure/20210915/amd64/bullseye/rootfs.vhd
    #image: s3://gardenlinux/objects/078f440a76024ccd1679481708ebfc32f5431569
    # already existing image in Azure to be used for testing (required/alternatively optional)
    image_name: <image name>

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

#### Configuration options

Only three parameters are required for the test: the Azure `subscription` or `subscription_id`, the Azure `location` and the image to be tested. All other parameters are optional and can be generated at runtime.

<details>

- **location** _(required)_: the Azure region in which all test relevant resources will be created 
- **subscription** _(required/optional)_: The Azure subscription (as in subscription name) which is used for creating all relevant resources and running the test. Either the subscription name or the `subscription_id` needs to be provided.
- **subscription_id** _(required/optioal)_: The Azure subscription (its ID) which is used for creating all relevant resources and running the test. Either the 'subscription' name or its needs to be provided.
- **resource_group** _(optional)_: all relevant resources for the integration test will be assigned to an Azure resource group. If you want to reuse an existing resource group, you can specify it here. If left empty, a new resource group gets created for the duration of the test.
- **nsg_name** _(optional)_: The integration tests need to create a new network security group, this is its name. If you want to reuse an existing security group, specify its name here. If left empty, a new network security group will be created for the duration of the test.

- **storage_account_name** _(optional)_: the storage account to which the image gets uploaded
- **image_name** _(optional/required)_: If the tests should get executed against an already existing Image, this is its name. Either **image_name** or **image** must be supplied but not both.
- **image** _(optional/required)_: If the tests should be executed against a Garden Linux filesystem snapshot that resulted from a local build, this option is the path that points to it. The file must be of type `.vhd`. The image will be removed from Azure once the test finishes. Either **image_name** or **image** must be supplied but not both.
The URI can be:
    - `file:/path/to/my/rootfs.raw`: for local files
    - `s3://mybucketname/objects/objectkey`: for files in S3

- **ssh_key_filepath** _(optional)_: The SSH key that will be deployed to the Azure instance and that will be used by the test framework to log on to it. Must be the file containing the private part of an SSH keypair which needs to be generated with `openssh-keygen` beforehand. If left empty, a temporary key with 2048 bits will be generated by the test.
- **passphrase** _(optional)_: If the given SSH key is protected with a passphrase, it needs to be provided here.
- **ssh_key_name** _(optional)_: The SSH key gets uploaded to Azure, this is the name of the key object resource.
- **user** _(optional)_: The user that will be provisioned to the Azure instance, which the SSH key gets assigned to and that is used by the test framework to log on the Azure instance. If not provided, the user defaults to `azureuser`.

- **keep_running** _(optional)_: if set to `true`, all tests resources, especially the VM will not get removed after the test (independent of the test result) to allow for debugging

</details>

#### Running the tests

Start docker container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount Azure credentials to `/root/.azure`
- mount SSH keys to `/root/.ssh`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with configfile to `/config`

```
docker run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.azure:/root/.azure -v $HOME/.ssh:/root/.ssh -v ~/config:/config  gardenlinux/integration-test:`bin/garden-version` bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=azure --configfile=/config/myazconfig.yaml integration/


### CHROOT

CHROOT tests are designed to run directly on your platform within a `chroot` environment and boosts up the time for the integration tests that do not need any target platform.

Notes:
 * CHROOT will run inside your `integration-test` Docker container
 * Docker container needs `SYS_ADMIN` capability
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

#### Configuration options

<details>

- **ssh_key_filepath** _(required)_: The SSH key that will be injected to the *chroot* and that will be used by the test framework to log on to it. In default, you do **not** need to provide or mount your real SSH key; a new one will be generated and injected by every new run. However, if you really want, a present one can be defined - take care that this will not be overwritten and set `ssh_key_generate` to false.
- **user** _(required)_: The user that will be used for the connection.
</details>

#### Running the tests

Start docker container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with configfile to `/config`

```
docker run --cap-add SYS_ADMIN --security-opt apparmor=unconfined -it --rm -v `pwd`:/gardenlinux gardenlinux/integration-test:dev /bin/bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=chroot --configfile=/config/mychrootconfig.yaml integration/


### GCP

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

    # use a service account to log on to GCP instead of access token created with gcloud before (optional)
    #service_account_json:
    #service_account_json_path: /root/.config/gcloud/application_default_credentials.json

    # use already existing image in GCE for tests (optional/required)
    #image_name:
    # upload this local image to GCE and use it for testing (optional/required)
    image: file:/build/gcp-dev/20210915/amd64/bullseye/rootfs-gcpimage.tar.gz
    #image: s3://gardenlinux/objects/078f440a76024ccd1679481708ebfc32f5431569
    # GCS bucket for image upload, must exist and be used for local image upload (optional)
    #bucket: 

    # GCE machine type (optional)
    machine_type: n1-standard-2

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

#### Configuration options

<details>

- **project** _(required)_: the GCP project which is used for creating all relevant resources and running the tests
- **zone** _(required)_: the GCP zone in which all test relevant resources will be created 

- **service_account_json_path** _(optional)_: If a service account JSON file is provided, it will be used to authenticate to GCP instead of using an access token.

- **image_name** _(optional/required)_: If the tests should get executed against an already existing Image, this is its name. Either **image_name** or **image** must be supplied but not both.
- **image** _(optional/required)_: If the tests should be executed against a Garden Linux filesystem snapshot that resulted from a local build, this option is the path that points to it. The file must be of type `.tar.gz`. Either **image_name** or **image** must be supplied but not both.
The URI can be:
    - `file:/path/to/my/rootfs.raw`: for local files
    - `s3://mybucketname/objects/objectkey`: for files in S3

- **bucket** _(optional)_: To create a GCE machine image from a local filesystem snapshot, it needs to be uploaded to a GCS bucket first. The will be created on the fly and a name will be generated if this field is left empty.

- **machine_type** _(optional)_: The GCE machine type to be used to create the GCE instance for the test. Defaults to `n1-standard-2` if not given.

- **ssh_key_filepath** _(required)_: The SSH key that will be deployed to the GCE instance and that will be used by the test framework to log on to it. Must be the file containing the private part of an SSH keypair which needs to be generated with `openssh-keygen` beforehand.
- **passphrase** _(optional)_: If the given SSH key is protected with a passphrase, it needs to be provided here.
- **user** _(required)_: The user that will be provisioned to the GCE instance, which the SSH key gets assigned to and that is used by the test framework to log on the Azure instance.

- **keep_running** _(optional)_: if set to `true`, all tests resources, especially the VM will not get removed after the test (independent of the test result) to allow for debugging

</details>

#### Running the tests

Start docker container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount GCP credentials to `/root/.config`
- mount SSH keys to `/root/.ssh`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with configfile to `/config`

```
docker run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.config:/root/.config -v $HOME/.ssh:/root/.ssh -v ~/config:/config  gardenlinux/integration-test:`bin/garden-version` bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=gcp --configfile=/config/mygcpconfig.yaml integration/


### KVM

KVM tests are designed to run directly on your platform. Currently, AMD64 and ARM64 architectures are supported.
Notes:
 * KVM/QEMU will run inside your `integration-test` Docker container
 * (Default) New temporary SSH keys are auto generated and injected
 * (Default: amd64) AMD64 and ARM64 architecutres are supported

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

    # Architecture to boot (optional)
    # Default: amd64
    #arch: arm64

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

#### Configuration options

<details>

- **ssh_key_filepath** _(required)_: The SSH key that will be injected to the .raw image file and that will be used by the test framework to log on to it. In default, you do **not** need to provide or mount your real SSH key; a new one will be generated and injected by every new run. However, if you really want, a present one can be defined - take care that this will not be overwritten and set `ssh_key_generate` to false.
- **passphrase** _(optional)_: If the given SSH key is protected with a passphrase, it needs to be provided here.
- **user** _(required)_: The user that will be used for the connection.
- **keep_running** _(optional)_: If set to `true`, all tests resources, especially the VM will not get removed after the test (independent of the test result) to allow further debugging. Default: `False`.

</details>

#### Running the tests

Start docker container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount /boot and /lib/modules for guestfish support (required for KVM tools)
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with configfile to `/config`
- mount SSH keys that are used to log in to the virtual machine to `/root/.ssh` (Optional: only needed when no SSH keys should be autogenerated)

**With SSH autogeneration**
This is the default and recommended way.
```
docker run -it --rm -v /boot/:/boot -v /lib/modules:/lib/modules -v `pwd`:/gardenlinux gardenlinux/integration-test:dev /bin/bash
```

**Without SSH autogeneration**
Use this only when really needed.
```
docker run -it --rm -v `pwd`:/gardenlinux -v /boot/:/boot -v /lib/modules:/lib/modules -v `pwd`/.build/:/build -v $HOME/.ssh:/root/.ssh -v ~/config:/config gardenlinux/integration-test:`bin/garden-version` /bin/bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=kvm --configfile=/config/mykvmconfig.yaml integration/


### Manual Testing

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

#### Running the tests

Start docker container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount SSH keys to `/root/.ssh`
- mount directory with configfile to `/config`

```
docker run -it --rm  -v `pwd`:/gardenlinux -v $HOME/.ssh:/root/.ssh -v ~/config:/config  gardenlinux/integration-test:`bin/garden-version` bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=manual --configfile=/config/myconfig.yaml integration/


### OpenStack CC EE flavor

Obtain credentials by downloading an OpenStack RC file and source it after adding your password to it. Alternatively you could statically add the password to it (environment variable `OS_PASSWORD`) and specifcy that file in the configuration.

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

#### Configuration options

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

#### Running the tests

Start docker container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount GCP credentials to `/root/.config`
- mount SSH keys to `/root/.ssh`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with configfile to `/config`

```
docker run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.config:/root/.config -v $HOME/.ssh:/root/.ssh -v ~/config:/config  gardenlinux/integration-test:`bin/garden-version` bash
```

Run the tests (be sure you properly mounted the Garden Linux repository to the container and you are in `/gardenlinux/tests`):

    pytest --iaas=openstack-ccee --configfile=/config/mygcpconfig.yaml integration/


## Misc
Within this section further tests are listed that may help developing and contributing on Garden Linux. These tests are disjunct from the Garden Linux code itself and may only perform validation on code (like `Shellcheck` or `autopep`).

### Autoformat Using Black

in order to auto format the source code run

    pipenv run black .

### Run Static Checks

    pipenv run flake8 .

### Shellcheck
Shellcheck is a static analysis tool and allows to analyse and validate given scripts. Tests must be executed explicitly via `pytest shellcheck`. This tool is disjunct from Garden Linux itself and can run on any files within the test container. For more details see Shellcheck [shellcheck/README.md](shellcheck/README.md).

    pytest shellcheck --severity=error