# 12. Remove the Firecracker Feature from Garden Linux

Date: 2025-10-01

## Status

Accepted

## Context

[firecracker](https://firecracker-microvm.github.io) is a micro-vm technology built for serverless computing.

Garden Linux carries the `firecracker` feature for years now with no known users.
From time to time this causes maintenance effort, for example when migrating the tests to the new testing framework, or when we adapt to a new Linux kernel version.

## Decision

We remove the `firecracker` feature from Garden Linux, and the respective configuration from the `package-linux` repo.

## Consequences

- Potential users who want to use Garden Linux with firecracker can't do that
- We reduce maintenance effort for Garden Linux maintainers
- If ever we want to support firecracker, the old code is still available via git history
