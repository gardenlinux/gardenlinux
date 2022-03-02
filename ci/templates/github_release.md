# Garden Linux Release $version

## New in this release
$features

For a detailed list of packages see attached component-descriptor.

## Public images on cloud platforms

### Alibaba Cloud (AMD64)

```
$ali_ids
```

###  Amazon Web Services (AMD64)

```
$aws_ids
```

### Google Cloud Platform (AMD64)

All regions:

```
gcp_image_name: $gcp_id
```

### Microsoft Azure (AMD64)

All regions:

```
urn: $azure_id
```

## Pre-built images available for downloads

### Alibaba Cloud (AMD64)
* [$ali_name]($ali_url)

###  Amazon Web Services (AMD64)
* [$aws_name]($aws_url)

### Google Cloud Platform (AMD64)
* [$gcp_name]($gcp_url)

### Microsoft Azure (AMD64)
* [$azure_name]($azure_url)

### Openstack CCEE (AMD64, VMware as Hypervisor)
* [$openstack_name]($openstack_url)

### VMware vSphere (AMD64)
* [$vsphere_name]($vsphere_url)

<details>

## How to import images to public Cloud Providers

- Alibaba Cloud
    - [Import custom images](https://www.alibabacloud.com/help/doc-detail/25464.htm) to Alibaba Cloud

- AWS
    - [Importing an Image into Your Device as an Amazon EC2 AMI](https://docs.aws.amazon.com/snowball/latest/developer-guide/ec2-ami-import-cli.html)
    - recommended `aws` command with parameters:
      ```shell
      aws ec2 register-image --name gardenlinux --description "Garden Linux" --architecture x86_64 --root-device-name /dev/xvda --virtualization-type hvm --ena-support --block-device-mapping "DeviceName=/dev/xvda,Ebs={DeleteOnTermination=True,SnapshotId=<your snapshot ID from snapshot import>,VolumeType=gp2}"
      ```

- Google Cloud Platform
    - [Importing a bootable virtual disk](https://cloud.google.com/compute/docs/import/importing-virtual-disks#bootable) to GCP

- Microsoft Azure
    - [Bringing and creating Linux images in Azure](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/imaging)

</details>
