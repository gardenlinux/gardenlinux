# 2. Distributions Can Never Change Retroactively

**Date:** 2023-09-22

## Status

Accepted (for the GitHub package pipeline)

## Context

Garden Linux uses the apt package manager and bootstraps via the `repo.gardenlinux.io` apt repository. 
Every Garden Linux version corresponds directly to an apt distribution on this repository, sharing the same name.
For instance, Garden Linux version `934.10` aligns with the `934.10` apt distribution.

The major apt distributions are assembled daily automatically by a GitHub pipeline. 
After the apt distribution (e.g. `1234.0`) is created, the respective Garden Linux version is build by another automated pipeline.

One of the mission statements of Garden Linux is to ensure reproducibility of Garden Linux releases.

## Decision

With the exception of `next` distributions, all apt distributions must be immutable. 
Any apt distribution used to bootstrap its corresponding Garden Linux version (e.g. `1234.0`) should never be altered retroactively.


## Consequences

1. Introduction of the dynamic Garden Linux apt distribution named `next` 
2. This `next` distribution is adaptable and can undergo changes at any given moment, ensuring it always encompasses the most recent package iterations.
3. When creating a `major.0` release, the existing state of `next` is utilized. 

## Notes

- The `today` apt distribution is like a symlink to the current major version of Garden Linux, which must stay unchanged after initial creation.
- The `next` apt distribution serves as the basis for the upcoming major release of tomorrow.