# 1. Adopting Architecture Decision Records (ADR) for Garden Linux

Date: 2023-08-23

## Status

Accepted

## Context

To ensure clarity and traceability of architectural decisions in Garden Linux, we recognized the need for a structured documentation approach. Refer to [Issue #1742](https://github.com/gardenlinux/gardenlinux/issues/1742) for more details. Please note that, Garden Linux has daily versions, with select versions being designated as "supported". ADRs in Garden Linux reflect the current state and decisions of the repository/branch they reside in. Unless otherwise specified, they do not retroactively apply to past versions that are still supported. 

For more context about ADR itself please refer to https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions

## Decision

We've chosen to adopt the ADR methodology using [adr-tools](https://github.com/npryce/adr-tools) for documenting architectural decisions in Garden Linux. Decisions documented will pertain to the current state of Garden Linux and won't retroactively affect past versions unless explicitly stated in the respective ADR.

## Consequences

The [adr-tools](https://github.com/npryce/adr-tools) will be our primary tool for managing and recording architecture decisions. This will ensure a consistent and traceable record of decisions made throughout the project's lifecycle.
