---
title: Releases
weight: 10
disableToc: false
---


<p align="center">
  <img
     src="https://raw.githubusercontent.com/gardenlinux/gardenlinux/main/logo/gardenlinux.svg"
     width="380"
  />
  <h1 align="center">Garden Linux Releases</h1>
 </a>
</p>

Garden Linux frequently publishes snapshot releases. We distinguish between stable releases, (i.e. those that are productively used on Gardener nodes) and development releases.

The most recent stable release is Garden Linux **318.8** (git commit id `ae20c2`).

# Stable released images for Cloud providers

Garden Linux is meant to be used as an operating system for Kubernetes nodes in hyperscalers or on physical hardware. Therefore, we publish machine images in most common cloud providers.

If you want to use Gardenlinux, you can reference these image IDs for your VMs in your very own Hyperscaler account.

## Amazon Web Services (AWS)

The following AMIs are the IDs for the latest stable Garden Linux in the different AWS regions.

```
eu-north-1:      ami-077967ddf49bd7822

eu-west-1:       ami-032de7308a9eb91f5
eu-west-2:       ami-0774a6896e4ac35e0
eu-west-3:       ami-00e17f38ab1ba55f4

eu-central-1:    ami-0b8eda557039b448e

ap-northeast-1:  ami-06a5e5183080d4345
ap-northeast-2:  ami-0fc6badc68b7b7dd1
ap-northeast-3:  ami-08e8b1a5ad052751f

ap-southeast-2:  ami-0ef9fbc659adf4a7e

ap-south-1:      ami-07f7b310124c898e1

ap-southeast-1:  ami-041d6354bb257235d

sa-east-1:       ami-0f4797d1ea0ffbe21

ca-central-1:    ami-0320e4ff5c5004a6b

us-west-1:       ami-088a63ebb9b6d8cca
us-west-2:       ami-0d3df510f088f6728

us-east-1:       ami-066eb78156cb8e30d
us-east-2:       ami-08782642e97383550
```

## Google Cloud Platform (GCP)

The latest stable Garden Linux image can be imported from the Garden Linux project.

```
projects/sap-se-gcp-gardenlinux/global/images/gardenlinux-gcp-cloud-gardener--prod-318-8-ae20c2
```

## Microsoft Azure (AZ)

The latest stable Garden Linux image can be imported from Azures image gallery.

```
urn: sap:gardenlinux:greatest:318.8.0
```

## Alibaba Cloud (alicloud)

The following are the IDs for the latest stable Garden Linux in the different alicloud regions.

```
cn-qingdao:      m-m5e4bbykekw4jyzitkj7
cn-beijing:      m-2zeia89omtfuowhzcmu6
cn-zhangjiakou:  m-8vb5unnrvye3l3k3gref
cn-huhehaote:    m-hp3docfc73wgmm7j0f3g
cn-wulanchabu:   m-0jl4okik565abn4sz8l8
cn-hangzhou:     m-bp129akowq2am8h1u0fr
cn-shanghai:     m-uf691pfb96718f40aena
cn-shenzhen:     m-wz91ua0udzuen8me2rhf
cn-heyuan:       m-f8zhse4877n7h9x9waoh
cn-guangzhou:    m-7xvgjgqjgq2moddcesjb
cn-chengdu:      m-2vc96g79oqz18eqhxd0v
cn-hongkong:     m-j6c743x19ja5l1j7y7n2
cn-nanjing:      m-gc71h59vd9y2eicp9luk

ap-northeast-1:  m-6we3z438cvtssrt3yhrk
ap-southeast-1:  m-t4nbth26nl1qlpupp8o8
ap-southeast-2:  m-p0wiyb4e6zgatd43sfcs
ap-southeast-3:  m-8pshj658blzktp97hibd
ap-southeast-5:  m-k1ado3yv9l6t84rkol46
ap-south-1:      m-a2d0y16ulm5ulnu2as00

us-east-1:       m-0xi73usy5pvepdypf77e
us-west-1:       m-rj95wblp6iefx2fgmgd7

eu-west-1:       m-d7o5bu6xdirbtcweapdp
eu-central-1:    m-gw8iwwd4iiln01dj646s

me-east-1:       m-eb3bjhkkxn3wuw4jgeqc
```


# Stable released snapshots

If you want to import Garden Linux to your hyperscaler account yourself, you can download the filesystem snapshots and follow the import guidelines by the resepctive cloud provider.

AWS:
- [download .raw](https://gardenlinux.s3.eu-central-1.amazonaws.com/objects/2149b22bd7b3f2b76b9cb14ba24f205ee132f1a3)
- Documentation: [Importing an Image into Your Device as an Amazon EC2 AMI](https://docs.aws.amazon.com/snowball/latest/developer-guide/ec2-ami-import-cli.html)

- recommended `aws` command with parameters:
  ```shell
  aws ec2 register-image --name gardenlinux --description "Garden Linux" --architecture x86_64 --root-device-name /dev/xvda --virtualization-type hvm --ena-support --block-device-mapping "DeviceName=/dev/xvda,Ebs={DeleteOnTermination=True,SnapshotId=<your snapshot ID from snapshot import>,VolumeType=gp2}"
  ```

Azure:
- [download .VHD](https://gardenlinux.s3.eu-central-1.amazonaws.com/objects/5b0c9e7d9941a263eb9a99216e893884d5ff44a0)
- Documentation: [Bringing and creating Linux images in Azure](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/imaging)

GCP:
- [download .tar.gz](https://gardenlinux.s3.eu-central-1.amazonaws.com/objects/89ceffabfc55de95dd6f00587e16d344ad251cca)
- Documentation: [Importing a bootable virtual disk](https://cloud.google.com/compute/docs/import/importing-virtual-disks#bootable) to GCP

AliCloud:
- [download .qcow2](https://gardenlinux.s3.eu-central-1.amazonaws.com/objects/cfc4233144437b2582b7053a423f7786f45ee188)
- Documentation: [Import custom images](https://www.alibabacloud.com/help/doc-detail/25464.htm)

VMware:
- [download .OVA](https://gardenlinux.s3.eu-central-1.amazonaws.com/objects/726ce0b438062dd48373e269c5588eb9ba9eb42c)


# Development releases

Development releases will be added at a later point in time.
