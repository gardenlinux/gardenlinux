# ADR 0031: Static Feature/Test Coverage Analysis for Test Framework

**Date:** 2026-02-02

## Status

Draft

## Context

As we continue to develop and maintain Garden Linux, we need to ensure comprehensive test coverage for feature configurations. However, tracking which feature settings are covered by tests presents significant challenges.

The [tests-ng framework](./0006-new-test-framework-in-place-self-contained-test-execution.md) is designed to run on several test environments but also actual production systems (VMs, containers, bare metal) where the `features/` directory is **not shipped** in the test distribution, as established in [ADR 0006](./0006-new-test-framework-in-place-self-contained-test-execution.md). Tests must be self-contained and portable, with the test distribution only including test files, plugins, and runtime dependencies.

Garden Linux features define configuration settings through a variety of formats and representations:

- **Builder-evaluated config**: e.g., packages to install in `pkg.include`
- **Builder-evaluated scripts**: plain shell scripts using `sed`, `awk`, etc. in `exec.config`
- **File templates**: file configurations in `file.include/` and `initrd.include/`

This variety makes it very hard to match actual tests and see "what is covered?" - there's no straightforward way to determine which feature configurations have corresponding tests. This challenge is further complicated by the need for [version independence](./0013-discontinue-packages-musthave-tests.md), where tests must work with systems built from different versions of features.

Traditional runtime coverage tools (like `pytest-cov`) have fundamental limitations in this architecture:

1. **Integration challenges**: The `features/` directory is not available at test runtime, so we cannot generate coverage target files from features or track which settings were tested during execution.

2. **Test execution required**: Traditional coverage tools require running tests to track coverage, which adds unnecessary overhead when the goal is simply to identify coverage gaps without executing the full test suite.

## Decision

We will use **static coverage analysis** to track test coverage by defining setting identifier markers in features and matching them with references in test files, without requiring test execution or the features directory at runtime.

### Setting Identifier Markers

We define setting identifier markers in features using the format `GL-SET-<feature>-<category>-<setting-description>`. Identifiers must be descriptive and self-documenting to clearly indicate which feature and which specific setting is being tested.

**Identifier Structure:**

- **Prefix**: `GL-SET-` (Garden Linux Setting identifier)
- **Feature name**: The feature directory name (e.g., `aws`, `ssh`, `cis`)
- **Category**: The type of setting (e.g., `service`, `config`, `file`)
- **Setting description**: A descriptive, hyphenated description of what the setting does (e.g., `aws-clocksource-enable`, `ssh-config-permit-root-login`)

**Where identifiers are defined:**

- In `exec.config`, `pkg.include`, `file.exclude`: add comments with identifiers like `# GL-SET-aws-service-aws-clocksource-enable`
- For `file.include/`: define identifiers in `file.include.ids.yaml` (markers shall not end up in the final image)
- For `initrd.include/`: define identifiers in `initrd.include.ids.yaml` (markers shall not end up in the final image)

This naming convention makes it immediately clear from the identifier itself which feature is being tested and what specific setting it covers, facilitating both manual review and automated coverage analysis.

These identifiers are then referenced in test files (`tests-ng/test_*.py`) to establish a clear mapping between features and tests.

### Coverage Analysis Approach

The coverage reporting system (`tests-ng/util/coverage.py`) performs static analysis in three steps:

1. **Extract setting IDs from features**: Scans the `features/` directory (available during development/CI) and extracts all setting IDs from:

   - Inline comments in `exec.config`, `pkg.include`, `file.exclude`, ... files (searching for `GL-SET-*` pattern)
   - `file.include/` files (via `file.include.ids.yaml` mappings)
   - `initrd.include/` files (via `initrd.include.ids.yaml` mappings)

2. **Find setting IDs in test files**: Searches all `tests-ng/test_*.py` files for `GL-SET-*` string patterns using regex matching.

3. **Generate coverage report**: Compares the two sets (defined vs. referenced) and generates human-readable and machine-readable reports showing coverage percentages, per-feature breakdown, and lists of untested setting IDs.

This approach works entirely through static file analysis - generating reports **offline** (not while running pytest), avoiding the need for test execution, runtime dependencies on the features directory, or additional coverage tracking infrastructure.

## Consequences

### Positive

- **Works everywhere**: Coverage analysis can run in any environment where the repository is available, without requiring test execution or the features directory at runtime.

- **Fast**: Static file analysis completes in seconds, making it suitable for quick feedback in development and CI/CD pipelines.

- **No test execution required**: Coverage reports can be generated without running any tests, enabling coverage tracking even when test infrastructure is unavailable.

- **Actionable**: Clearly shows which setting IDs need tests, organized by feature, making it easy to identify and address coverage gaps.

- **Simple and reliable**: Uses only standard library modules (plus optional `yaml` for parsing), with no complex test execution or coverage tracking overhead.

### Trade-offs and risks

- **Static analysis only**: Can only detect setting IDs that are present as string literals in features and test files.

- **Pattern matching limitations**: Relies on regex pattern matching, which may have edge cases with unusual ID formats or comments.

- **No execution verification**: Static analysis cannot verify that tests actually exercise the settings correctly - it only verifies that setting IDs are referenced in test code.

- **Manual maintenance**: The `file.include.ids.yaml`, `initrd.include.ids.yaml` files and inline comments must be maintained manually to keep coverage tracking accurate. This should be reflected in the documentation on how to write features and tests.

## Alternatives Considered

1. **Traditional runtime coverage tools (pytest-cov)**: These tools require:

   - The `features/` directory to be available at test runtime to generate coverage targets
   - Test execution to track which targets were called

   Rejected because the test distribution architecture explicitly excludes the `features/` directory, and these tools cannot work in production test environments where features don't exist.

2. **Hybrid approach**: Generate coverage target files from features during build, then use runtime coverage tools during test execution. Rejected because:

   - Still requires test execution
   - Adds complexity to the build and test pipeline
   - Doesn't solve the fundamental issue that features aren't available at runtime in production environments

3. **Manual tracking**: Rely on developers to manually track which setting have tests. This is the current approach. Rejected because:

   - Error-prone and doesn't scale
   - No automated way to identify coverage gaps
   - Difficult to maintain as the codebase grows
