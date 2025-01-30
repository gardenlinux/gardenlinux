## Feature: _oci
### Description
<website-feature>
This flag feature creates an artifact for Open Container Image (OCI) compatible platforms.
</website-feature>

### Features
This feature creates an OCI archive containing a bootable container image.


### Usage

*The following steps have to be adopted to your build configuration.*

Build a kernel, an initrd and the rootfs by generating the build for your target platform and add the *_oci* feature:

``` shell
$ ./build gcp_oci
```

After the build process has finished you*ll find an compressed archive in the destination directory of your build:

``` shell
$ ls -lsah .build/*.oci.*
.build/gcp-gardener_oci-amd64-today-local.oci
```

`.build/gcp-gardener_oci-amd64-today-local.oci` is the OCI archive.

### Meta
|||
|---|---|
|type|flag|
|artifact|None|
|included_features|None|
|excluded_features|None|
