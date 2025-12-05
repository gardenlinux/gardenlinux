# 20. Maintain CHANGELOG for python-gardenlinux-lib

Date: 2025-11-04

## Status

Proposed

## Context

Python gardenlinux library is used in at least 17 different github workflows at the time of writing of this ADR
- for generating release notes
- for pushing OCI artifacts to a registry
- for parsing flavors
and more.

As more and more parts of the gardenlinux release process rely on the library, a better release process --
with a structured CHANGELOG as its cornerstone -- is a neccessary step:

- to avoid unwanted incidents caused by updates of the library and
- to improve github workflows by better utilizing new or underused features of the library

## Decision

With every version bump of the gardenlinux python library, we will update the CHANGELOG file in its repository, so that
a pull request containing the actual version change also contains an update of the CHANGELOG.
CHANGELOG will contain the description of the changes made since the previous version of the library,
with an emphasis on the library *use*. The format of the file is described here: https://common-changelog.org.

Changelog updates are not to be generated automatically, although helper tools (LLMs, git commit message parsers etc)
can be used to *assist* in writing changelog text.

Changelog will be covered by the usual code review process, so that a person not involved in the latest *code changes*
can validate if the changelog text is clear and useful.

Changelog should be maintaned by humans for humans.

## Consequences

The library release process becomes more structured and easier to follow,
especially for troubleshooting potential incidents where the library can be involved.

On the other side, keeping changelog in a good shape will require additional efforts from a developer aiming
to release a new library version and from a reviewer of a corresponding pull request. Hopefully with experience these
efforts would become reasonably small.
