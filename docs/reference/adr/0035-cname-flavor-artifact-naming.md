---
title: "ADR 0035: Canonical Name, Flavor, and Artifact Naming"
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/reference/adr/0035-cname-flavor-artifact-naming.md
github_target_path: docs/reference/adr/0035-cname-flavor-artifact-naming.md
---

# ADR 0035: Canonical Name, Flavor, and Artifact Naming

Date: 2026-06-12

## Status

Accepted

## Context

The terms `cname`, `flavor`, and related identifiers are used across the Garden Linux project — in the builder, the main repository, `python-gardenlinux-lib`, `glci`, and `gardenlinux-update` — but each component has developed its own interpretation. The following inconsistencies exist today:

### `cname`

- **`gardenlinux/builder`**: defines cname as `{feature-encoding}-{arch}-{version}`.
- **`gardenlinux/gardenlinux`**: two conflicting usages within the same repo — `GARDENLINUX_CNAME` in `/etc/os-release` correctly contains `{feature-encoding}-{arch}-{version}` (no commit), matching the builder; but `.build/` output filenames use `{feature-encoding}-{arch}-{version}-{commit}` as their prefix, and this form has informally also been referred to as "the cname" in CI logs and scripts.
- **`python-gardenlinux-lib`**: treats `{flavor}-{arch}-{version}-{commit}` as its primary cname format; a no-commit form exists only as an explicitly labelled workaround[^1]. Consequently, `release_metadata_string` writes `GARDENLINUX_CNAME` including the commit, which contradicts what the builder writes into `/etc/os-release`.
- **`glci`**: uses a version-less and commit-less string as its config-time cname.
- **`gardenlinux-update`**: strips the version from `GARDENLINUX_CNAME` to obtain a prefix for OCI manifest matching => implicitly treating `{feature-encoding}-{arch}-{version}` as the correct cname format.

### `flavor`

- **`gardenlinux/gardenlinux`**: a full build specification (platform + features + arch + build/test/publish metadata) declared in `flavors.yaml`.
- **`glci`**: a `(cloud-provider, cname-string)` config pair.
- **`python-gardenlinux-lib`**: used in two conflicting sub-systems — as the feature-encoding prefix of a cname in `features/parser.py`, and as a row in a build matrix parser in `flavors/parser.py`.
- **`gardenlinux/builder`**: the word is not used at all.

This lack of shared definitions causes confusion, divergent implementations, and subtle bugs when components make different assumptions about what a string contains.

## Decision

### 1. Canonical Name (`cname`)

The **canonical name** (cname) of a build is the minimal, canonically-sorted encoding of the feature set[^2] — and **only** the feature set. Architecture, version, and commit are not part of the cname.

```
cname = {feature-encoding}
```

The cname is derived from the **minimal feature set**: the subset of the resolved feature set whose members have in-degree zero in the dependency graph, i.e. features that are not pulled in transitively by any other selected feature. Only these need to be stated explicitly — all other features in the full feature set are implied.

The minimal features are sorted by **lexicographical topological order** with a type-biased key: platform features sort before elements, elements before flags, and within each group the ordering follows lexicographical topological order of the dependency graph. This is the ordering produced by `networkx.lexicographical_topological_sort` with a type-prefix sort key, as implemented in `builder/parse_features`.

The cname string is assembled from the sorted minimal features as follows: features are concatenated with `-` as separator, except that flag features (which begin with `_`) are joined directly to the preceding component without a leading `-`. This encoding is reversible: given a cname, the minimal feature set can be recovered by replacing every occurrence of `_` with `-_` and splitting on `-`.

Examples:

- Features `{aws, gardener, _prod}` where `aws` is the platform, `gardener` the element, `_prod` the flag → cname = `aws-gardener_prod`
- Features `{container}` → cname = `container`

The word _canonical_ is fitting: the cname is the canonical way to represent a particular set of features in their minimal, consistently-sorted form. It identifies _what_ is being built, independent of where or when. Two builds with the same cname are builds of the same feature set.

### 2. Flavor

A **flavor** is the cname qualified with a target architecture:

```
flavor = {cname}-{arch}
```

The flavor identifies what is being built for which architecture, independent of any particular release version. It is a stable identifier that persists across versions of a build target. This is the natural unit for entries in `flavors.yaml`, for CI job naming, and for any context where the version is tracked separately.

### 3. Versioned Flavor

A **versioned flavor** is the flavor qualified with a version — the string passed to the builder to invoke a build:

```
versioned flavor = {cname}-{arch}-{version}
```

Examples: `aws-gardener_prod-amd64-1877.3`, `container-amd64-1877.3`.

### 4. Artifact Base Name

The **artifact base name** is the versioned flavor plus the short commit hash:

```
artifact base name = {cname}-{arch}-{version}-{short_commit}
```

The artifact base name is the prefix of every file produced under `.build/` by the builder (e.g. `.build/aws-gardener_prod-amd64-1877.3-a1b2c3d4.raw`, `.build/aws-gardener_prod-amd64-1877.3-a1b2c3d4.manifest`). When the working tree is dirty the short commit is replaced by the literal string `local` (e.g. `.build/aws-gardener_prod-amd64-1877.3-local.raw`). It uniquely identifies a specific build run, not just a build target. This is what the gardenlinux repository previously called "the cname" in many places — including CI logs, GitHub Actions workflow outputs, and artifact upload paths. It is also used as the S3 singles metadata key (`meta/singles/{artifact_base_name}`).

### 5. `GARDENLINUX_CNAME` in `/etc/os-release`

`GARDENLINUX_CNAME` MUST contain the cname as defined in section 1 — i.e. the feature encoding only, without architecture, version, or commit hash. This is a change from the current state where `GARDENLINUX_CNAME` contains the full versioned flavor (`{cname}-{arch}-{version}`).

### 6. Summary table

| Term                   | Format                                    | Example                                   |
| ---------------------- | ----------------------------------------- | ----------------------------------------- |
| **cname**              | `{feature-encoding}`                      | `aws-gardener_prod`                       |
| **flavor**             | `{cname}-{arch}`                          | `aws-gardener_prod-amd64`                 |
| **versioned flavor**   | `{cname}-{arch}-{version}`                | `aws-gardener_prod-amd64-1877.3`          |
| **artifact base name** | `{cname}-{arch}-{version}-{short_commit}` | `aws-gardener_prod-amd64-1877.3-a1b2c3d4` |

## Consequences

### Benefits

Having four clearly-bounded terms eliminates the most common source of ambiguity across the project: whether a "cname" includes the commit, the version, or both. Components can now validate their assumptions against this ADR. The distinction between cname (feature-set only, version-independent), flavor (cname plus architecture), and versioned flavor (flavor plus version) cleanly separates what is being built from where and when.



[^1]: See comment at [`cname.py:97`](https://github.com/gardenlinux/python-gardenlinux-lib/blob/5f2338f568762b6fa42fc19d0148a8951fc8e537/src/gardenlinux/features/cname.py#L97): `# Workaround Garden Linux canonical names without mandatory final commit hash`
[^2]: See [ADR 0034](./0034-feature-terminology.md)
