---
title: "ADR 0034: Defining python-gardenlinux-lib as an internal tool"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/reference/adr/0034-feature-terminology.md
github_target_path: docs/reference/adr/0034-feature-terminology.md
---

# 34. Garden Linux Feature Terminology

Date: 2026-06-12

## Status

Accepted

## Context

Garden Linux images are assembled from composable units called *features*. The main Garden Linux repository, `python-gardenlinux-lib`, and downstream tooling all use the terms *feature*, *platform*, *element*, and *flag*, but without a shared, written definition. This has led to inconsistencies — most notably in how `platform` is understood (a feature sub-type in the build system, a cloud provider name in publishing tooling, and an OCI image spec concept in update tooling) and in what the `GARDENLINUX_PLATFORM` and `GARDENLINUX_FEATURES_PLATFORMS` keys in `/etc/os-release` mean.

This ADR establishes shared definitions for these terms.

## Decision

### 1. Feature

A **feature** is the atomic building block of a Garden Linux image. It is a named directory inside the `features/` tree of the Garden Linux repository. A feature must contain an `info.yaml` file that declares at minimum its `type`. It may also contain package lists, file overlays, and build time scripts that are applied during the build.

Features are not independent: they form a **directed acyclic graph (DAG)**. Each feature may declare:

- `features.include`: other features that are automatically pulled in when this feature is selected.
- `features.exclude`: other features that are removed from the build if they were only transitively included (explicitly including an excluded feature is a hard build error).

The DAG is resolved and validated at build time. For the precise mechanics of how feature content (package lists, file overlays, build time scripts such as `exec.config` and `exec.early`) is applied during the build, this ADR defers to the `gardenlinux/builder` documentation.[^1]

### 2. Feature types

Every feature has exactly one type, declared in its `info.yaml`. The type is primarily a descriptive and user-facing classification; it does not change how the feature participates in the DAG or how its content is applied during the build. The three types are:

#### 2.1 `platform`

A feature of type `platform` represents a deployment target — the combination of hardware, firmware, and cloud or hypervisor environment the image is intended to run on. Examples: `aws`, `azure`, `gcp`, `kvm`, `baremetal`, `container`.

In a well-formed build exactly one platform feature SHOULD be present. If zero or more than one platform feature is present after DAG resolution, the builder will by default treat this as an error. Explicitly opting in via `--allow-frankenstein` downgrades this to a warning and allows the build to continue; the resulting image is referred to as a **frankenstein image** and is not considered a supported configuration.

#### 2.2 `element`

A feature of type `element` represents a functional component or capability added on top of the platform. Elements are composable and multiple elements may be present in a single build. Examples: `gardener`, `server`, `cloud`, `cis`, `firewall`.

#### 2.3 `flag`

A feature of type `flag` represents a lightweight modifier. Flags are distinguished by a leading underscore in their name (e.g. `_prod`, `_fips`, `_trustedboot`). They are intended for minor behavioural changes that do not warrant a full element and SHOULD NOT include other features.

### 3. Feature set

The **feature set** of a build is the complete set of features present after DAG resolution — the transitive closure of all included features minus all excluded ones. This is distinct from the *minimal* feature set used for naming (see [ADR 0035](0035-cname-flavor-artifact-naming.md)).

### 4. `GARDENLINUX_FEATURES_*` and `GARDENLINUX_PLATFORM` in `/etc/os-release`

The builder exposes the resolved feature set to feature scripts via environment variables. These are written verbatim into `/etc/os-release` by `features/base/exec.config`:

| Key | Content |
|---|---|
| `GARDENLINUX_FEATURES` | Comma-separated list of all features in the resolved feature set |
| `GARDENLINUX_FEATURES_PLATFORMS` | Comma-separated list of all features of type `platform` |
| `GARDENLINUX_FEATURES_ELEMENTS` | Comma-separated list of all features of type `element` |
| `GARDENLINUX_FEATURES_FLAGS` | Comma-separated list of all features of type `flag` |
| `GARDENLINUX_PLATFORM` | The single authoritative platform identifier for this image |

`GARDENLINUX_PLATFORM` is derived from `GARDENLINUX_FEATURES_PLATFORMS` as follows: if exactly one platform feature is present, `GARDENLINUX_PLATFORM` is set to that feature's name. If more than one platform feature is present (frankenstein build), `GARDENLINUX_PLATFORM` is set to the literal string `frankenstein`.

`GARDENLINUX_PLATFORM` is always a single token and is the value to be used for all platform-routing decisions (publishing, testing, image naming). `GARDENLINUX_FEATURES_PLATFORMS` is informational and reflects the raw feature graph output; it MUST NOT be used as input to publishing or routing decisions (see also [ADR 0031](0031-builder-glci-interface.md)).

## Consequences

### Benefits

A shared written definition eliminates the ambiguity that has caused silent bugs (e.g. the `openstackbaremetal` regression described in [ADR 0020](0020-enforce-single-platform-by-default-in-builder.md)) and divergent implementations. All tooling can now be validated against a single reference.

### Impact on individual components

#### `gardenlinux/builder`

No functional changes required. The builder's existing behaviour is consistent with the definitions in this ADR. Documentation in `docs/features.md` should be updated to cross-reference this ADR.

#### `gardenlinux/gardenlinux`

`features/base/exec.config` already implements the `GARDENLINUX_PLATFORM` / frankenstein logic correctly. `features/README.md` contains outdated content (notably listing `metal` as a platform when it is in fact an element; `baremetal` is the platform) and must be updated to match this ADR.

#### `gardenlinux/python-gardenlinux-lib`

This library contains a parallel implementation of the feature type system. Several adjustments are required:

- The `CName.platform` property returns `platforms[0]` and falls back to a `frankenstein` constant controlled by the `GL_ALLOW_FRANKENSTEIN` environment variable. This logic duplicates `features/base/exec.config` but with different environment variable names and without being tied to the builder's `BUILDER_FEATURES_PLATFORMS` output. It should be aligned: the single-platform-or-frankenstein resolution belongs in the build layer (i.e. `exec.config`), not in a parsing library. The library should read `GARDENLINUX_PLATFORM` from release files rather than re-deriving it from the feature list.
- The library's `Parser.filter_as_dict()` correctly separates features by type, which is consistent with this ADR and can be retained.
- The `GL_ALLOW_FRANKENSTEIN` and `GL_ALLOW_MULTIPLE_PLATFORMS` environment variables in the library are not defined by the builder and should be removed in favour of reading the already-resolved `GARDENLINUX_PLATFORM` value from the release file.

#### `gardenlinux/glci`

glci uses the word `platform` to mean cloud provider (e.g. `"AWS"`, `"Azure"`). This is a distinct concept from the feature-type `platform` defined here. To avoid confusion it may be worth considering renaming glci's internal config field (e.g. to `cloud_provider` or `target`) in a future cleanup, though this is not required for correctness given that glci reads `GARDENLINUX_PLATFORM` from the manifest and that contract is defined in [ADR 0031](0031-builder-glci-interface.md).

#### `gardenlinux/gardenlinux-update`

No changes required. This tool reads `GARDENLINUX_PLATFORM` from `/etc/os-release` indirectly (via the OCI index annotations populated from the manifest). The meaning is consistent with this ADR.



[^1]: https://github.com/gardenlinux/builder/blob/main/docs/features.md
