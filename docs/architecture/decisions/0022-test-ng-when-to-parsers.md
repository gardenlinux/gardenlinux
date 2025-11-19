# 22. Use Parser Plugins for Files and Command Output in Test Framework

**Date:** 2025-11-19

## Status

Draft

## Context

In the new Garden Linux tests framework, we need to parse various file formats and command outputs to verify system configuration and behavior. The framework provides parser plugins for parsing structured formats (JSON, YAML, INI, TOML) and domain-specific formats (PAM configs, SSH configs), but there has been inconsistency in when these parser plugins should be used versus direct file/command parsing.

The framework already includes a default file parser plugin and an underlying parser class that can be used for both file and command output parsing.

Discussions about when to use parser plugins versus direct parsing occurred in these PRs:

- https://github.com/gardenlinux/gardenlinux/pull/3728
- https://github.com/gardenlinux/gardenlinux/pull/3788
- https://github.com/gardenlinux/gardenlinux/pull/3827

These discussions revealed inconsistent approaches across tests. For example:

- **Simple line checks**: Some tests read files directly with `Path.read_text()` and parse them via a regex with `re.search()` to manually search for lines, others use an `open(path)` and `read().strip().split()` approach and again others use the existing parser plugins.

- **Structured format parsing**: Tests parsing JSON, YAML, INI, or TOML files sometimes use direct `json.loads()` or `yaml.safe_load()` calls or use the same methods as in "Simple line checks" or again use the existing parser plugins.

- **Command output parsing**: Tests parsing command outputs like `sshd -T` or `systemctl --output=json` are mostly parsed inline with ad-hoc logic, leading to inconsistent parsing approaches across different tests that parse the same command output.

Key questions that arose:

- When should we use the default parser plugin versus parsing directly in tests?
- When is it acceptable to read files directly or parse command output inline?
- When should we create new domain-specific parser plugins (e.g., for PAM configs, SSH configs) versus using the default parser plugin?
- How do we balance parser plugin benefits (consistency, automatic comment filtering, reusability) with test readability?

> [!NOTE]
> The parser plugins are planned to undergo refactoring to improve their API and usability.
> This is tracked in https://github.com/gardenlinux/gardenlinux/issues/3866

## Decision

### Use the default parser plugins for file and command output parsing scenarios

The default parser plugin should be the preferred approach for parsing files and command output because it:

- Automatically filters comments, ensuring consistent parsing across tests
- Provides consistent parsing for multiple formats (keyval, ini, json, yaml, toml)
- Handles file reading with proper error handling
- Makes test code more consistent and maintainable

### Creating New Parser Plugins

For domain-specific parsing scenarios (e.g., parsing `/etc/passwd`, PAM configs, SSH configs), creating new parser plugins is fine and appreciated if the default parser plugin cannot meet the specialized parsing needs or if a dedicated plugin would provide significant advantages. New parser plugins should be created when:

- The parsing logic is used in multiple tests and would benefit from standardization
- The format requires specialized parsing that the default parser plugin cannot handle
- A dedicated plugin would significantly improve test readability and maintainability

## Consequences

### Positive

- **Consistency**: Tests that parse the same formats will do so consistently, reducing bugs from inconsistent parsing.
- **Maintainability**: Parsing logic is centralized, making it easier to fix bugs or update parsing behavior.
- **Reusability**: Parsing plugins can be reused across multiple tests, reducing code duplication.
- **Better error messages**: Plugins can provide domain-specific error messages that are more helpful than generic parsing errors.
- **Type safety**: Plugins can provide better type hints and validation than ad-hoc parsing.

### Negative

- **Learning curve**: Developers need to lookup documentation and learn about available parser plugins and when to use them.
- **Over-abstraction risk**: There's a risk of creating parser plugins that hide important test logic or make tests harder to understand. A decision needs to be made on a per plugin basis.
- **Maintenance burden**: Parser plugins need to be maintained, though this is compensated by reduced duplication. Minimal integration tests for plugins could help to reduce the burden.

### Neutral

- **Parser Plugins**: Existing plugins need to be refactored for better UI.
- **Documentation**: Developer documentation needs to be updated and extended with examples.
- **Refactoring of tests**: Existing tests might need refactoring to match the decisions taken.

## Alternatives Considered

1. **Always use parser plugins**: Require all file/command parsing to go through parser plugins, including creating new plugins for every parsing need. Rejected because it would create unnecessary overhead for one-off test cases and risk over-abstraction. However, the chosen approach does prefer using the default parser plugin for consistency.

2. **Never use parser plugins**: Always parse directly in tests without any parser plugins. Rejected because it leads to code duplication, inconsistent parsing (e.g., handling comments differently), and harder maintenance.

3. **Case-by-case judgment without guidelines**: The current approach, but without clear guidelines. Rejected because it leads to inconsistency and repeated discussions. The chosen approach provides clear guidelines while still allowing flexibility for edge cases.
