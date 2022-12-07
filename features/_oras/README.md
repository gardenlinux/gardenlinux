## Feature: _oras

### Description
<website-feature>
This flag shows how to push to an OCI compatible registry using [oras](https://oras.land). It is only for demonstration and does *not* alter the contents or results of the builded artifacts.
</website-feature>


### Usage

``` shell
$ ./build.sh --features kvm,_oras .build/
```

The output of the build process shows the oras command to push the artifacts in the way they can be consumed by onmetal-image.

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

##### Used software versions

Component | Version
| :--- | ---: 
oras | 0.16.0
onmetal-image | Git-Commit: [26f6ac2607e1cac19c35fac94aa8cd963b19628a](https://github.com/onmetal/onmetal-image/commit/26f6ac2607e1cac19c35fac94aa8cd963b19628a)

