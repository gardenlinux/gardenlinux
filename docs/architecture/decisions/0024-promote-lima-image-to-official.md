# 24. Promote Lima Image to Official Garden Linux Product

Date: 2025-11-21

## Status

Accepted

## Context

Garden Linux currently provides a [lima](https://lima-vm.io) image, but it is not officially recognized as part of the supported product portfolio.
Lima images are currently published in a separate pipeline on a best effort-basis and are not considered part of the product.

## Product Feasibility and Viability Assessment

Before promoting the lima image to an official product, several questions need to be addressed:

- **Maintenance Effort:** Expected maintenance effort is low to moderate. There might be issues when new versions of lima are incompatible with our software stack, or when image upload or publishing fails.
- **Testing:** No automated tests exist yet. It would be possible to create and boot lima vms in the pipeline for verification purposes, and tooling to more easily build and boot lima vms for Garden Linux developers can be implemented.
- **Repository Packages:** `cloud-init` and `sshfs` are required for a functional lima image. Both are already part of our repo. 
- **Tooling Requirements:** Based on decision [23. Providing Garden Linux Images for Lima-VM via Containerized YAML Generator](https://github.com/gardenlinux/gardenlinux/pull/3913), the only required extra tooling is the container image for generating lima manifest files. Other approaches might have required extra tooling in our release workflow, or modification of the Builder.
- **User Adoption:** So far, no external users are known, but potentially this is useful both for Garden Linux developers and for potential users.

## Decision

The *lima* image is an official part of the Garden Linux product offering.

## Consequences

- The lima image will receive the same level of support and maintenance as other official Garden Linux images.
- Documentation and release processes will be updated to include the lima image.
- Additional resources may be required for maintenance, testing, and user support.
- The Garden Linux user community will benefit from an officially supported local VM image, improving developer experience and adoption.
