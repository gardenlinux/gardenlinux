## Feature: _oras

### Description
<website-feature>
This flag feature shows how to push to an OCI compatible registry image using [oras](https://oras.land). It is only for demonstration and does *not* alter the contents or results of a built artifacts.
</website-feature>


### Usage

``` shell
$ ./build.sh --features kvm,_oras .build/
```

The output of the build process shows the oras command to push the artifacts in the way they can be consumed by a `onmetal` image.

### Details

#### Building onmetal-image compatible images with oras

> This description show how to create an [onmetal-image](https://github.com/onmetal/onmetal-image) compatible image with [oras](https://oras.land/).

onmetal-image uses specific _mediaTypes_ while creating a bundeled image and it also puts a configured _kernel command line_ into the config layer of the image manifest.

Each comparable section shows the _original_  usage / output of onmetal-image followed by the corresponding commands for oras.

For pushing/pulling of images (and artifacts) an OCI compatible registry must be used.


#### Investigating an image build with onmetal-image

#####  onmetal-image

```sh
$ /config/onmetal-image --store-path /git/.build/onmetal inspect localhost:5000/gardenlinux:latest
{
  "descriptor": {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "digest": "sha256:e2887cc93eaad65be23b5d9631342b904d46c4d2d8b9138bce384decda743ca5",
    "size": 713,
    "annotations": {
      "org.opencontainers.image.ref.name": "localhost:5000/gardenlinux:latest"
    }
  },
  "manifest": {
    "schemaVersion": 2,
    "config": {
      "mediaType": "application/vnd.onmetal.image.config.v1alpha1+json",
      "digest": "sha256:9074eb95a07ed98222ffc0c94a3e6577b972ce62073fe4d14c32d005700f1aba",
      "size": 209
    },
    "layers": [
      {
        "mediaType": "application/vnd.onmetal.image.rootfs.v1alpha1.rootfs",
        "digest": "sha256:89c372adab112641ca4b554cb458bb1ea3f9be02d13b48d8e53178c9f19b858d",
        "size": 721420288
      },
      {
        "mediaType": "application/vnd.onmetal.image.initramfs.v1alpha1.initramfs",
        "digest": "sha256:a45c40c17c93fb1cb1275126f82bc5383a3f53fb7bf42e7d335deb263eab3e8b",
        "size": 27363208
      },
      {
        "mediaType": "application/vnd.onmetal.image.vmlinuz.v1alpha1.vmlinuz",
        "digest": "sha256:046ff03c1918ef70f7526d4820b66ac04b06415a5f0d5153d5f08d1b45dc87ca",
        "size": 13230144
      }
    ]
  },
  "config": {
    "commandLine": "root=LABEL=ROOT ro console=tty0 console=ttyS0,115200 earlyprintk=ttyS0,115200 consoleblank=0 cgroup_enable=memory swapaccount=1 ignition.firstboot=1 ignition.platform.id=qemu security=selinux"
  }
}
```

##### oras

Different to onmetal-image's output, oras does not extract the config -> commandLine. For this it is neccessary to request it's contents when using oras with an additonal query (in this example shown by using _curl_):

```sh
$ /config/oras manifest fetch localhost:5000/gardenlinux@latest | jq '.'
{
  "schemaVersion": 2,
  "config": {
    "mediaType": "application/vnd.onmetal.image.config.v1alpha1+json",
    "digest": "sha256:9074eb95a07ed98222ffc0c94a3e6577b972ce62073fe4d14c32d005700f1aba",
    "size": 209
  },
  "layers": [
    {
      "mediaType": "application/vnd.onmetal.image.rootfs.v1alpha1.rootfs",
      "digest": "sha256:89c372adab112641ca4b554cb458bb1ea3f9be02d13b48d8e53178c9f19b858d",
      "size": 721420288
    },
    {
      "mediaType": "application/vnd.onmetal.image.initramfs.v1alpha1.initramfs",
      "digest": "sha256:a45c40c17c93fb1cb1275126f82bc5383a3f53fb7bf42e7d335deb263eab3e8b",
      "size": 27363208
    },
    {
      "mediaType": "application/vnd.onmetal.image.vmlinuz.v1alpha1.vmlinuz",
      "digest": "sha256:046ff03c1918ef70f7526d4820b66ac04b06415a5f0d5153d5f08d1b45dc87ca",
      "size": 13230144
    }
  ]
}
```

To grab the contents of the kernel command line (only config entry):

```sh
$ curl -s -L http://localhost:5000/v2/gardenlinux/blobs/sha256:9074eb95a07ed98222ffc0c94a3e6577b972ce62073fe4d14c32d005700f1aba | jq '.'
{
  "commandLine": "root=LABEL=ROOT ro console=tty0 console=ttyS0,115200 earlyprintk=ttyS0,115200 consoleblank=0 cgroup_enable=memory swapaccount=1 ignition.firstboot=1 ignition.platform.id=qemu security=selinux"
}
```

An alternative way is to use oras:

```sh
$ /config/oras manifest fetch-config localhost:5000/oras-gardenlinux:v3
{
	"commandLine": "root=LABEL=ROOT ro console=tty0 console=ttyS0,115200 earlyprintk=ttyS0,115200 consoleblank=0 cgroup_enable=memory swapaccount=1 ignition.firstboot=1 ignition.platform.id=qemu security=selinux"
}
```


#### Create an onmetal-image compatible manifest using oras

##### Kernel command line

must be supplied via an own json-file _orasconfig.json_ in the following examples:

```sh
$ jq '.' orasconfig.json
{
	"commandLine": "root=LABEL=ROOT ro console=tty0 console=ttyS0,115200 earlyprintk=ttyS0,115200 consoleblank=0 cgroup_enable=memory swapaccount=1 ignition.firstboot=1 ignition.platform.id=qemu security=selinux"
}
```

Just like that we can easily put additional fields into this config snippet:

```sh
jq . orasconfig.json
{
  "commandLine": "root=LABEL=ROOT ro console=tty0 console=ttyS0,115200 earlyprintk=ttyS0,115200 consoleblank=0 cgroup_enable=memory swapaccount=1 ignition.firstboot=1 ignition.platform.id=qemu security=selinux",
  "os-release": "974.0",
  "signature/crc": "Put valid content here",
  "manifest": "URL"
}
```

##### Push / Create

```sh
$ /config/oras push localhost:5000/oras-gardenlinux:v1 kvm_oci-amd64-today-dc5ce3cd.oci.tar.xz:application/vnd.onmetal.image.rootfs.v1alpha1.rootfs  kvm_oci-amd64-today-dc5ce3cd.vmlinuz:application/vnd.onmetal.image.vmlinuz.v1alpha1.vmlinuz  kvm_oci-amd64-today-dc5ce3cd.initrd:application/vnd.onmetal.image.initramfs.v1alpha1.initramfs --config orasconfig.json:application/vnd.onmetal.image.config.v1alpha1+json
```

The build flags using onmetal-image are the following:

```sh
$ onmetal-image build --rootfs-file output/kvm_oci-amd64-today-dc5ce3cd/rootfs.raw --kernel-file output/kvm_oci-amd64-today-dc5ce3cd/rootfs.vmlinuz --initramfs-file output/kvm_oci-amd64-today-dc5ce3cd/rootfs.initrd --command-line 'root=LABEL=ROOT ro console=tty0 console=ttyS0,115200 earlyprintk=ttyS0,115200 consoleblank=0 cgroup_enable=memory swapaccount=1 ignition.firstboot=1 ignition.platform.id=qemu security=selinux' --store-path output/kvm_oci-amd64-today-dc5ce3cd/onmetal
```

To add additional artifacts during creation they can simply be appended:

```sh
$ oras push localhost:5000/oras-gardenlinux:v4 kvm_oci-amd64-today-dc5ce3cd.raw:application/vnd.onmetal.image.rootfs.v1alpha1.rootfs kvm_oci-amd64-today-dc5ce3cd.vmlinuz:application/vnd.onmetal.image.vmlinuz.v1alpha1.vmlinuz kvm_oci-amd64-today-dc5ce3cd.initrd:application/vnd.onmetal.image.initramfs.v1alpha1.initramfs kvm_oci-amd64-today-dc5ce3cd.os-release:application/vnd.gardenlinux.os.release kvm_oci-amd64-today-dc5ce3cd.log:application/vnd.gardenlinux.log kvm_oci-amd64-today-dc5ce3cd.manifest:application/vnd.gardenlinux.manifest --config orasconfig.json:application/vnd.onmetal.image.config.v1alpha1+json
```

This will give us the following structure:

```sh
$ onmetal-image inspect localhost:5000/oras-gardenlinux:v4
{
  "descriptor": {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "digest": "sha256:d3d8d1bbc4dbe8a9e74276fb5de439a82e4d18aa3491c2ec8229c5328716f061",
    "size": 1809,
    "annotations": {
      "org.opencontainers.image.ref.name": "localhost:5000/oras-gardenlinux:v4"
    }
  },
  "manifest": {
    "schemaVersion": 2,
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "config": {
      "mediaType": "application/vnd.onmetal.image.config.v1alpha1+json",
      "digest": "sha256:5bb41d1b9f4ab6c20f7f5a5576286fce6b7664a8f058f38085ddb3066c0faf35",
      "size": 214
    },
    "layers": [
      {
        "mediaType": "application/vnd.onmetal.image.rootfs.v1alpha1.rootfs",
        "digest": "sha256:a6baf04f08ae108f23eb76d8ccf3704f4d52bc10fa5645657f55a5185a52cfb5",
        "size": 721420288,
        "annotations": {
          "org.opencontainers.image.title": "kvm_oci-amd64-today-dc5ce3cd.raw"
        }
      },
      {
        "mediaType": "application/vnd.onmetal.image.vmlinuz.v1alpha1.vmlinuz",
        "digest": "sha256:046ff03c1918ef70f7526d4820b66ac04b06415a5f0d5153d5f08d1b45dc87ca",
        "size": 13230144,
        "annotations": {
          "org.opencontainers.image.title": "kvm_oci-amd64-today-dc5ce3cd.vmlinuz"
        }
      },
      {
        "mediaType": "application/vnd.onmetal.image.initramfs.v1alpha1.initramfs",
        "digest": "sha256:ad1e195f8d7874a6cbf6a972a0badf8e7de03ccac54f4ae920c4ed9398bf7110",
        "size": 27363804,
        "annotations": {
          "org.opencontainers.image.title": "kvm_oci-amd64-today-dc5ce3cd.initrd"
        }
      },
      {
        "mediaType": "application/vnd.gardenlinux.os.release",
        "digest": "sha256:9664cc6fb8ab048760c776064f0391a5949459986fed2e3ed0189e3aa6376c7d",
        "size": 510,
        "annotations": {
          "org.opencontainers.image.title": "kvm_oci-amd64-today-dc5ce3cd.os-release"
        }
      },
      {
        "mediaType": "application/vnd.gardenlinux.log",
        "digest": "sha256:bda2276cbf5fc37d411883ef9d441a19482c7a4363782da108ac17e6130eff47",
        "size": 108288,
        "annotations": {
          "org.opencontainers.image.title": "kvm_oci-amd64-today-dc5ce3cd.log"
        }
      },
      {
        "mediaType": "application/vnd.gardenlinux.manifest",
        "digest": "sha256:7977d5a6cd277d0241c23320069d6a91902643cd6c8f8865181d8b1c15512fe2",
        "size": 6802,
        "annotations": {
          "org.opencontainers.image.title": "kvm_oci-amd64-today-dc5ce3cd.manifest"
        }
      }
    ],
    "annotations": {
      "org.opencontainers.image.created": "2022-11-30T13:31:22Z"
    }
  },
  "config": {
    "commandLine": "root=LABEL=ROOT ro console=tty0 console=ttyS0,115200 earlyprintk=ttyS0,115200 consoleblank=0 cgroup_enable=memory swapaccount=1 ignition.firstboot=1 ignition.platform.id=qemu security=selinux"
  }
}
```


#### List created image using oras

```sh
$  /config/oras manifest fetch localhost:5000/oras-gardenlinux:v2 | jq '.'
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.manifest.v1+json",
  "config": {
    "mediaType": "application/vnd.onmetal.image.config.v1alpha1+json",
    "digest": "sha256:5bb41d1b9f4ab6c20f7f5a5576286fce6b7664a8f058f38085ddb3066c0faf35",
    "size": 214
  },
  "layers": [
    {
      "mediaType": "application/vnd.onmetal.image.rootfs.v1alpha1.rootfs",
      "digest": "sha256:cbde236614f165c30cb716ed335f829264a59672b19533119cb28e4da354806f",
      "size": 199673068,
      "annotations": {
        "org.opencontainers.image.title": "kvm_oci-amd64-today-dc5ce3cd.oci.tar.xz"
      }
    },
    {
      "mediaType": "application/vnd.onmetal.image.vmlinuz.v1alpha1.vmlinuz",
      "digest": "sha256:046ff03c1918ef70f7526d4820b66ac04b06415a5f0d5153d5f08d1b45dc87ca",
      "size": 13230144,
      "annotations": {
        "org.opencontainers.image.title": "kvm_oci-amd64-today-dc5ce3cd.vmlinuz"
      }
    },
    {
      "mediaType": "application/vnd.onmetal.image.initramfs.v1alpha1.initramfs",
      "digest": "sha256:a45c40c17c93fb1cb1275126f82bc5383a3f53fb7bf42e7d335deb263eab3e8b",
      "size": 27363208,
      "annotations": {
        "org.opencontainers.image.title": "kvm_oci-amd64-today-dc5ce3cd.initrd"
      }
    }
  ],
  "annotations": {
    "org.opencontainers.image.created": "2022-11-30T11:10:16Z"
  }
}
```

So we have some additonal annotations here which are ignored by onmetal-image.

#### Grab the config details using oras

```sh
$ oras manifest fetch-config localhost:5000/oras-gardenlinux:v3 | jq .
{
  "commandLine": "root=LABEL=ROOT ro console=tty0 console=ttyS0,115200 earlyprintk=ttyS0,115200 consoleblank=0 cgroup_enable=memory swapaccount=1 ignition.firstboot=1 ignition.platform.id=qemu security=selinux",
  "os-release": "974.0",
  "signature/crc": "Put valid content here",
  "manifest": "URL"
}
```

#### List using onmetal-image

```sh
$ /config/onmetal-image --store-path /git/.build/onmetal pull localhost:5000/oras-gardenlinux:v2

$ /config/onmetal-image --store-path /git/.build/onmetal inspect localhost:5000/oras-gardenlinux:v2
{
  "descriptor": {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "digest": "sha256:75c3b05c3e9962b8221b88164b24aed5d7ec3ecdcec5decdb6810588ef2cbf9c",
    "size": 1110,
    "annotations": {
      "org.opencontainers.image.ref.name": "localhost:5000/oras-gardenlinux:v2"
    }
  },
  "manifest": {
    "schemaVersion": 2,
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "config": {
      "mediaType": "application/vnd.onmetal.image.config.v1alpha1+json",
      "digest": "sha256:5bb41d1b9f4ab6c20f7f5a5576286fce6b7664a8f058f38085ddb3066c0faf35",
      "size": 214
    },
    "layers": [
      {
        "mediaType": "application/vnd.onmetal.image.rootfs.v1alpha1.rootfs",
        "digest": "sha256:cbde236614f165c30cb716ed335f829264a59672b19533119cb28e4da354806f",
        "size": 199673068,
        "annotations": {
          "org.opencontainers.image.title": "kvm_oci-amd64-today-dc5ce3cd.oci.tar.xz"
        }
      },
      {
        "mediaType": "application/vnd.onmetal.image.vmlinuz.v1alpha1.vmlinuz",
        "digest": "sha256:046ff03c1918ef70f7526d4820b66ac04b06415a5f0d5153d5f08d1b45dc87ca",
        "size": 13230144,
        "annotations": {
          "org.opencontainers.image.title": "kvm_oci-amd64-today-dc5ce3cd.vmlinuz"
        }
      },
      {
        "mediaType": "application/vnd.onmetal.image.initramfs.v1alpha1.initramfs",
        "digest": "sha256:a45c40c17c93fb1cb1275126f82bc5383a3f53fb7bf42e7d335deb263eab3e8b",
        "size": 27363208,
        "annotations": {
          "org.opencontainers.image.title": "kvm_oci-amd64-today-dc5ce3cd.initrd"
        }
      }
    ],
    "annotations": {
      "org.opencontainers.image.created": "2022-11-30T11:10:16Z"
    }
  },
  "config": {
    "commandLine": "root=LABEL=ROOT ro console=tty0 console=ttyS0,115200 earlyprintk=ttyS0,115200 consoleblank=0 cgroup_enable=memory swapaccount=1 ignition.firstboot=1 ignition.platform.id=qemu security=selinux"
  }
}
```

#### Request artifacts via onmetal-image

These steps verify that the layers created with the oras commands are still usable with onmetal-image and it's layer-specific subcommands.

##### Kernel

```sh
/config/onmetal-image --store-path /git/.build/onmetal url --layer kernel localhost:5000/oras-gardenlinux:v2
{
  "url": "http://localhost:5000/v2/oras-gardenlinux/blobs/sha256:046ff03c1918ef70f7526d4820b66ac04b06415a5f0d5153d5f08d1b45dc87ca"
}

$ curl -s -L http://localhost:5000/v2/oras-gardenlinux/blobs/sha256:046ff03c1918ef70f7526d4820b66ac04b06415a5f0d5153d5f08d1b45dc87ca -o oras_vmlinuz
```

##### Initrd

```sh
$ /config/onmetal-image --store-path /git/.build/onmetal url --layer initramfs localhost:5000/oras-gardenlinux:v2
{
  "url": "http://localhost:5000/v2/oras-gardenlinux/blobs/sha256:a45c40c17c93fb1cb1275126f82bc5383a3f53fb7bf42e7d335deb263eab3e8b"
}
$ curl -s -L http://localhost:5000/v2/oras-gardenlinux/blobs/sha256:a45c40c17c93fb1cb1275126f82bc5383a3f53fb7bf42e7d335deb263eab3e8b  -o oras_initrd

$ cmp oras_initrd kvm_oci-amd64-today-dc5ce3cd.initrd
```

##### Root filesystem

```sh
$ /config/onmetal-image --store-path /git/.build/onmetal url --layer rootfs localhost:5000/oras-gardenlinux:v2
{
  "url": "http://localhost:5000/v2/oras-gardenlinux/blobs/sha256:cbde236614f165c30cb716ed335f829264a59672b19533119cb28e4da354806f"
}

$ curl -s -L http://localhost:5000/v2/oras-gardenlinux/blobs/sha256:cbde236614f165c30cb716ed335f829264a59672b19533119cb28e4da354806f  -o oras_rootfs
```

#### Manifest with annotations

created by

``` sh
$ jq . annotations.json
{
  "$config": {
    "os-release": "981.0",
    "signature/src": "kjldaslkdjasdklsjada"
  },
  "$manifest": {
    "signed-by": "author"
  }
}

$ oras push --annotation-file annotations.json localhost:5000/oras-gardenlinux:981.0 kvm_oras-amd64-today-aab1c350.raw:application/vnd.onmetal.image.rootfs.v1alpha1.rootfs kvm_oras-amd64-today-aab1c350.vmlinuz:application/vnd.onmetal.image.vmlinuz.v1alpha1.vmlinuz kvm_oras-amd64-today-aab1c350.initrd:application/vnd.onmetal.image.initramfs.v1alpha1.initramfs --config kvm_oras-amd64-today-aab1c350.json:application/vnd.onmetal.image.config.v1alpha1+json
```

will result in

``` sh
{
  "schemaVersion": 2,
  "mediaType": "application/vnd.oci.image.manifest.v1+json",
  "config": {
    "mediaType": "application/vnd.onmetal.image.config.v1alpha1+json",
    "digest": "sha256:923549919b8afae4ea8df24fdf1782603983562d2c4f74c6094e1d431482a292",
    "size": 747,
    "annotations": {
      "os-release": "981.0",
      "signature/src": "kjldaslkdjasdklsjada"
    }
  },
  "layers": [
    {
      "mediaType": "application/vnd.onmetal.image.rootfs.v1alpha1.rootfs",
      "digest": "sha256:fba672096e4383ed2a99a0a0d5f52ca80598af36cbe29ff4b11fadd0ad2fb76b",
      "size": 722468864,
      "annotations": {
        "org.opencontainers.image.title": "kvm_oras-amd64-today-aab1c350.raw"
      }
    },
    {
      "mediaType": "application/vnd.onmetal.image.vmlinuz.v1alpha1.vmlinuz",
      "digest": "sha256:0b9b2cb0fe1ac567972f597e4d455fb166412ed721927965d9ea2363781cab43",
      "size": 13230848,
      "annotations": {
        "org.opencontainers.image.title": "kvm_oras-amd64-today-aab1c350.vmlinuz"
      }
    },
    {
      "mediaType": "application/vnd.onmetal.image.initramfs.v1alpha1.initramfs",
      "digest": "sha256:eda9574599e3e3b52708a945e3b2dbb71a6cbecfeff2947100dadfd6af0e56a8",
      "size": 27603392,
      "annotations": {
        "org.opencontainers.image.title": "kvm_oras-amd64-today-aab1c350.initrd"
      }
    }
  ],
  "annotations": {
    "org.opencontainers.image.created": "2022-12-07T11:17:04Z",
    "signed-by": "author"
  }
}
```

##### Used software versions

Component | Version
| :--- | ---:
oras | 0.16.0
onmetal-image | Git-Commit: [26f6ac2607e1cac19c35fac94aa8cd963b19628a](https://github.com/onmetal/onmetal-image/commit/26f6ac2607e1cac19c35fac94aa8cd963b19628a)

### Additional information

#### Image spec

[Pre-defined annotation keys](https://github.com/opencontainers/image-spec/blob/v1.0.1/annotations.md#pre-defined-annotation-keys)

#### Signing

_This section is only for information, no actual implementation is done._

Artifacts and images should be signed, so an update of one of them could be discovered.

For this Docker implemented [Content Trust](https://docs.docker.com/engine/security/trust/) which only works in docker and does not provide options to move signed images to another registry.

The [Notary Project](https://github.com/notaryproject/notaryproject) aims to provide specifications for cross registry usage but it is not yet finished.

In contrast [cosign](https://github.com/sigstore/cosign) can be used.

##### cosign

Creating a key pair can be done with _cosign generate-key-pair_.

To sign the artifact the sha256 digest must be used:

```sh
$ cosign sign --key cosign.key localhost:5000/oras-gardenlinux@sha256:2b0ab7951d92049b29696d65867b6f536ef413726de8abd8cd2523c6bfd8519b
Enter password for private key:
Pushing signature to: localhost:5000/oras-gardenlinux
```


For validation the public key must be used. The following example shows verification using the wrong key:

```sh
cosign verify --key validate.pub localhost:5000/oras-gardenlinux@sha256:386acf4443a3d45dfe6de4160995bcb8307e08ade6c7b2d798a694a6322a8f23
Error: no matching signatures:
invalid signature when validating ASN.1 encoded signature
main.go:62: error during command execution: no matching signatures:
invalid signature when validating ASN.1 encoded signature
```

While using the correct public key everything is fine and the return code is correct:

```sh
$ cosign verify --key gl-cosign.pub localhost:5000/oras-gardenlinux@sha256:386acf4443a3d45dfe6de4160995bcb8307e08ade6c7b2d798a694a6322a8f23 | jq .

Verification for localhost:5000/oras-gardenlinux@sha256:386acf4443a3d45dfe6de4160995bcb8307e08ade6c7b2d798a694a6322a8f23 --
The following checks were performed on each of these signatures:
  - The cosign claims were validated
  - The signatures were verified against the specified public key
[
  {
    "critical": {
      "identity": {
        "docker-reference": "localhost:5000/oras-gardenlinux"
      },
      "image": {
        "docker-manifest-digest": "sha256:386acf4443a3d45dfe6de4160995bcb8307e08ade6c7b2d798a694a6322a8f23"
      },
      "type": "cosign container image signature"
    },
    "optional": null
  }
]
$ echo $?
0
```
