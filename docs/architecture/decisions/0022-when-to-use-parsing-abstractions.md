# 22. When to Use Parsing Abstractions for Files and Command Output in Test Framework

**Date:** 2025-11-13

## Status

Draft

## Context

In the new Garden Linux tests framework, we need to parse various file formats and command outputs to verify system configuration and behavior. The framework provides plugins for parsing structured formats (JSON, YAML, INI, TOML) and domain-specific formats (PAM configs, SSH configs), but there has been inconsistency in when these abstractions should be used versus direct file/command parsing.

Discussions about when to use abstractions versus direct parsing occurred in these PRs:

- https://github.com/gardenlinux/gardenlinux/pull/3728
- https://github.com/gardenlinux/gardenlinux/pull/3788
- https://github.com/gardenlinux/gardenlinux/pull/3827

Key questions that arose:

- When should we create or use parsing plugins versus parsing directly in tests?
- When is it acceptable to read files directly or parse command output inline?
- How do we balance abstraction benefits (consistency, reusability) with test readability?

## Decision

We will use parsing abstractions (implemented by plugins) when they provide clear benefits in terms of:

1. **Standardization**: Ensuring consistent parsing across multiple tests
2. **Complexity handling**: Managing complex structured or domain-specific formats
3. **Reusability**: When parsing logic is used in multiple tests
4. **Error handling**: Providing consistent error handling and validation

**Note**: This decision distinguishes between:

- **Using existing plugins** (especially the default file parser): This is generally preferred for consistency
- **Creating new plugins**: This should be done more carefully, only when there's clear benefit

We will **use abstractions** (implemented by existing plugins) when:

- **Simple line checks**: Even simple line checks benefit from using the default file parser plugin, as commented-out lines are filtered out automatically and parsing in tests looks consistent.
- **Complex structured formats**: Parsing Key/Value, JSON, YAML, INI, TOML, or other structured formats that benefit from standardized parsing.
- **Domain-specific formats**: Complex formats like PAM configs, SSH configs, or other domain-specific configurations that have specialized parsing needs that cannot be met by the default parsing plugins or would have significant advantages if implemented as an extra plugin.
- **Command output standardization**: When command outputs need to be parsed consistently across multiple tests (e.g., `sshd -T`, `systemctl --output=json`). This ensures all tests parse the same command output in the same way.
- **Reusability**: When the same parsing logic is used in multiple tests. Creating a plugin avoids code duplication and ensures consistency.

We will **avoid creating new abstractions** (implemented by creating a new plugin) when:

- **One-off parsing**: Parsing logic that is only used in a single test and it is not expected that other tests will ever use it. In these cases, use the default parser plugin or parse directly in the test rather than creating a new plugin.
- **Simple direct parsing is clearer**: When direct parsing in the test code is more readable and the parsing logic is trivial (e.g., checking if a string contains a substring, simple regex matching). The default parser plugin should still be preferred for file reading to handle comments and provide consistency.
- **Over-abstraction risk**: When creating a new plugin would hide important test logic or make tests significantly harder to understand. A thin line exists here, and good UI and documentation of a plugin can compensate, but if the abstraction adds more complexity than it removes, avoid it.

## Consequences

### Positive

- **Consistency**: Tests that parse the same formats will do so consistently, reducing bugs from inconsistent parsing.
- **Maintainability**: Parsing logic is centralized, making it easier to fix bugs or update parsing behavior.
- **Reusability**: Parsing plugins can be reused across multiple tests, reducing code duplication.
- **Better error messages**: Plugins can provide domain-specific error messages that are more helpful than generic parsing errors.
- **Type safety**: Plugins can provide better type hints and validation than ad-hoc parsing.

### Negative

- **Learning curve**: Developers need to lookup documentation and learn about available plugins and when to use them.
- **Over-abstraction risk**: There's a risk of creating abstractions that hide important test logic or make tests harder to understand. A decision needs to be made on a per plugin basis.
- **Maintenance burden**: Plugins need to be maintained, though this is compensated by reduced duplication. Minimal integration tests for plugins could help to reduce the burden.

### Neutral

- **Parser Plugins**: Existing plugins need to be refactored for better UI.
- **Documentation**: Developer documentation needs to be updated and extended with examples.
- **Refactoring of tests**: Existing tests might need refactoring to match the decisions taken.

## Alternatives Considered

1. **Always use abstractions**: Require all file/command parsing to go through plugins, including creating new plugins for every parsing need. Rejected because it would create unnecessary overhead for one-off test cases and risk over-abstraction. However, the chosen approach does prefer using existing plugins (especially the default parser) for consistency.

2. **Never use abstractions**: Always parse directly in tests without any plugins. Rejected because it leads to code duplication, inconsistent parsing (e.g., handling comments differently), and harder maintenance.

3. **Case-by-case judgment without guidelines**: The current approach, but without clear guidelines. Rejected because it leads to inconsistency and repeated discussions. The chosen approach provides clear guidelines while still allowing flexibility for edge cases.
