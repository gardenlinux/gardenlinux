---
title: Enable secure boot for Garden Linux on AWS
weight: 10
disableToc: false
---

# Enable secure boot for Garden Linux on AWS

This article describes all steps needed to spawn a secure enabled Garden Linux image on AWS. Thereby, it uses the integration testing platform for spawning all required AWS resources. For more information about the integration testing platform used for Garden Linux, take a look [here](../../tests/README.md)

## Table of Content

- [Create image](#create-image)
- [Prepare spawning](#prepare-spawning)
  - [Option A: Enable secure boot internally](#option-a-enable-secure-boot-internally)
    - [Integration test configuration](#integration-test-configuration)
  - [Option B: Enable secure boot externally](#option-b-enable-secure-boot-externally)
    - [UEFI variables](#uefi-variables)
    - [Integration test configuration](#integration-test-configuration-1)
- [Spawn environment](#spawn-environment)
- [Use secure boot enabled Garden Linux](#use-secure-boot-enabled-garden-linux)
- [Cleanup everything](#cleanup-everything)

## Create image

Before spawning a secure boot enabled Garden Linux instance, we have to create the corresponding artifact for this. In order to create it, you must have the Garden Linux repo checked out and execute the following make target from within the root directory of the repository:

```
make aws-secureboot-dev
```

For our test, we are creating a dev image, which will give us root access for further testing later on. If your build system doesn't have enough memory to build this image, you can add the following attribute to the `make` command:

```
make aws-secureboot-dev BUILD_OPTS="--lessram"
```

## Prepare spawning
This chapter describes what steps are required to successfully spawn an AWS instance with Garden Linux running with secure boot. There are two options to choose from.

You can either enable secure boot internally. This way you simply need to spawn the Garden Linux image and execute the `enroll-gardenlinux-secureboot-keys`, which will prepare the Garden Linux image for secure boot by using UEFI's setup mode. Ensure to reboot the system to have secure boot fully enabled.

Besides of this, you can also enable secure boot externally. This way, you have secure boot enabled right at the first start, but you need to provide all information during the creation of the instances, which also requires some additional tools to be executed on your workstation.

### Option A: Enable secure boot internally

By creating a Garden Linux with the secure boot feature enabled and by using UEFI's setup mode, you can activate secure boot from within the AWS instance once the Garden Linux image has been spawned successfully. As long as you do not enable secure boot within the instance, the Garden Linux image will simply spawn without secure boot enabled. This must be kept in mind.

#### Integration test configuration
Before starting the required AWS environment, a configuration for the integration test platform is needed.

The following example shows such a configuration. For test purposes, it uses the `eu-west-1` region, a small instance type (e.g. `t3.micro`), an image with `amd64` architecture and most importantly the `UEFI` boot mode.

Generally, there is no need to adjust this configuration, if you have created the Garden Linux image as described in this [chapter](#create-image).

However, you may need to adjust the path to your image artifact which could look like `aws-gardener_secureboot_dev-amd64-today-<commit hash|local>.raw`.

The configuration looks like this then:
```
aws:
    # region
    region: eu-west-1
    # machine/instance type of the test VM - not all machines are available in all regions (optional)
    instance_type: t3.micro
    # architecture of the image and VM to be used (optional)
    architecture: amd64
    # boot mode
    boot_mode: uefi
    # UEFI data. This contains the UEFI variables
    uefi_data: <content of secure_boot_blob.bin>

    # local/S3 image file to be uploaded for the test (optional/alternatively required)
    image: file:/build/aws-gardener_secureboot_dev-amd64-today-local.raw

    # keep instance running after tests finishes (optional)
    keep_running: true

```

Finally, the content must be saved into a YAML file and it has to be mounted to the integration test container later on. For this case, create a folder in your home directory and place the YAML in there. This folder will be mounted to the integration test container afterwards. The configuration could be called `aws-secureboot.yaml` for example.


#### Enroll signature databases

Once the image has been started as described in chapter [Spawn image](#spawn-environment) and you are connected via SSH as described [here](#use-secure-boot-enabled-garden-linux), you need to enroll the signature databases to the UEFI variables. This works because the UEFI is in setup mode on AWS by default. As soon as the signature databases got uploaded, the setup mode will be exited.

For enrolling the signature databases, simply run the following command:
```
sudo /usr/sbin/enroll-gardenlinux-secureboot-keys
```

The signature databases are located in the `/etc/gardenlinux` directory and are uploaded from there to the UEFI variables. Now, the environment is ready to run secure boot. For this, simply reboot the instance. After that, secure boot should be enabled.


### Option B: Enable secure boot externally

Instead of enabling secure boot internally, you can also enable it externally. This is achieved by already providing the required information during the creation and spawning of the image.

The following chapters explain, what needs to be done.

#### UEFI variables

As soon as you have build a new Garden Linux image using the secure boot feature, there will also be signature databases which are required for secure boot. These databases must be uploaded to AWS as UEFI vars, so that UEFI can verify the integrity of the booted system during the startup process.

The signature databases are created in the [cert/](../../cert/) directory during the build of the image. There, you will find the following files:
* secureboot.db.esl
* secureboot.kek.esl
* secureboot.pk.esl

These files are required during startup. Therefore, they must be added to the spawned AWS instance as UEFI variables. In order to achieve this, Amazon provides a tool for creating a file blob. This file blob can be added to the spawning AWS instance since it contains the signature databases. This blob is then used as UEFI variables during boot, so that UEFI can verify the booted system.

The corresponding tool can be found here:
* https://github.com/awslabs/python-uefivars

Simply checkout the git repository and execute the `uefivars.py` script within the repo. If you run this command on Debian bullseye, make sure to install the `crc32c` python module. Unfortunately, there is no debian package for `crc32c` at the moment, but you can install it via `pip` for example.

Once downloaded, the signature databases must be converted to the secure boot file blob:
```
./uefivars.py \
  -i none \
  -o aws \
  -O secure_boot_blob.bin \
  -P cert/secureboot.pk.esl \
  -K cert/secureboot.kek.esl \
  --db cert/secureboot.pk.esl
```
If the execution was successful, there should be a file called `secure_boot_blob.bin`. The content of the file can now be added to the created AWS instance. Since this documentation uses the integration test platform for spawning all required AWS resources and the integration test platform uses its own configuration, the content of the created file must be added to the integration test configuration. The configuration and its required values are described in the next chapter.

#### Integration test configuration

Similar to the configuration and explanation of chapter [Integration test configuration](#integration-test-configuration) from the previous option, you can use the same configuration from there also for this option, but it must be adjusted slightly to provide the UEFI variables that have been prepared previously.

This way, you ensure that the Garden Linux instance will start with secure boot right from the beginning. No further tasks are then needed.

The integration test configuration needs the following additional attribute configured:
```
aws:
    ...
    # UEFI data. This contains the UEFI variables
    uefi_data: <content of secure_boot_blob.bin>
    ...
```

As you can see, it has the `uefi_data` attribute set, which contains the content of the `secure_boot_blob.bin` file.

## Spawn environment

The environment can now be spawned by using the integration test platform. As described in the corresponding [documentation](../../tests/README.md#prerequisites-1), you must have the integration test container in place.
As described there, the following command is used:

```
make --directory=container build-integration-test
```

Then, make sure you have API access to AWS by having your credentials in your home directory. There should be a file called `~/.aws/credentials`. If it's not there, you need to login via the following command:
```
aws configure
```

After that, the integration test container can be started like this. Make sure that you are in the Garden Linux repo while executing this command.
```
sudo podman run -it --rm -v `pwd`:/gardenlinux -v `pwd`/.build/:/build -v $HOME/.aws:/root/.aws -v $HOME/.ssh:/root/.ssh -v ~/config:/config gardenlinux/integration-test:`bin/garden-version` /bin/bash
```

As you can see, the current Garden Linux repo is mounted into the container (`/gardenlinux`). Moreover, it also gets access to the AWS credentials, the SSH directory and the previously created configuration (`~/config`).

Once you executed the command, you should have access to the bash terminal within the container. From there, you can execute the integration test, which will create all required AWS resources for you. Since we've set the `keep_running` parameter to `true`, the created resources will remain after the execution, so that we can access the instance via SSH for further testing afterwards.

```
pytest --iaas=aws --configfile=/config/aws-secureboot.yaml
```

## Use secure boot enabled Garden Linux

After you have run the integration test from the previous chapter, you should still have the bash terminal open within the integration test container.

From there, you can now use `ssh` to connect to the remote AWS instance running Garden Linux with secure boot enabled. The SSH key can be found in the `/tmp` directory of the integration test container. 

During integration test (right at the beginning), the output shows the location of the used SSH key:

```
INFO     helper.sshclient:sshclient.py:47 generated RSA key pair: /tmp/sshkey-gl-test-20221123084607-c6hhy6_k.key
```

Additionally, the output also contains which address can be used to access the remote machine:
```
INFO     aws-testbed:aws.py:634 Ec2 instance is accessible through ec2-54-246-161-244.eu-west-1.compute.amazonaws.com
```

The instances is running with the so called `admin` user, so you can access this machine by the following command:
```
ssh -i /tmp/sshkey-gl-test-20221123084607-c6hhy6_k.key admin@ec2-54-246-161-244.eu-west-1.compute.amazonaws.com
```

Now, you are connected to the Garden Linux instance. In order to check if the instance is started with secure boot, you can use the following command:

```
$ journalctl | grep -i "Secure Boot"
Nov 23 08:52:37 localhost kernel: Kernel is locked down from EFI Secure Boot; see man kernel_lockdown.7
Nov 23 08:52:37 localhost kernel: secureboot: Secure boot enabled
```

Typically, you could also use the `mokutil` tool but it is not installed by default. If it would be installed, you could run it like this:

```
mokutil --sb-state
```

If the output shows `SecureBoot enabled.`, the Garden Linux instance has successfully been started with secure boot enabled.

## Cleanup everything

Within the integration-test container, execute the following command. The integration container can be started as stated in the [Running the tests](../../tests/README.md#running-the-tests) documentation of AWS within the `tests/` directory or in the previous chapter [Spawn environment](#spawn-environment).
```
/gardenlinux/tests/tools/clean_orphans_aws.py
```


This command is an interactive tool for cleaning up your AWS environment. Thereby, it will only focus on resources which have been created by the integration test scripts before. This is achieved by using corresponding tags. 
Once executed, the `clean_orphans_aws.py` script will ask for the following resources:
* EC2 Instances
* Security Groups
* Images/AMIs
* Snapshots
* SSH Key Pairs
* S3 Buckets

Each resource and the removal of it will only be executed by pressing the `y` button into the prompt. You can also skip some of the resources by pressing `N`.

Since an environment can also run other integration test resources which may not be removed, you can identify each resource by corresponding tags and a created UUID for each test run. At the beginning of the integration test for example, the integration test prints the information about the used UUID which can then be used for identifying the proper AWS resources easily:

```
INFO     aws-testbed:aws.py:426 This test's tags are:
INFO     aws-testbed:aws.py:428 	component: gardenlinux
INFO     aws-testbed:aws.py:428 	test-type: integration-test
INFO     aws-testbed:aws.py:428 	test-name: gl-test-20221123084607
INFO     aws-testbed:aws.py:428 	test-uuid: cc250a12-48d5-46e4-a1e7-a01fe74d837b
```
The `clean_orphans_aws.py` script will always print the tags of AWS resources as well once it ask you to remove them, so it should be possible to identify the correct resources and skip them if they do not belong to the integration test of this documentation.