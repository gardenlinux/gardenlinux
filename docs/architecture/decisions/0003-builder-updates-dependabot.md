# 3. Update the Builder using Dependabot

**Date:** 2023-12-11

## Status

Accepted

## Context

The [Garden Linux Builder](https://github.com/gardenlinux/builder) is a containerized solution to build Linux images.
It is used by the upstream Garden Linux project, but it is and can be used by any project needing custom Linux images.

The builder has two artefacts:
- The `build` shell script
- The `ghcr.io/gardenlinux/builder` container image

The `build` script and the `ghcr.io/gardenlinux/builder` container image are automatically updated with new commit to the builder's main branch.

The builder has no concept of semantic versioning so far.

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

The Garden Linux builder versions can be bumped with dependabot and we recommend users to make use of that.

We implement the needed changes to support this, like:

- Tagged releases on GitHub for the builder will be published
  - The builder implements a versioning schema that is orianted at semantic versioning with a major and a minor version
    - The minor version will increase on updates that don't break compatibility between the `build` script and the `ghcr.io/gardenlinux/builder` container image
    - The major versin will increase on updates taht do break compatibility between the `build` script and the `ghcr.io/gardenlinux/builder` container image
- The `build` script will look for a `builder.dockerfile` additionally to `Dockerfile`
- The [`gardenlinux`](https://github.com/gardenlinux/gardenlinux) and [`builder_example`](https://github.com/gardenlinux/builder_example) implement our recommended solution of keeping the builder updated via dependabot
- We recommend new users of the builder to bootstrap their project based on the [`builder_example` repo](https://github.com/gardenlinux/builder_example)

## Consequences

- The `build` script needs to look for a `builder.dockerfile`
- Making major updates via dependabot can't be implemented safley as the `build` script will need to be updated manually
  - For this reason we recommend to disable dependabot for major version upgrades and take care of them manually according to the release notes of major builder releases
