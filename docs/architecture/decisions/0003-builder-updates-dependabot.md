# 3. Update the Builder using Dependabot

**Date:** 2023-12-11

## Status

Accepted

## Context

The [Garden Linux Builder](https://github.com/gardenlinux/builder) is a containerized solution to build Linux images.
It is used by the upstream Garden Linux project, but it is and can be used by any project needing custom Linux images.

All projects that use the builder are encouraged to pin the builder to a specific build [as shown here in the Garden Linux repository](https://github.com/gardenlinux/gardenlinux/blob/f4a389e88feb15e78b5529831d3cf3cd8978fc20/build#L6).
Pinning the builder to one specific version as opposed to using a `latest` tag is desirable so image builds are stable and predictable. This pinning approach has the downside that manual effort is needed to update the used builder from time to time.

Also, updating the builder only means changing one sha with another sha which does not satisfy the wish to understand what has changed in the builder during those two versions.

It would be nice if updating builder versions could be handled by [dependabot](https://docs.github.com/en/code-security/dependabot) which does support OCI images.

The only way that seems possible to make this happen is to have a dedicated Dockerfile/Containerfile.
Dependabot can take care to keep this up to date and will open pull requests for updates.
Those pull requests can validate using CI/CD that the new builder version still works and it will contain a summary of changes between the two versions.

Currently the builder only supports building from Dockerfiles with the standard name (`Dockerfile`), but having a file with that name in the project root just for defining the version of the builder might not be desirable.
For this reason, the builder should also accept a Dockerfile with a more speaking name such as `builder.dockerfile`.
Dependabot will be able to pick that up.

## Decision

The Garden Linux builder supports using dependabot and we recommend users to make use of that.

We implement the needed changes to support this, like:

- Tagged releases on GitHub for the builder will be published
- The builder will look for a `builder.dockerfile` additionally to `Dockerfile`

## Consequences

- The `build` shell script does not only need to be updated in the builder github repository, but also in all consumers of the builder
