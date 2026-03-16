# 33. Retention policy for public cloud images

Date: 2026-03-05

## Status

Accepted

## Context

The amount of public cloud images you can provide on AWS for EC2 instances is limited. Per default only _5_ public images per region are allowed ([source](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ami-quotas.html). For us this limit was increased to _150_. However, we still reached it in 03/2026, and several times before, so a manual clean up of old images was needed.

At the moment each release consumes six slots. For the two supported architectures (_x64_ and _arm64_) we have one image for each of the current variants (_regular_, _usi_, and _trustedboot_). This number will increase in future with for example the new _FIPS_-related images.

To avoid upload errors, we have to reduce the amount of slots we consume.

We are currently not aware of such limits for the other providers, but we will still apply this new retention policy to all cloud providers, we serve with public images. Because deleting old images that are no longer supported by us and will most likely be vulnerable to CVEs is a good idea in general.

Gardener has ensured us that they do not use old versions of Garden Linux. The clusters are migrated automatically in a timely manner to new supported versions.

## Decision

We will automatically delete old public images of Garden Linux on all supported cloud providers. An image has to be deleted three months after we have stopped supporting its version.

A buffer time of three month before the deletion should give all of our users enough time to migrate to a supported version.

## Consequences

We have to communicate this retention policy transparently to our users. Also GLCI has to implement a mechanism to automatically perform the required clean ups.
