# 5. How to handle Secure Boot Keys in glci

**Date:** 2024-12-05

## Status

Accepted

## Context

[Glci](https://github.com/gardenlinux/glci) is the component that's responsible for publishing Garden Linux release artifacts to hyperscalers, in particular AWS, Azure, GCP, AliCloud and OpenStack.
As of December 2024, the execution runtime for glci is [Concourse](https://concourse-ci.org), but this is not relevant for the scope of this document.

Glci makes use of *release manifest* files which describe all relevant aspects of a Garden Linux release.

Secure boot (see [Wikipedia](https://en.wikipedia.org/wiki/UEFI#Secure_Boot), [Debian Wiki](https://wiki.debian.org/SecureBoot)) is a cryptographic method designed to ensure the operating system image has not been tampered with by a third party.
For secure boot to work, public keys/certificates are needed to boot an os image.
Those either need to be shipped with the PCs UEFI firmware or manually provided.
A key bundle for secure boot consists of the platform key (pk), the key exchange key database (keks), the authorized keys database (dbs) and the disallowed key database (dbxs).

Since the certificates Garden Linux uses are not shipped by default, those certificates are also a relevant aspect of a Garden Linux release and the release process. With regards to publishing Garden Linux to hyperscalers, glci must import the signing (public) key alongside the image itself to the hyperscalers.

For glci to locate the proper key that belongs to a given release, it should be referenced in the respective release manifest.

This ADR describes various options for how secure boot keys could be referenced in release manifests.

## Options Considered

1. Embed certificates into release manifest
   - embedded as base64 encoded string in a new top level key
2. Upload pk, keks, dbs and (optionally) dbxs key files per release, reference keys in release manifest as regular file
3. Use keys from GitHub repo with some sort of implicit mapping

## Decision

We go with option 2.
Keys are uploaded together with other build artifacts to the s3 bucket.
The keys will be referenced through the `paths` section of the release manifest like all other files belonging to the release, identified by their extensions. There will be no change to the general structure of the release manifest.

## Consequences

- Each release has a clearly identified key, no ambiguity about the correct key
  - With option 3, there might be guesswork about which key fits which image, both options 1 and 2 provide ways to audit an older image
- We duplicate the key files, which might be confusing to people who are not aware of the decision
- Clients need to be aware that with option 2 they need to download multiple files, which are unambiguously identified by their name
- Option 2 does not require changes in how glci parses or works with manifest files
- Option 2 does create checksums for key files automatically
