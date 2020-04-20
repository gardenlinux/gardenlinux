# gardenlinux versioning and repository layout (proposal)

gardenlinux will be built in several flavours, and in different versions / codelines. Therefore, we
need to find a suitable scheme for versions and (build result) repository layout.

Note: this is a _draft_ / _proposal_

## Versioning Schema

- use (relaxed) semver, as done for Gardener
  - [0](https://github.com/gardener/cc-utils/blob/master/version.py#L40)
  - two-tuples of integers should be sufficient (<major>.<patch>)
- count days since "gardenlinux epoch" for major version
  - as suggested, use 2020-04-01 as day-0
- first version built on any day: `<days-since-gl-epoch>.0`
- subsequent versions get incremented patch-levels
  - both for builds on same day, and patch-releases done later
- append hash digest of source-repository commit used for building (for snapshots)

### Examples

First build on 2020-04-11: `10.0`
Second build on 2020-04-11: `10.1`
Patch-Release based on `11.x` (anytime later): `10.2`


# Release Version Semantics

Each release version of gardenlinux consists of multiple artifacts (e.g. for different hyperscalers).
A release is considered to be _complete_ iff all artifacts have been successfully built, published
(and possibly validated). Only complete release versions of gardenlinux should be published to
Release Channels.

# Release Channels

gardenlinux will emit a stream of release versions. Release Channels are used to expose release
versions adhering to a certain semantics and qualities. Release Channels are semantically similar
to symbolic links; they always point to an existing gardenlinux release version.

Proposed Channels: TBD


# Repository Layout

Semantically, the release repository is structured equivalent to a directory tree in a file system
featuring symbolic links.

- use architecture (e.g. amd64, ppc64, ..) as topmost directory
  - follow Debian's architecture names
- place build artifacts in a flat list, grouped by naming convention

*Naming convention*

`<arch>/<platform>-<extensions>-<modifiers>-<version>-<artifactname>`

- arch: architecture as defined by Debian
- platform: target platform (e.g. `aws`, `gcp`, `azure`, ..)
- extensions: list of extensions (e.g. `ghost`, `chost`, ..)
- modifiers: list of modifiers (e.g. `prod`)
- version: epoch + patch-level + commit-hash


## Example

```
amd64/metal-ghost-prod-18.0-deadbeef-rootf.tar.xz
amd64/metal-ghost-prod-18.0-deadbeef-manifest
amd64/metal-chost-prod-18.0-deadbeef-rootf.tar.xz
amd64/metal-chost-prod-18.0-deadbeef-manifest
amd64/metal-vhost-prod-18.0-deadbeef-rootf.tar.xz
amd64/metal-vhost-prod-18.0-deadbeef-manifest
amd64/aws-ghost-prod-18.0-deadbeef-rootf.tar.xz
amd64/aws-ghost-prod-18.0-deadbeef-manifest
amd64/aws-chost-prod-18.0-deadbeef-rootf.tar.xz
amd64/aws-chost-prod-18.0-deadbeef-manifest
amd64/azure-ghost-prod-18.0-deadbeef-rootf.tar.xz
amd64/azure-ghost-prod-18.0-deadbeef-manifest
amd64/azure-chost-prod-18.0-deadbeef-rootf.tar.xz
amd64/azure-chost-prod-18.0-deadbeef-manifest
amd64/gcp-ghost-prod-18.0-deadbeef-rootf.tar.xz
amd64/gcp-ghost-prod-18.0-deadbeef-manifest
amd64/gcp-chost-prod-18.0-deadbeef-rootf.tar.xz
amd64/gcp-chost-prod-18.0-deadbeef-manifest
amd64/ali-ghost-prod-18.0-deadbeef-rootf.tar.xz
amd64/ali-ghost-prod-18.0-deadbeef-manifest
amd64/ali-chost-prod-18.0-deadbeef-rootf.tar.xz
amd64/ali-chost-prod-18.0-deadbeef-manifest
amd64/openstack-ghost-prod-18.0-deadbeef-rootf.tar.xz
amd64/openstack-ghost-prod-18.0-deadbeef-manifest
amd64/openstack-chost-prod-18.0-deadbeef-rootf.tar.xz
amd64/openstack-chost-prod-18.0-deadbeef-manifest
amd64/vmware-ghost-prod-18.0-deadbeef-rootf.tar.xz
amd64/vmware-ghost-prod-18.0-deadbeef-manifest
amd64/vmware-chost-prod-18.0-deadbeef-rootf.tar.xz
amd64/vmware-chost-prod-18.0-deadbeef-manifest
amd64/kvm-ghost-prod-18.0-deadbeef-rootf.tar.xz
amd64/kvm-ghost-prod-18.0-deadbeef-manifest
amd64/kvm-chost-prod-18.0-deadbeef-rootf.tar.xz
amd64/kvm-chost-prod-18.0-deadbeef-manifest
amd64/gcp-chost-prod-18.0-deadbeef-rootf.tar.xz
amd64/gcp-chost-prod-18.0-deadbeef-manifest
```
