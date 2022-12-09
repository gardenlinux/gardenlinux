# Local tests

# Table of Content
- [General](#general)
- [Test oci](#test-oci)
- [Test garden_feat](#test-garden_feat)

# General

Tests located in this folter `test/local` are local tests. Local tests are executed in the base-test container, the integration-test container will also work, but without spawning a `chroot` or `kvm` environment that needs to be accessed via `ssh`. The local tests are run directly in the container. The goal is to be able to write tests for the Garden Linux build pipeline.

The configuration file for this tests does not need the `features` to be set, if set it will be ignored. The configuration contains a dictionary, the key should be the name of the test and under the key the configuration options for this specific test are defined. If a test does not have any configuration options it can be left out of the configuration file.

To select a specific test to be executed instead of running all local tests, the `-k EXPRESSION` *pytest* option can be used. See the `pytest --help` for a more detailed explanation.

```yaml
local:
    # configuration parameters for tests separated by test names
    oci:
      # Path to a final artifact. Represents the .tar.xz archive image file (required)
      image: /build/kvm_dev_oci-amd64-today-local.oci.tar.xz
      kernel: /build/kvm_dev_oci-amd64-today-local.vmlinuz

    garden_feat:
```

# Test oci
This test does several steps using the results of a build with _oci feature:
- verify neccessary testconfig options are present (image, kernel)
- install the docker-registry into the container, provide a config, start the registry
- extracts the testconfig["image"] file to retrieve the OCI fs layout
- tag the extracted OCI image for uploading to the registry on localhost
- push the OCI image to the local registry
- retrieve the url for the kernel file out of the OCI image
- download the kernel image
- compare the downloaded kernel with the testconfig["kernel"]

Configuration options:
- **oci** contains the configuration options for local test `test_oci`
    - **image** the build result image used within the tests
    - **kernel** the name for the builded kernel

# Test garden_feat

This test checks if the script `bin/garden-feat` is working as expected. The script creates the Garden Linux features list during build, therefore it is important to resolve dependencies between the feature properly.

This test does not have any configuration options.