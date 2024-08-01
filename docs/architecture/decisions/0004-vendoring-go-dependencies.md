# 4. Vendoring dependencies in Go Applications

**Date:** 2024-08-01

## Status

Accepted

## Context

This document discusses the options and tradeoffs for packaging Go applications in Garden Linux.

### Build time vs run time dependencies

When speaking of software dependencies, it is important to keep build time and run time dependencies apart.
This document is concerned with build time dependencies in Go applications.

Build dependencies can be specified in the Garden Linux package build like in [this example](https://github.com/gardenlinux/package-ignition/blob/a5403d0e5473b63cf19a4fb2d4ac42f8ed979000/.github/workflows/build.yml#L11).

### Traditional Linux distributions

Linux distributions historically assume compiled languages work similar to C or C++.
Build time dependencies are packaged as part of the distribution.
If an application needs the `foo` library to build, installing a package named `libfoo-dev` or similar is the recommended solution.

### The Go ecosystem

Like many modern programming language ecosystems, Go has a dependency management system that works independent of linux package managers.
Go is a compiled language, and it's known for producing large binary files with little to no run time dependencies.

[go mod](https://go.dev/doc/modules/gomod-ref) is a tool to declare and manage build time dependencies for Go applications.

It's also common in Go to manually copy dependencies in source code form in the repository.

This process is described as 'vendoring'.
`go mod` also supports the `go mod vendor` command to automate this process.

### Debian's position

Vendoring goes against the general idea of traditional linux distributions where dependencies are packaged on their own as described above.

The following articles provide context on how vendoring of Go code is viewed in Debian:

- [LWN.net (January 13, 2021): Debian discusses vendoring—again](https://lwn.net/Articles/842319/)
- [LWN.net (January 20, 2021): The Debian tech committee allows Kubernetes vendoring](https://lwn.net/Articles/843313/)

### Qualities ensured by Garden Linux

For Garden Linux, being able to reproduce disk images of previous releases is a crucial quality.
In the past, one way to achieve this was to have all dependencies packages in the Garden Linux APT repository, and to de-vendor Go applications when needed.

### The downsides of de-vendoring

To be able to build Go applications without vendoring can mean quite a lot of effort as most likely Garden Linux does not package all the needed dependencies.
Adding multiple new packages for dependencies of a new Go package might be a lot of maintenance effort.

## Decision

We allow vendoring dependencies for Go applications in Garden Linux.
We require vendored dependencies to be commited to version control to allow reproduce releases.

## Consequences

- We are able to follow upstream projects of applications written in Go (like containerd) more closely
- If dependencies are downloaded at build time, even with proper version locks and checksums, we depend on external repositories which defeats the purpose of our [debian snapshot](https://github.com/gardenlinux/repo?tab=readme-ov-file#gardenlinux-repo-infrastructure)
