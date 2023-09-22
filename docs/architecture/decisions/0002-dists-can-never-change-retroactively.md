# 2. Distributions Can Never Change Retroactively

**Date:** 2023-09-22

## Status

Accepted (for the GitHub package pipeline)

## Context

The Garden Linux apt repository produces daily distributions. 
These distributions are assembled through a dedicated package repository pipeline. 
Garden Linux maintainers define the package specifications for upcoming apt distributions.

## Decision

Apt distributions, identified by their version numbers, are immutable. They cannot be altered once established. Essentially, when a distribution is named with a specific version, its contents remain unchanged.

## Consequences

1. Introduction of the dynamic Garden Linux apt distribution named `next` 
2. This `next` distribution is adaptable and can undergo changes at any given moment, ensuring it always encompasses the most recent package iterations.
3. When creating a `major.0` release, the existing state of `next` is utilized. 