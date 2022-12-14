## Feature: _distroless
### Description
<website-feature>

This `flag` feature creates a `distroless` alike artifacts for Container Runtime Environments (CRE) and is compatible with Docker and Podman.
</website-feature>

### Features
Like the `container` feature, this creates a common `docker-archive` image artifact as a `.tar.gz` tarball which can be used on all common Container Runtime Environments (e.g. Podman, Docker). However, the `_distroless` feature removes many packages and removes the most of distribution related configs.

The `distroless` feature ships only `glibc` and `python3-minimal` for executing application but may be configured to the individual needs by the feature system.

By default, created artifacts are only `base` images without any further features on top. This means, they may mostly be used for executing a specific `entrypoint` script. To fullfil needed dependencies of packages, libs, etc. of the `entrypoint` script a custom build may be needed.
Custom Garden Linux artifacts created by this feature can be loaded by running e.g. `docker load -i container-amd64-today-local.container.tar.gz`.

### Unit testing
This flag feature does not support unit testing.


### Meta
|||
|---|---|
|type|flag|
|artifact|`.tar.gz`|
|included_features|`base`, `container`|
|excluded_features|None|