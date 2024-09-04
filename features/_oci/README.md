## Feature: _oci
### Description
<website-feature>
This flag feature creates an artifact for Open Container Image (OCI) compatible platforms.
</website-feature>

### Features
This feature creates an archive containing the artifacts for an upload to an OCI compatible registry. This does *not* create a bootable container image. Instead the build artifacts are bundled into an OCI compatible image.


### Usage

*The following steps have to be adopted to your build configuration.*

Build a kernel, an initrd and the rootfs by generating the build for your target platform and add the *_oci* feature:

``` shell
$ ./build gcp_oci
```

After the build process has finished you*ll find an compressed archive in the destination directory of your build:

``` shell
$ ls -lsah .build/*.oci.*
.build/gcp-gardener_oci-amd64-today-local.initrd
.build/gcp-gardener_oci-amd64-today-local.log
.build/gcp-gardener_oci-amd64-today-local.manifest
.build/gcp-gardener_oci-amd64-today-local.oci.tar.xz
.build/gcp-gardener_oci-amd64-today-local.os-release
.build/gcp-gardener_oci-amd64-today-local.raw
.build/gcp-gardener_oci-amd64-today-local.tar.gz
.build/gcp-gardener_oci-amd64-today-local.tar.xz
.build/gcp-gardener_oci-amd64-today-local.tar.xz.sha256
.build/gcp-gardener_oci-amd64-today-local.vmlinuz
```

`.build/gcp-gardener_oci-amd64-today-local.oci.tar.xz` is the archive containing the created output of *onmetal-image* and can be used for uploading the contents to an OCI compatible registry after extracting and using *onmetal-image* itself:

``` shell
$ cd .build
$ tar xJvf .build/gcp-gardener_oci-amd64-today-local.oci.tar.xz
```

The files are extracted to the directory *onmetal*.

Adjust your environment to store the credentials for your registry so they can be used by onmetal-image. This can be achieved by using e.g. *docker*, *podman* or *oras*.
Refer to the documentation of your registry.

``` shell
$ oras login ghcr.io
Username: <username>
Personal Access Token: <PAT>
Login Succeeded
```

Now you can list the contents of your onmetal-image storage:

``` shell
$ onmetal-image --store-path ./onmetal/ list
REPOSITORY  TAG         IMAGE ID
<none>      <none>      f0dcfde4f8b4
```

Go and grep your full ID out of the directory:

``` shell
$ jq '.' onmetal/index.json 
{
    "schemaVersion":2,
    "manifests": [
      {
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "digest": "sha256:f0dcfde4f8b4b6033add31243096a4b560173cd9884be1e37c524c53219fa394",
        "size": 713
      }
    ]
}
```

You have to *tag* your created artifacts. This is needed because the the tag must contain the name of the remote registry which is unknown during the build process.


``` shell
$ onmetal-image --store-path ./onmetal/ tag sha256:f0dcfde4f8b4b6033add31243096a4b560173cd9884be1e37c524c53219fa394 ghcr.io/<username>/<project>:<version>
Successfully tagged ghcr.io/<username>/<project>:<version> with sha256:f0dcfde4f8b4b6033add31243096a4b560173cd9884be1e37c524c53219fa394

$ onmetal-image --store-path ./onmetal/ list
REPOSITORY                   TAG         IMAGE ID
<none>                       <none>      f0dcfde4f8b4
ghcr.io/<username>/<project> <version>   f0dcfde4f8b4
```

Finally push the artifacts:

``` shell
$ onmetal-image --store-path ./onmetal/ push ghcr.io/<username>/<project>:<version>
Successfully pushed ghcr.io/<username>/<project>:<version> f0dcfde4f8b4b6033add31243096a4b560173cd9884be1e37c524c53219fa394
```

#### Using the artifacts

You can use *onmetal-image* once again to verify the contents:

``` shell
$ onmetal-image --store-path ./onmetal/ inspect ghcr.io/<username>/<project>:<version>
{
  "descriptor": {
    "mediaType": "application/vnd.oci.image.manifest.v1+json",
    "digest": "sha256:f0dcfde4f8b4b6033add31243096a4b560173cd9884be1e37c524c53219fa394",
    "size": 713,
    "annotations": {
      "org.opencontainers.image.ref.name": "ghcr.io/<username>/<project>:<version>"
    }
  },
  "manifest": {
    "schemaVersion": 2,
    "config": {
      "mediaType": "application/vnd.onmetal.image.config.v1alpha1+json",
      "digest": "sha256:41c46e4d7cec399eee96a20c7b3ba27b4cf4910eae915aa9bb7e1837f2982dd9",
      "size": 147
    },
    "layers": [
      {
        "mediaType": "application/vnd.onmetal.image.rootfs.v1alpha1.rootfs",
        "digest": "sha256:44dd616962d17884bd3609443a3c62b94d423fd1513a40098ffa1a1f75495fd5",
        "size": 231536600
      },
      {
        "mediaType": "application/vnd.onmetal.image.initramfs.v1alpha1.initramfs",
        "digest": "sha256:3108caa582a70f3490723a654d93896840ea2ad09d3c06bb0c51ed83a60e0660",
        "size": 16583520
      },
      {
        "mediaType": "application/vnd.onmetal.image.vmlinuz.v1alpha1.vmlinuz",
        "digest": "sha256:d002d4426df1928be7646289e8a67f2851679e955cacbbc042295f5c6af80b69",
        "size": 13212832
      }
    ]
  },
  "config": {
    "commandLine": "ro console=tty0 console=ttyS0,115200 earlyprintk=ttyS0,115200 consoleblank=0 cgroup_enable=memory swapaccount=1 security=apparmor"
  }
}
```

