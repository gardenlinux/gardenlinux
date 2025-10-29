# 18. Revert ADR 3 Update the Builder using Dependabot

Date: 2025-10-27

## Status

Accepted

## Context

In ADR [3 Update the Builder using Dependabot](./0003-builder-updates-dependabot.md), we added an indirection to the Garden Linux Builder using a `Dockerfile`.
The intention was to allow keeping the Builder updated using Dependabot.

For various reasons, this workflow was not as useful as anticipated, and the additional complexity turned out to be a problem.
This was a problem mostly when working on release branches of Garden Linux.

## Decision

We reverted the changes that introduced the indirection in the builder via the `Dockerfile`.

This decision is already implemented in the following pull requests:

- https://github.com/gardenlinux/builder/pull/94
- https://github.com/gardenlinux/gardenlinux/pull/2275

## Consequences

- Updates of the Builder image need to be applied manually to the Garden Linux git repo
- The Builder and the Garden Linux build process is simpler to maintain
