# 5. Secure Boot Keys in GLCI

**Date:** 2024-12-05

## Status

Accepted

## Context

- gcli
- release manifest
- secure boot
- how to get new gl versions into gardener

## Options

1. Embed certificates into release manifest (embedded as base64 encoded string in a new top level key)
2. Upload key per release, reference key in release manfist as regular file
3. Use keys from GitHub repo

## Decision

We go with option 2.
Keys are uploaded together with other build artifacts to the s3 bucket.
The release manifest is extended to contain the paths to the certificates with 

## Consequences

- Each release has a clearly identfied key, no ambiguity about the correct key
  - With option 3, there might be guesswork about which key fits which image, both options 1 and 2 provide ways to audit an older image
- We duplicate the key files, which might be confusing to people who are not aware of the decision
- Clients need to be aware that with option 2 they need to download multiple files, which are unambiguously identified by their name
- Option 2 does not require changes in how glci parses or works with manfiest files
- Option 2 does create checksums for key files automatically
