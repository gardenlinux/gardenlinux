# 31. S3 Artifact and Metadata Publishing Contract Between Builder and GLCI

Date: 2026-02-05

## Status

Accepted

## Context

- Build artifacts produced by the Garden Linux builder are to be published and later consumed by GLCI.
- AWS S3 was chosen as the interface between build and consumption:
  + GitHub Actions (or equivalent CI) running the image build upload artifacts and metadata to S3.
  + GLCI consumes artifacts and metadata from S3 asynchronously, potentially long after the build finished.
- For this workflow to be reliable, a **clear, documented interface** is required that specifies:
  + Which files are uploaded
  + Where they are uploaded in S3
  + Which metadata is produced
  + Which builder outputs are authoritative inputs for that metadata
- Currently, the upload to S3 and metadata generation is handled by `python-gardenlinux-lib`.
- Misalignment between builder output and how metadata is derived has caused issues, most notably while consolidating `openstack` / `openstackbaremetal` into `openstack` and `openstack-metal`.
- A clear documented interface between **build artifacts** and **GLCI inputs** is required to avoid future ambiguity and regressions.

This ADR defines that interface.

## Decision

### 1. Authoritative Inputs

The **builder output files** are the sole authoritative inputs for publishing artifacts and metadata to S3.

The task of the upload logic is:

- to upload files to S3, and
- to translate builder output into metadata understood by GLCI.

It must **not**:

- enforce additional assumptions about structure,
- reinterpret semantics,
- or impose constraints beyond what is explicitly defined in this and subsequent ADRs.

---

### 1.1 Release Metadata File (`*.release`)

**Format:** key-value file compatible with `os-release` style

#### Required fields

| Field                            | Meaning                                                          |
| -------------------------------- | ---------------------------------------------------------------- |
| `GARDENLINUX_CNAME`              | Canonical name, uniquely identifying the build target            |
| `GARDENLINUX_VERSION`            | Version string                                                   |
| `GARDENLINUX_COMMIT_ID`          | Commit identifier (may be `local`)                               |
| `GARDENLINUX_COMMIT_ID_LONG`     | Commit hash or `local`                                           |
| `GARDENLINUX_PLATFORM`           | **Single authoritative platform**                                |
| `GARDENLINUX_FEATURES`           | Comma-separated feature list                                     |
| `GARDENLINUX_FEATURES_ELEMENTS`  | Feature elements *(informational only, not used in publishing)*  |
| `GARDENLINUX_FEATURES_FLAGS`     | Feature flags *(informational only, not used in publishing)*     |
| `GARDENLINUX_FEATURES_PLATFORMS` | Feature platforms *(informational only, not used in publishing)* |

#### Optional fields

| Field                          | Meaning              |
| ------------------------------ | -------------------- |
| `GARDENLINUX_PLATFORM_VARIANT` | Platform sub-variant |

#### Platform semantics

- `GARDENLINUX_PLATFORM` is the **one and only platform value** used for publishing.
- This guarantees exactly one platform value, or a deliberate “frankenstein” value if a non-standard image was built.
- `GARDENLINUX_FEATURES_PLATFORMS` **must not** be used as input to any publishing or routing decision:
  + It may contain zero, one, or multiple values.
  + It reflects feature graph structure, not publishing semantics.

### 1.2 Requirements File (`*.requirements`)

**Format:** simple key-value file (one `key=value` entry per line).

#### Fields

| Field        | Type   | Required | Meaning                                                                                       |
| ------------ | ------ | -------- | --------------------------------------------------------------------------------------------- |
| `arch`       | string | yes      | Architecture of the image                                                                     |
| `uefi`       | bool   | no       | UEFI is required (not merely supported, for hybrid legacy and UEFI images this must be false) |
| `secureboot` | bool   | no       | Secure Boot is required                                                                       |
| `tpm2`       | bool   | no       | TPM 2.0 is required                                                                           |

For non-required fields, the default value is `false`.

### 1.3 Artifact Files

- All remaining files in the artifact directory.
- Each file represents a build output to be uploaded to S3.
- Artifact files are opaque to the publishing contract; their internal structure is not interpreted.

## 2. Metadata Assembly

Exactly one metadata document is produced per build, referred to as the *singles metadata*.

### 2.1 Metadata Fields

The metadata document contains the following information:

| Metadata Key        | Source                                           |
| ------------------- | ------------------------------------------------ |
| `platform`          | `GARDENLINUX_PLATFORM`                           |
| `platform_variant`  | `GARDENLINUX_PLATFORM_VARIANT` (if present)      |
| `architecture`      | `arch` from requirements file                    |
| `version`           | `GARDENLINUX_VERSION`                            |
| `gardenlinux_epoch` | Major version component of `GARDENLINUX_VERSION` |
| `build_committish`  | `GARDENLINUX_COMMIT_ID_LONG`                     |
| `build_timestamp`   | Filesystem timestamp of the release file         |
| `modifiers`         | Parsed list from `GARDENLINUX_FEATURES`          |
| `require_uefi`      | `uefi` from requirements file                    |
| `secureboot`        | `secureboot` from requirements file              |
| `tpm2`              | `tpm2` from requirements file                    |
| `paths`             | List of uploaded artifact descriptors            |
| `s3_bucket`         | Target S3 bucket                                 |
| `s3_key`            | S3 path of the metadata document                 |

The artifact descriptors in `paths` are of the form:

```yaml
- name: <artifact_base_name>.<artifact_file_extension>
  suffix: .<artifact_file_extension>
  md5sum: <md5sum_of_artifact>
  sha256sum: <sha256sum_of_artifact>
  s3_key: <path_to_uploaded_artifact_object>
  s3_bucket_name: <s3_bucket>
```

No additional interpretation or normalization of these values is performed beyond format translation.

## 3. S3 Layout

### 3.1 Artifact Files

- Artifact files are uploaded to S3 under implementation-defined paths.
- Their placement is opaque to GLCI and not part of this contract.
- The path to find the artifacts at is defined in the artifact descriptor keys `s3_bucket_name` and `s3_key`

### 3.2 Singles Metadata Document

- Exactly one metadata document is uploaded per build.
- Location (fixed and stable): `meta/singles/<artifact_base_name>`
- Format: YAML
- This document is the **primary entry point for GLCI** to discover build artifacts and associated metadata.

## 4. Responsibilities and Non-Responsibilities

### Responsibilities of the Upload Logic

- Upload build artifacts to S3.
- Translate builder output into metadata consumable by GLCI.
- Preserve builder intent and semantics exactly as expressed in the release file and requirements file.

### Explicit Non-Responsibilities

- Enforcing assumptions about naming conventions beyond documented extraction rules.
- Inferring architecture from the canonical name or any other source than the requirements file.
- Inferring platform semantics from feature graphs.

## Consequences

- The interface between builder output and GLCI input is explicit and stable.
- Architecture handling is unambiguous and future-proof.
- Platform handling is unambiguous and future-proof.
- Builder semantics are preserved without reinterpretation.
- Future refactors of publishing logic can be validated against this ADR.
- Ambiguity and hidden assumptions in metadata generation are eliminated.
