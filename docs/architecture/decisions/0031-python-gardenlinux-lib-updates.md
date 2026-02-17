# 31. Mandatory gl-s3 --dry-run Regression Testing for python-gardenlinux-lib Updates

Date: 2026-02-13

## Status

Accepted

## Context

`python-gardenlinux-lib` is used in the publish step to generate S3 artifacts and metadata consumed by GLCI.

The publish step consumes the images and the corresponding `*.release` file produced by the builder. It uploads the images to S3 together with the generated metadata singles YAML.

In the past, updates to `python-gardenlinux-lib` merged into `gardenlinux/main` have caused regressions during patch releases. These were typically not crashes but subtle structural or semantic changes in the generated metadata singles YAML, breaking downstream expectations in GLCI.

Once merged into `main`, the library becomes part of the release critical path for:
- future major releases
- patch releases of currently maintained versions

## Decision

Any PR in `gardenlinux` that updates `python-gardenlinux-lib` must pass a regression test using `gl-s3 --dry-run`.

The test validates that the generated metadata singles YAML remains compatible across a defined matrix of releases and flavours.

A library update may not be merged unless this validation succeeds.

## Validation Matrix

### Release Coverage

The test must include:
- the latest released minor version tag for each maintained release
- the current HEAD of each maintained `rel-*` branch
- current `main` or comparison against the last nightly baseline

### Flavour Coverage

Validation is performed per flavour.

At minimum, the following representative flavours must be tested:
- baseline flavour
  + e.g. `aws-gardener_prod`
- secure boot + TPM flavour
  + e.g. `aws-gardener_prod_tpm2_trustedboot`
- platform variant flavour
  + e.g. `openstack-metal-gardener_prod` for current and future releases
  + e.g. `openstackbaremetal` for releases 1877 and earlier

The effective validation set is the cross product of selected releases and selected flavours.

## Matching Criteria

For each release and flavour combination:
- the metadata singles YAML must match the expected output
- no unintended structural or semantic changes are allowed

Intentional changes require explicit review and approval and must document their compatibility impact across maintained releases.

No update to `python-gardenlinux-lib` enters `main` without demonstrating stable S3 metadata behavior across maintained release lines and representative flavours.

## Consequences

### Positive

- prevents metadata regressions during patch releases
- makes metadata contract changes explicit
- protects the release critical path

### Cost

- additional effort when updating the library
- increased delay between a new library version and its adoption in `gardenlinux/main`
