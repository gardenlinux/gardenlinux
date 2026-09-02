---
title: "ADR 0038: Public-by-Default Documentation Policy"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/reference/adr/0038-public-by-default-documentation-policy.md
github_target_path: docs/reference/adr/0038-public-by-default-documentation-policy.md
---

# ADR 0038: Public-by-Default Documentation Policy

Date: 2026-08-25

## Status

Draft

## Context

Garden Linux documentation has historically been split across two locations:

- **Public docs** at various git repositories, later aggregated on docs.gardenlinux.org — for users, contributors, and external maintainers.
- **Internal docs** on a private GitHub Enterprise Server — for the core team.

This split caused measurable problems:
- The internal copy was often more up-to-date than the public copy.
- Outside maintainers, contractors and even core team members had to determine, for each topic, which copy was the source of truth.
- The boundary between "internal" and "external" content was implicit and inconsistently applied, making it easy to either over-share or under-share.

## Decision

Every document the project produces is public by default. The public docs are the single source of truth and are available on docs.gardenlinux.org.

The question is no longer "should this be public?" but "what must be redacted to make this public?"

### What stays internal

Only content whose public availability would cause real harm:

- **Credentials and secrets**: tokens, passwords, account names for shared services, signing keys.
- **Internal infrastructure**: private hostnames, IP ranges, infrastructure-as-code that exposes internal topology, deploy endpoints not hardened against public access.
- **Vendor and contractual details**: anything covered by a non-disclosure agreement, partner agreements, or that names specific vendors in a way that creates a relationship obligation.
- **Personal information**: names of individuals where not already public on the org chart, contact details, performance or compensation information.
- **Internal-only processes with no external analog**: workflows that only make sense for someone with the same internal access (for example, "rotate the S3 key in the project vault"), as opposed to "publish a release", which generalizes.

Everything else is public: names of already-public maintainers, role references, public services, design decisions, most runbooks, most release steps.

### Internal docs carry only the delta

If an internal document extends a public one, it is a short supplement — not a parallel copy. It records the internal-only steps that follow a public procedure, links to the internal systems needed to execute those steps, and covers cases where the public document explains a concept but the internal action requires authentication.

When the public document changes, the internal document's pointer to it is reviewed, not duplicated.

If an internal document is not derived from a public one, it lives in the internal docs hub as a dedicated document.

### Marking the handoff in public docs

A public document with internal extensions ends with a short labelled section:

::: warning For Garden Linux maintainers
The additional internal step XYZ is mandatory. This requires authentication; see the [Internal Step XYZ](https://pages.github.tools.sap/gardenlinux/docs/) for details.
:::

The public document must not name individuals or expose internal service identifiers. Linking to the internal docs hub (which is behind existing access controls) is acceptable.

## Consequences

- The public docs are the single source of truth for all documentation the project produces.
- Internal docs exist only to carry the delta from the public version that core team members actually need.
- Outside maintainers and contractors always read the most current version of any document.
- New core team members have one unambiguous source of truth for each topic.
- The effort to maintain two parallel copies of the same content is eliminated.
- A one-time migration effort is required to consolidate existing internal documentation into the new structure.