And of course you can ask for the url e.g. of the kernel:

``` shell
$ onmetal-image --store-path ./onmetal/ url --layer kernel ghcr.io/<username>/<project>:<version>
{
  "headers": {
    "Authorization": [
      "Bearer <YOUR BEARER TOKEN>"
    ]
  },
  "url": "https://ghcr.io/v2/<username>/<project>/blobs/sha256:d002d4426df1928be7646289e8a67f2851679e955cacbbc042295f5c6af80b69"
}
```

With that information you can instruct *curl* (ensure redirects!) to obtain the content:

``` shell
$ curl -v -L -H "Authorization: Bearer <BEARER TOKEN>" -o vmlinuz https://ghcr.io/v2/<username>/<project>/blobs/sha256:d002d4426df1928be7646289e8a67f2851679e955cacbbc042295f5c6af80b69
```

Here you should find the kernel in the output file *vmlinuz*.

### Inspecting the uploaded content

You can inspect the manifest and all additional information by using *curl*. Please take care of the additional header which you have to submit:

``` shell
$ curl -s -L -H "Authorization: Bearer <BEARER TOKEN>" -H "Accept: application/vnd.oci.image.manifest.v1+json" https://ghcr.io/v2/<username>/<project>/manifests/<version> | jq
{
  "schemaVersion": 2,
  "config": {
    "mediaType": "application/vnd.onmetal.image.config.v1alpha1+json",
    "digest": "sha256:41c46e4d7cec399eee96a20c7b3ba27b4cf4910eae915aa9bb7e1837f2982dd9",
    "size": 147
  },
  "layers": [
    {
      "mediaType": "application/vnd.onmetal.image.rootfs.v1alpha1.rootfs",
      "digest": "sha256:44dd616962d17884bd3609443a3c62b94d423fd1513a40098ffa1a1f75495fd5",
      "size": 231536600
    },
    {
      "mediaType": "application/vnd.onmetal.image.initramfs.v1alpha1.initramfs",
      "digest": "sha256:3108caa582a70f3490723a654d93896840ea2ad09d3c06bb0c51ed83a60e0660",
      "size": 16583520
    },
    {
      "mediaType": "application/vnd.onmetal.image.vmlinuz.v1alpha1.vmlinuz",
      "digest": "sha256:d002d4426df1928be7646289e8a67f2851679e955cacbbc042295f5c6af80b69",
      "size": 13212832
    }
  ]
}
```

With this information you can also use curl to get the contents:

``` shell
$ curl -L -H "Authorization: Bearer <BEARER TOKEN>" -H "Accept: application/vnd.oci.image.manifest.v1+json" https://ghcr.io/v2/<username>/<project>/blobs/sha256:d002d4426df1928be7646289e8a67f2851679e955cacbbc042295f5c6af80b69 -o kernel
```

``` shell
$ curl -s -L -H "Authorization: Bearer <BEARER TOKEN>" -H "Accept: application/vnd.oci.image.manifest.v1+json" https://ghcr.io/v2/<username>/<project>/blobs/sha256:41c46e4d7cec399eee96a20c7b3ba27b4cf4910eae915aa9bb7e1837f2982dd9 | jq
{
  "commandLine": "ro console=tty0 console=ttyS0,115200 earlyprintk=ttyS0,115200 consoleblank=0 cgroup_enable=memory swapaccount=1 security=apparmor"
}
```

#### Attaching additional artifacts (like buildlog)

The build process creates additional files like the buildlog. These file can be attached to an OCI compatible registry as additional artifacts. For this one must use a client which can handle these types.
The following example shows how to attach these files files to an Azure registry using *oras*:

``` shell
$ oras attach <registry>/<project>:<version> azure-gardener_dev_oci-amd64-today-local.os-release --artifact-type build/os-release
$ oras attach <registry>/<project>:<version> azure-gardener_dev_oci-amd64-today-local.manifest --artifact-type build/manifest
$ oras attach <registry>/<project>:<version> azure-gardener_dev_oci-amd64-today-local.log --artifact-type build/log
```

#### docker / podman pull

Pulling these OCI compatible images using docker or podman is not possible. The last download step failed due to the fact that this images does not contain the expected filesystem layer.

We wanted to create a simple possibility to pull the image usind docker or podman and display additional information. But without building a simple container this is not possible. An idea would be to create this simple container just holding the os-release, buildlog and manifest.

#### Additional information

- [onmetal-image](https://github.com/onmetal/onmetal-image)
- [OCI Distribution Specifications](https://github.com/opencontainers/distribution-spec/)
- [OCI Registry As Storage (ORAS)](https://oras.land/)
- [jq](https://stedolan.github.io/jq/)

### Unit testing
This feature does not support unit tests.

### Meta
|||
|---|---|
|type|flag|
|artifact|`.oci.tar.xz`|
|included_features|cloud|
|excluded_features|None|
