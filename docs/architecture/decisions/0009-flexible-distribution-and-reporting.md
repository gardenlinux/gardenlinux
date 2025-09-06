# ADR 0009: Flexible Distribution and Reporting

**Date:** 2025-07-25

## Status

Accepted

## Context

See [6. New Test Framework to enable In-Place, Self-Contained Test Execution](./0006-new-test-framework-in-place-self-contained-test-execution.md) for additional context on this decision.

The Garden Linux test framework must support a wide variety of environments, including cloud providers, VMs, containers, chroots, and bare metal. The current approach relies heavily on SSH and manual deployment, which is slow, error-prone, and not always feasible. Additionally, previous frameworks lacked robust mechanisms for exporting and reporting test results in a standardized, machine-readable format.

Key limitations:
- **Deployment Constraints:** Reliance on SSH and manual copying (e.g., scp) is slow and fragile, especially for large test suites.
- **Cloud Provider Diversity:** Different cloud platforms require different image formats and deployment strategies.
- **Reporting Weaknesses:** Lack of standardized, exportable reporting formats makes it difficult to integrate test results with external systems or dashboards.

## Decision

We will support multiple mechanisms for distributing the test suite and collecting results, tailored to the needs of each environment:

- **Distribution Mechanisms:** The test suite may be delivered via scp, cloud-init/user_data, OCI registry/artifact, image attach, or other platform-specific methods. The suite will be packaged as a relocatable tarball or directory, and may be built on demand or pulled as a build artifact.
- **Cloud Provider Support:** Image formats and deployment workflows will be adapted for each provider (e.g., raw, vhd, qcow2), with research into automation and API integration for disk/image attachment.
- **Reporting:** Test output will be flexible and allow custom formats in a plugin-based system, so that new formats are easy to add. The default output will be a human-readable text format, machine readable outputs such as a [diki](https://github.com/gardener/diki)-compatible format or JUnit xml output may be added later.
- **Backchannel for Logs:** Mechanisms will be explored for retrieving logs and results from the system under test.

## Consequences

- **Portability:** The test framework can be deployed and executed in diverse environments, including public clouds, on-premises, and edge systems.
- **Scalability:** Automated distribution and reporting enable large-scale, repeatable testing across many systems and platforms.
- **Integration:** Standardized reporting formats facilitate integration with CI/CD pipelines, dashboards, and external tools.
- **Maintainability:** Flexible distribution mechanisms reduce operational overhead and make it easier to adapt to new platforms or requirements.
- **Implementation Effort:** Initial implementation will likely use scp and S3 uploads, with further research into image attach and OCI artifact strategies.
