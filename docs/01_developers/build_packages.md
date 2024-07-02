Garden Linux packages are built using [the `package-build` scripts](https://github.com/gardenlinux/package-build).

Each package has it's own GitHub repository following the naming convention `package-{package_name}`.
Those packages are picked up by [the workflows of the 'repo'](https://github.com/gardenlinux/repo).

As a trivial example, have a look at [`gardenlinux/package-containerd`](https://github.com/gardenlinux/package-containerd).

As a non-trivial example have a look at [`gardenlinux/package-openssh`](https://github.com/gardenlinux/package-openssh).

If possible, we use the binary packages as provided by debian.
Only in cases where it is needed to make a change, we rebuild the package and thus create a GitHub repository `package-{package_name}`.

There are different types of package rebuilds:

1. Source from debian:
  - use case: apply Garden Linux-specific patches on top
  - use case: rebuild with a specific build environment (e.g. golang, glibc, gcc, ...), for example when newer compiler/runtime is needed
  - use case: a package we include was (temporarily) removed from debian testing
    - this happens from time to time and is to be expected
2. Source from upstream project:
  - use case: debian does not maintain a package for the given software we need
  - use case: debian maintains an old version only, we need to create a package for a newer version available in upstream
3. Native source:
  - use case: source code is developed/maintained by the Garden Linux developers, so debian does not package it
