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

### Examples

First build on 2020-04-10: `10.0`
Second build on 2020-04-10: `10.1`
Patch-Release based on `10.x` (anytime later): `10.2`


# Release Version Semantics

Each release version of gardenlinux consists of multiple artifacts (e.g. for different hyperscalers).
A release is considered to be _complete_ iff all artifacts have been successfully built, published
(and possibly validated). Only complete release versions of gardenlinux should be published to
Release Channels.

# Release Channels

gardenlinux will emit a stream of release versions. Release Channels are used to expose release
versions adhering to a certain semantics and qualities. Release Channels are semantically similar
to symbolic links; they always point to an existing gardenlinux release version.

Proposed Channels:

- greatest - self-explanatory
- stable   - follow Debian's stable (details TBD)

*Proposal for initial setup*

Start with `greatest`, only.

# Repository Layout

Semantically, the release repository is structured equivalent to a directory tree in a file system
featuring symbolic links.

```
version/<version>/      # release artifacts reside here in a flat list
channel/<channel_name>  # channels point to release versions
```

## Example (omitting file-names)

```
version/20.0/...
version/21.0/...
version/21.1/...
version/22.0/...

channel/greatest       # symlink to versions/22.0/
channel/stable         # symlink to versuins/21.1/
```

## Artifact / File Names

- group all corresponding files as a flat list within version directory
- apply a naming convention to make names constructrable

`gardenlinux-<arch>-<iaas>-<flavour><ext>`

- gardenlinux: hardcoded, common prefix (smurf naming..)
- arch: computer architecture (x86_64, arm64, ppc64, hpia64, ..)
- iaas: hyperscaler typw (aws, gcp, ..)
- flavour: gardenlinux flavour(s) (dev, prod, ..)
- ext: technical packaging format (.raw, .tar, ..)


## Example (including file names)

```
version/12.3/gardenlinux-x86_64-aws-prod.raw
version/12.3/gardenlinux-x86_64-aws-prod.tar.gz
version/12.3/gardenlinux-x86_64-aws-dev.raw
version/12.3/gardenlinux-x86_64-aws-dev.tar.gz
version/12.3/gardenlinux-x86_64-azure-prod.raw
version/12.3/gardenlinux-x86_64-azure-prod.tar.gz
version/12.3/gardenlinux-x86_64-azure-dev.raw
version/12.3/gardenlinux-x86_64-azure-dev.tar.gz
version/12.3/gardenlinux-x86_64-gcp-prod.raw
version/12.3/gardenlinux-x86_64-gcp-prod.tar.gz
version/12.3/gardenlinux-x86_64-gcp-dev.raw
version/12.3/gardenlinux-x86_64-gcp-dev.tar.gz
version/12.3/gardenlinux-x86_64-kvm-prod.raw
version/12.3/gardenlinux-x86_64-kvm-prod.tar.gz
version/12.3/gardenlinux-x86_64-kvm-dev.raw
version/12.3/gardenlinux-x86_64-kvm-dev.tar.gz
version/12.3/gardenlinux-x86_64-openstack-prod.raw
version/12.3/gardenlinux-x86_64-openstack-prod.tar.gz
version/12.3/gardenlinux-x86_64-openstack-dev.raw
version/12.3/gardenlinux-x86_64-openstack-dev.tar.gz
version/12.3/gardenlinux-x86_64-vmware-prod.raw
version/12.3/gardenlinux-x86_64-vmware-prod.tar.gz
version/12.3/gardenlinux-x86_64-vmware-dev.raw
version/12.3/gardenlinux-x86_64-vmware-dev.tar.gz
version/12.3/gardenlinux-arm64-aws-prod.raw
version/12.3/gardenlinux-arm64-aws-prod.tar.gz
version/12.3/gardenlinux-arm64-aws-dev.raw
version/12.3/gardenlinux-arm64-aws-dev.tar.gz
version/12.3/gardenlinux-arm64-azure-prod.raw
version/12.3/gardenlinux-arm64-azure-prod.tar.gz
version/12.3/gardenlinux-arm64-azure-dev.raw
version/12.3/gardenlinux-arm64-azure-dev.tar.gz
version/12.3/gardenlinux-arm64-gcp-prod.raw
version/12.3/gardenlinux-arm64-gcp-prod.tar.gz
version/12.3/gardenlinux-arm64-gcp-dev.raw
version/12.3/gardenlinux-arm64-gcp-dev.tar.gz
version/12.3/gardenlinux-arm64-kvm-prod.raw
version/12.3/gardenlinux-arm64-kvm-prod.tar.gz
version/12.3/gardenlinux-arm64-kvm-dev.raw
version/12.3/gardenlinux-arm64-kvm-dev.tar.gz
version/12.3/gardenlinux-arm64-openstack-prod.raw
version/12.3/gardenlinux-arm64-openstack-prod.tar.gz
version/12.3/gardenlinux-arm64-openstack-dev.raw
version/12.3/gardenlinux-arm64-openstack-dev.tar.gz
version/12.3/gardenlinux-arm64-vmware-prod.raw
version/12.3/gardenlinux-arm64-vmware-prod.tar.gz
version/12.3/gardenlinux-arm64-vmware-dev.raw
version/12.3/gardenlinux-arm64-vmware-dev.tar.gz
```
