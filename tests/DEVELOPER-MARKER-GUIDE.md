# Garden Linux Setting ID Marker Guide

---

## Table of Contents

1. [Overview](#overview)
2. [Coverage.py and Test Coverage Analysis](#coveragepy-and-test-coverage-analysis)
3. [Marker Schema](#marker-schema)
4. [Category Reference](#category-reference)
5. [Special Patterns](#special-patterns)
6. [When to Create Markers](#when-to-create-markers)
7. [Where to Place Markers](#where-to-place-markers)

---

## Overview

This guide explains how to create and use setting identifier markers for establishing traceability between Garden Linux features and tests. The following sections detail the tooling, marker syntax, categories and placement guidelines.

---

## Coverage.py and Test Coverage Analysis

**Tool Location:** [`tests/util/coverage.py`](../tests/util/coverage.py)

### What is coverage.py?

`coverage.py` is a static analysis tool that generates coverage reports for Garden Linux by analyzing the relationship between **setting ID markers** (`GL-SET-*`) in feature configurations and their corresponding test cases. Unlike traditional code coverage tools that require test execution, this tool performs **static analysis** to determine which features have test coverage.

These markers follow a specific format (`GL-SET-$feature-$category-$description` - see [Marker Schema](#marker-schema) for details) that enables automated parsing and analysis. The tool scans both feature definitions and test files to establish traceability between what's configured and what's tested.

### Key Capabilities

1. **Static Coverage Analysis**

   - Analyzes setting ID markers in features without running tests
   - Scans test files for `@pytest.mark.setting_ids()` decorators
   - Generates coverage reports showing which features are tested

2. **Coverage Reporting**

   - Lists all setting IDs defined in features
   - Shows which setting IDs have corresponding tests
   - Identifies untested features and gaps in test coverage
   - Provides percentage coverage statistics

3. **Traceability**
   - Establishes clear links between feature configurations and tests
   - Enables audit trail for compliance requirements
   - Supports version-independent testing strategies

### How It Works

**Step 1: Feature Scanning**

- Scans feature directories (`features/*/`) for setting ID markers
- Extracts markers from inline comments in shell scripts (see [Inline Comments](#inline-comments-preferred))
- Parses `file.include.ids.yaml` and `initrd.include.ids.yaml` files for file-based markers (see [Split ID Files](#fileincludeidsyaml-and-initrdincludeidsyaml-for-file-includes))
- Builds a complete inventory of all defined setting IDs across all marker categories (see [Category Reference](#category-reference))

**Step 2: Test Scanning**

- Scans test files (`tests/test_*.py`) for pytest markers
- Extracts setting IDs from `@pytest.mark.setting_ids()` decorators (see [Tests](#tests))
- Maps each test function to its associated setting IDs

**Step 3: Coverage Analysis**

- Matches setting IDs from features with setting IDs in tests
- Identifies covered and uncovered setting IDs
- Calculates coverage percentages and statistics

**Step 4: Report Generation**

- Produces human-readable and machine-readable coverage reports
- Highlights gaps in test coverage
- Provides actionable insights for improving test coverage

### Usage Example

```bash
# Generate coverage report
python tests/util/coverage.py

...

Summary:
  Total setting IDs defined: 614
  Setting IDs found in test files: 257
  Setting IDs not found (untested): 357
  Orphaned setting IDs (in tests but not features): 0
  Coverage: 41.9%

Coverage by feature:
--------------------------------------------------------------------------------
✓ _ephemeral: 3/3 (100.0%)
⚠ _fips: 3/7 (42.9%)

...

Untested setting IDs by feature:
--------------------------------------------------------------------------------

_fips:
  Total setting IDs: 7
  Covered: 3
  Untested: 4
  Untested setting IDs:
    - GL-SET-_fips-config-openssh-sshd-Ciphers
    - GL-SET-_fips-config-openssh-sshd-KexAlgorithms
    - GL-SET-_fips-config-openssl
    - GL-SET-_fips-config-openssl-fipsinstall

...


================================================================================

✓ JSON report written to: tests/coverage_report.json
✓ JUnit XML report written to: tests/coverage_report.xml
```

### Integration with Development Workflow

1. **During Feature Development**

   - Add setting ID markers to new features (see [When to Create Markers](#when-to-create-markers) for guidelines)
   - Place markers appropriately using inline comments or split ID files (see [Where to Place Markers](#where-to-place-markers))
   - Use coverage.py to verify markers are correctly formatted and follow the [Marker Schema](#marker-schema)
   - Identify which tests need to be created

2. **During Test Development**

   - Check coverage reports to find untested features
   - Write tests with appropriate `@pytest.mark.setting_ids()` decorators (see [Tests](#tests))
   - Ensure test markers match the exact setting IDs from features
   - Verify test coverage increases after adding new tests

3. **In CI/CD Pipelines**
   - Run coverage.py as part of automated checks
   - Enforce minimum coverage thresholds
   - Block PRs that reduce test coverage
   - Generate audit reports for compliance tracking

---

**For more information:**

- [ADR 0031 - Static Feature/Test Coverage Analysis](docs/architecture/decisions/0031-static-feature-test-coverage-analysis.md)
- [Coverage Reporting Tool](tests/util/coverage.py)
- [Test Framework Documentation](tests/README.md)
