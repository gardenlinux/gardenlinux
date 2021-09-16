# Tests


## 1. Full Integration Tests Including Image Upload

## 1.1 Prerequisites

Build the integration test container with all necessary dependencies

```
make docker
```

## 2. Tests by Cloud Provider

### 2.1 AWS

Notes for AWS credentials:
- or credentials can be supplied in ~/.aws/config and ~/.aws/credentials

Use the following configuration file:

```
aws:
    # region where the VM will be created (required)
    region: eu-central-1
    # If specified this AMI will be used (no image upload)
    #ami_id: ami-xxx
    # user and ssh key used to connect to the ec2 instance
    user: admin
    # path to the ssh key file
    ssh_key_filepath: ~/.ssh/id_rsa_gardenlinux_test
    # ssh key passphrase if configured
    passphrase:
    # name of the public ssh key object as it gets imported into AWS
    key_name: gardenlinux-test-2
    remote_path: /
    # not all machines are available in all regions
    instance_type: t3.micro
    # bucket where the image will be uploded to
    bucket: import-to-ec2-gardenlinux-validation
    # image file (if provided locally)
    image: file:/build/aws/20210714/amd64/bullseye/rootfs.raw
    # image file (if provided from S3)
    #image: s3://gardenlinux/objects/078f440a76024ccd1679481708ebfc32f5431569
```

Start docker container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount AWS credentials to `/root/.aws`
- mount SSH keys to `/root/.ssh`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with configfile to `/config`

```
docker run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.aws:/root/.aws -v $HOME/.ssh:/root/.ssh -v ~/config:/config  gardenlinux/integration-test:`bin/garden-version` bash
```

Run the tests:

```
pipenv install --dev
pipenv run pytest --iaas=aws --configfile=/config/myawsconfig.yaml integration/
```

### 2.2 Azure

Login using the following command

```
az login
```

Note: ohter means of authentiacation, e.g. usage of service accounts should be possible.

Use the following test configuration:

```
azure:
    location:
    subscription: <subscription>
    # resource group. if ommitted a new group will be created for the 
    # duration of this test
    resource_group: <resource group>
    passphrase: <passphrese if configured>
    storage_account-name: <storage account name>
    image_name: <image name>
    # specify image file in case an image needs to be uploaded for the test
    # the image will be removed after the test
    image: <path to image file>
    ssh_key_filepath: <private ssh key>
    ssh_key_name: <name of key>
    nsg_name: <network security group>
    user: "azureuser"
    remote_path:
```

Start docker container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount Azure credentials to `/root/.azure`
- mount SSH keys to `/root/.ssh`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with configfile to `/config`

```
docker run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.azure:/root/.azure -v $HOME/.ssh:/root/.ssh -v ~/config:/config  gardenlinux/integration-test:`bin/garden-version` bash
```

Run the tests:

```
pipenv install --dev
pipenv run pytest --iaas=azure --configfile=/config/myawsconfig.yaml integration/
```

#### 2.3 GCP

Obtain credentials using the following command:

```
gcloud auth application-default login
```

Use the following test configuration:

```
gcp:
    # project id (required)
    project:
    # Zone where the VM should be created (required)
    zone: europe-west1-d

    #service_account_json:
    #service_account_json_path: /root/.config/gcloud/application_default_credentials.json

    # Optional image name: if specified an existing image will be used
    # if there is no image with that name the image specified in image 
    # will be used
    image_name:

    # Optional image file: if specified image will be uploaded and used
    # for the test
    image: /build/gcp-dev/20210915/amd64/bullseye/rootfs-gcpimage.tar.gz

    # the bucket must exist in the specififed project
    bucket:

    # machine type (required)
    machine_type: n1-standard-1
    # user and ssh key used to connect to the vm
    user: gardenlinux
    ssh_key_filepath: /root/.ssh/id_rsa_gardenlinux_test
    passphrase:
    remote_path: /

    # Define if all resources should be kept after the test
    #keep_running: true
```

Start docker container with dependencies:

- mount Garden Linux repository to `/gardenlinux`
- mount GCP credentials to `/root/.config`
- mount SSH keys to `/root/.ssh`
- mount build result directory to `/build` (if not part of the Garden Linux file tree)
- mount directory with configfile to `/config`

```
docker run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.config:/root/.config -v $HOME/.ssh:/root/.ssh -v ~/config:/config  gardenlinux/integration-test:`bin/garden-version` bash
```

Run the tests:

```
pipenv install --dev
pipenv run pytest --iaas=gcp --configfile=/config/myawsconfig.yaml integration/
```

## 3. Misc

### auto-format using black

in order to auto format the source code run

```
pipenv run black .
```

### run static checks

```
pipenv run flake8 .
```
