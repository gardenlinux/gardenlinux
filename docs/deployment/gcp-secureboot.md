---
title: Enable secure boot for Garden Linux on GCP
weight: 10
disableToc: false
---

# Enable secure boot for Garden Linux on GCP

This article describes all steps needed to spawn a secure boot enabled Garden Linux image on GCP. Thereby, it uses the integration testing platform for spawning all required GCP resources. For more information about the integration testing platform used for Garden Linux, take a look [here](../../tests/README.md)

## Table of Content

- [Create image](#create-image)
- [Prepare spawning](#prepare-spawning)
  - [UEFI variables](#uefi-variables)
  - [Integration test configuration](#integration-test-configuration)
- [Spawn environment](#spawn-environment)
- [Use secure boot enabled Garden Linux](#use-secure-boot-enabled-garden-linux)
- [Cleanup everything](#cleanup-everything)

## Create image

Before spawning a secure boot enabled Garden Linux instance, we have to create the corresponding artifact for this. In order to create it, you must have the Garden Linux repo checked out and execute the following make target from within the root directory of the repository:

```
make gcp-secureboot-dev
```

For our test, we are creating a dev image, which will give us root access for further testing later on. If your build system doesn't have enough memory to build this image, you can add the following attribute to the `make` command:

```
make gcp-secureboot-dev BUILD_OPTS="--lessram"
```

## Prepare spawning
This chapter describes what steps are required to successfully spawn an GCP instance with Garden Linux running with secure boot.

### UEFI variables

Once you have build a new Garden Linux image using the secure boot feature, there will also be keys and a signature database which are required for secure boot. These keys and signature database must be uploaded to GCP alongside with the image, so that UEFI can verify the integrity of the booted system during the startup process.

The keys and signature database are created in the [cert/](../../cert/) directory during the build of the image. There, you will find the following files:
* secureboot.db.auth
* secureboot.kek.auth
* secureboot.pk.auth

These files are required during startup. Therefore, they must be added to the spawned GCP image. In order to achieve this, the files are added as metadata to the image upload.

### Integration test configuration
Before one can spawn the required GCP environment, a configuration for the integration test platform is needed.

The following example shows such a configuration. For test purposes, it uses the `europe-west1` region and a small instance type.

In general, there is no need to adjust this configuration, if you have created the Garden Linux image as described in this [chapter](#create-image).

However, you may need to adjust the project name matching the name of the project you are planning to use for the integration tests. Also make sure the ssh_key_filepath points to the ssh private key, you want to use to access the running instance with, the SSH public key must be in the same directory and have the same file name as the SSH private key with a `.pub` suffix. Additionally you may need to adjust the path to your image artifact which should look like `gcp-gardener_dev_secureboot-amd64-today-<commit hash|local>.tar.gz`.

```
gcp:
    # project id (required)
    project: sap-cp-k8s-gdnlinux-gcp-test
    # GCP region where the test resources should be created (required)
    region: europe-west1
    # zone where the VM should be created (required)
    zone: europe-west1-d

    # use a service account to log on to GCP instead of access token created with gcloud before (optional)
    #service_account_json:
    #service_account_json_path: /root/.config/gcloud/application_default_credentials.json
    #service_account_json_path: /config/gcloud/sa_credentials.json

    # use already existing image in GCE for tests (optional/required)
    #image_name:
    # upload this local image to GCE and use it for testing (optional/required)
    image: file:/build/gcp-gardener_dev_secureboot-amd64-today-local.tar.gz
    #image: s3://gardenlinux/objects/078f440a76024ccd1679481708ebfc32f5431569
    # region of the S3 bucket from where the image should be downloaded from (optional)
    #image_region: eu-central-1

    # GCS bucket for image upload, must exist and be used for local image upload (optional)
    #bucket:

    # enable uefi boot, default is legacy boot (optional)
    #uefi: false
    # enable secureboot, implies uefi boot, default is off (optional)
    secureboot: true
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
    #test_name: my-gardenlinux-test

    # list of features that is used to determine the tests to run
    #features:
    #  - "base"

    # ssh related configuration for logging in to the VM (required)
    ssh:
        # path to the ssh key file (required)
        ssh_key_filepath: /gardenlinux/config/id_rsa_gardenlinux_test
        # passphrase for a secured SSH key (optional)
        passphrase:
        # username used to connect to the Azure instance (required)
        user: gardenlinux

    # keep instance running after tests finishes (optional)
    keep_running: true

```

The content must be saved into a YAML file and it must be mounted to the integration test container later on. For this, create a folder in your home directory and place the YAML in there. This folder will be mounted to the integration test container then. The configuration could be called `gcp-secureboot.yaml` for example.

## Spawn environment

The environment can now be spawned by using the integration test platform. As described in the corresponding [documentation](../../tests/README.md#prerequisites-1), you must have the integration test container in place.
As described there, the following command is used:

```
make container-integration
```
Alternatively the following command will lead to the same result.
```
make --directory=container build-integration-test
```

Then, make sure you have API access to GCP by having your credentials in your home directory. There should be a file called `~/.config/gcloud/application_default_credentials.json`. If it's not there, you need to login via the following command:
```
gcloud auth application-default login
```

After that, the integration test container can be started like this. Make sure that you are in the Garden Linux repo while executing this command.
```
sudo podman run -it --rm  -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.config:/root/.config -v $HOME/.ssh:/root/.ssh -v ~/config:/config  gardenlinux/integration-test:`bin/garden-version` bash
```

As you can see, the current Garden Linux repo is mounted into the container (`/gardenlinux`). Moreover, it also gets access to the GCP credentials, the SSH directory and the previously created configuration (`~/config`).

Once you executed the command, you should have access to the bash terminal within the container. From there, you can execute the integration test, which will create all required GCP resources for you. Since we've set the `keep_running` parameter to `true`, the created resources will remain after the execution, so that we can access the instance via SSH for further testing afterwards.

```
pytest --iaas=gcp --configfile=/config/gcp-secureboot.yaml
```

## Use secure boot enabled Garden Linux

After you have run the integration test from the previous chapter, you should still have the bash terminal open within the integration test container.

From there, you can now use `ssh` to connect to the remote GCP instance running Garden Linux with secure boot enabled. Use the SSH private key you configured in the configuration yaml file.

Additionally, the output also contains which address can be used to access the remote machine:
```
INFO     gcp-testbed:gcp.py:461 Waiting for 34.76.177.199 to respond...
INFO     gcp-testbed:gcp.py:465 Instance 34.76.177.199 is reachable...
```

The instance is running with the so called `gardenlinux` user, so you can access this machine by the following command:
```
ssh -o userknownhostsfile=7/dev/null -o stricthostkeychecking=no -i /gardenlinux/config/id_rsa_gardenlinux_test gardenlinux@34.76.177.199
```

Now, you are connected to the Garden Linux instance. In order to check if the instance is started with secure boot, you can use the following command:

```
$ sudo bootctl
systemd-boot not installed in ESP.
System:
     Firmware: UEFI 2.70 (EDK II 1.00)
  Secure Boot: enabled (user)
 TPM2 Support: yes
 Boot into FW: supported
...
```

## Cleanup everything

Since the we set `keep_running` in the configuration yaml to `true` the resources are not deleted automatically after the tests finished. Therefore the script `clean_orphans_gcp.py` exists to help remove the resources spawned by the integration tests. Within the integration-test container, execute the following command. The integration container can be started as stated in the [Running the tests](../../tests/README.md#running-the-tests) documentation of GCP within the `tests/` directory or in the previous chapter [Spawn environment](#spawn-environment).
```
/gardenlinux/tests/tools/clean_orphans_gcp.py
```

This command is an interactive tool for cleaning up your GCP environment. Thereby, it will only focus on resources which have been created by the integration test scripts before. This is achieved by using corresponding tags. 
Once executed, the `clean_orphans_gcp.py` script will ask for the following resources:
* Instances
* Subnetworks
* Networks
* Images
* Buckets

Each resource and the removal of it will only be executed by pressing the `y` button into the prompt. You can also skip some of the resources by pressing `N`.

Since an environment can also run other integration test resources which may not be removed, you can identify each resource by corresponding tags and a created UUID for each test run. At the beginning of the integration test for example, the integration test prints the information about the used UUID which can then be used for identifying the proper GCP resources easily:

```
INFO     gcp-testbed:gcp.py:204 This test's tags are:
INFO     gcp-testbed:gcp.py:206         component: gardenlinux
INFO     gcp-testbed:gcp.py:206         test-type: integration-test
INFO     gcp-testbed:gcp.py:206         test-name: gl-test-20221130100632
INFO     gcp-testbed:gcp.py:206         test-uuid: dc183e89-8f9e-454f-a080-80831d833f05
```
The `clean_orphans_gcp.py` script will always print the tags of GCP resources as well once it ask you to remove them, so it should be possible to identify the correct resources and skip them if they do not belong to the integration test of this documentation.