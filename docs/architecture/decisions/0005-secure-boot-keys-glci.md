# 5. How to handle Secure Boot Keys in glci

**Date:** 2024-12-05

## Status

Accepted

## Context

[Glci](https://github.com/gardenlinux/glci) is the component that's responsible for publishing Garden Linux release artifacts.
As of December 2024, the execution runtime for glci is [Concourse](https://concourse-ci.org), but this is not relevant for the scope of this document.

Glci makes use of *release manifest* files which describe all relevant aspects of a Garden Linux release.

Secure boot (see [Wikipedia](https://en.wikipedia.org/wiki/UEFI#Secure_Boot), [Debian Wiki](https://wiki.debian.org/SecureBoot)) is a cryptographic method designed to ensure the operating system image has not been tampered with by a third party.
For secure boot to work, public keys/certificates are needed to boot an os image.
Those either need to be shipped with the PCs UEFI firmware or manually provided.

Since the certificates Garden Linux uses are not shipped by default, those certificates are also a relevant aspect of a Garden Linux release.

This ADR describes various options for how secure boot keys could be referenced in release manifests.

## Options Considered

1. Embed certificates into release manifest
   - embedded as base64 encoded string in a new top level key
2. Upload key file per release, reference key in release manifest as regular file
3. Use keys from GitHub repo with some sort of implicit mapping

## Decision

We go with option 2.
Keys are uploaded together with other build artifacts to the s3 bucket.
The release manifest is extended to contain the paths to the certificates.

## Consequences

- Each release has a clearly identified key, no ambiguity about the correct key
  - With option 3, there might be guesswork about which key fits which image, both options 1 and 2 provide ways to audit an older image
- We duplicate the key files, which might be confusing to people who are not aware of the decision
- Clients need to be aware that with option 2 they need to download multiple files, which are unambiguously identified by their name
- Option 2 does not require changes in how glci parses or works with manifest files
- Option 2 does create checksums for key files automatically
