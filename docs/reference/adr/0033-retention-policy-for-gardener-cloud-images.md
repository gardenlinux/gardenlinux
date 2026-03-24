# 33. Retention policy for Gardener cloud images

Date: 2026-04-13

## Status

Accepted

## Context

This ADR covers the public cloud images, which we provide for Gardener. These images are currently not available to the general public, because of technical limitations (limited to a namespace). In future we also want to provide public cloud images that can be consumed by everybody. An additional policy that covers these public images would then be needed.

The amount of cloud images you can provide on AWS for EC2 instances is limited. Per default only _5_ public images per region are allowed ([source](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ami-quotas.html)). For us this limit was increased to _150_. However, we still reached it in 03/2026, and several times before, so a manual clean up of old images was needed.

At the moment each release consumes six slots. For the two supported architectures (_x64_ and _arm64_) we have one image for each of the current variants (_regular_, _usi_, and _trustedboot_). This number will increase in future with for example the new _FIPS_-related images.

To avoid upload errors, we have to reduce the amount of slots we consume.

We are currently not aware of such limits for the other providers, but we will still apply this new retention policy to all cloud providers, we serve with public images for Gardener. Deleting old images that are no longer supported by us and will most likely be vulnerable to CVEs is a good idea in general.

We can only delete images when they are no longer used by Gardener's customers. Otherwise they would no longer be able to create new nodes without running into errors. Existing nodes would not be influenced by the deletion.

There are different mechanisms in Gardener, which define how long a version needs to be available. The landscape-YAML file defines which GL versions are supported and when they will expire, but these settings can be overwritten by customers. Hence, a hybrid approach is needed that also detects if a version is no longer used (not seen for a while). Only then it can be marked for deletion.

## Decision

We will automatically delete no longer needed public images of Garden Linux on all supported cloud providers. A version is no longer needed, if we no longer support it and the Gardener team says that it is no longer used by customers. For this purpose, Gardener will provide us an automatic mechanism that tells us, which versions have expired and are no longer used.

## Consequences

We have to wait until Gardener can provide us the necessary mechanism to inform us about expired and no longer used Garden Linux versions. With this mechanism GLCI has to implement a solution that automatically performs the required clean ups for the no longer needed images.
