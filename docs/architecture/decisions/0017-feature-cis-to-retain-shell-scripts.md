# 17. Retain Shell-Based CIS Implementation (No Custom Python Rewrite)

Date: 2025-10-24

## Status

Accepted

## Context

 - The CIS hardening feature in Garden Linux currently executes upstream shell scripts from ovh/debian-cis. 
 - There is a need to formally document why we intentionally keep this shell-based approach instead of rewriting and owning a custom implementation in Python.

## Key considerations:

 - Rewriting CIS logic into Python would require full long-term ownership of hundreds of evolving rule checks.

 - ovh/debian-cis is actively maintained upstream — following industry-standard CIS baseline updates.

 - We intentionally avoid duplicating upstream effort and introducing maintenance obligations that do not provide strategic value.

 - Our responsibility is limited to packaging, integrating, and executing upstream logic safely, not to reimplement or maintain CIS rule definitions.

 - To ensure architectural clarity and traceability, this is documented as a formal design decision (marker).

## Decision

Garden Linux will retain the upstream shell-based CIS implementation without rewriting or owning the CIS logic internally as an Exception.
A design decision marker is created to clearly document the intentional choice.

The CIS hardening tests will be hence executed as-is from upstream.