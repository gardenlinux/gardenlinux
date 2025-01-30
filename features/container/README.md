## Feature: container
### Description
<website-feature>
This platform feature creates artifacts for Container Runtime Environments (CRE) and is compatible with Docker and Podman.
</website-feature>

### Features
This feature creates a common `docker-archive` image artifact as a `.tar.gz` tarball which can be used on all common Container Runtime Environments (e.g. Podman, Docker).

By default, created artifacts are only `base` images without any further features on top. This means, they may mostly be used for executing a specific `entrypoint` script. To fullfil needed dependencies of packages, libs, etc. of the `entrypoint` script a custom build may be needed.
Custom Garden Linux artifacts created by this feature can be loaded by running e.g. `docker load -i container-amd64-today-local.container.tar.gz`.

### Unit testing
This platform features supports unit testing and is based on the `chroot` fixture.

To ensure that unit tests can be performed the package `openssh-server` gets installed within a `chroot` during the [unit testing](../../tests/platform/chroot.py#L188-L200).

Testing of specific units can be avoided by placing the `non_container` fixture.


### Meta
|||
|---|---|
|type|platform|
|artifact|`.tar.gz`|
|included_features|`base`,`_oci`|
|excluded_features|None|