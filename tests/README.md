# Tests


## Full Integration Test Including Image Upload

1. Write a configuration file

Notes for AWS credentials:
- credentials must be supplied either in the test configuration file itself (keys `access_key_id`, `secret_access_key` and `region`)
- or credentials can be supplied in ~/.aws/config and ~/.aws/credentials

```
aws:
    region: eu-central-1
    # the AWS access key
    #access_key_id: xxx
    # the AWS secret access key
    #secret_access_key: xxx
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

2. Build the integration test container with all necessary dependencies

```
make docker
```

3. Start docker container with dependencies:
- mount Garden Linux repository to /gardenlinux
- mount AWS credentials to /root/.aws
- mount SSH keys to /root/.ssh
- mount build result directory to /build (if not part of the Garden Linux file tree)

```
docker run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.aws:/root/.aws -v $HOME/.ssh:/root/.ssh  gardenlinux/integration-test:`bin/garden-version` bash
```

**NOTE**: You need to extend the PYTHONPATH in your container to include the directory `ci` of the gardenlinux repository, i.e. `/gardenlinux/ci` in the above example.

3. Set up dependencies

```
pipenv install --dev
pipenv shell
```

3.1 Run single tests

3.1.1 Azure

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


Start container with 
```
docker run -it -v ~/src/gardenlinux:/gardenlinux -v ~/.azure:/root/.azure -v ~/tmp:/tmp -v ~/.ssh:/root/.ssh gardenlinux/integration-test:517.0 bash
```

Initialize environment

```
export PYTHONPATH=/gardenlinux/bin:/gardenlinux/ci
pipenv install --dev
pipenv shell
```

Run test:

```
pytest --configfile=/tmp/test_config.yaml --iaas azure integration/
```

4. Run tests

```
./run_full_test.py --debug --iaas aws --config /tmp/tmp_test_config.yaml

```

## Prerequisites

Python 3.8

to install on debian buster:
```
apt-get update && apt install python3 -t bullseye
```

install pipenv and install dependencies:
```
apt-get update && apt-get install pipenv
pipenv install --dev
```

## auto-format using black

in order to auto format the source code run

```
pipenv run black .
```

## run static checks

```
pipenv run flake8 .
```

## Run tests

on GCP:

```
pipenv run pytest --iaas gcp integration/
```

on AWS:

```
pipenv run pytest --iaas aws integration/
```

The test configuration is read from `test_config.yaml`


