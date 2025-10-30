# 19. Standardize on systemd Timers

Date: 2025-10-30

## Status

Accepted

## Context

Garden Linux currently uses a mix of cron jobs and systemd timers for scheduling periodic tasks. This creates unnecessary complexity by maintaining two different scheduling mechanisms. Since Garden Linux already uses systemd as its init system and service manager, we need to decide whether to standardize on a single scheduling mechanism.

systemd timers offer several advantages over traditional cron:
- Integration with systemd's dependency management
- Better logging and status tracking via journald
- More precise timer specifications
- Built-in service management and failure handling

While cron is a traditional Unix tool with a long history, maintaining two parallel scheduling systems doesn't provide significant benefits and increases maintenance overhead.

## Decision

We will standardize on systemd timers for all scheduled tasks in Garden Linux and migrate existing cron jobs to systemd timer units.

This means:
1. All new scheduled tasks must use systemd timer units
2. Existing cron jobs will be converted to equivalent systemd timer units
3. The cron service will not be included in Garden Linux features by default

## Consequences

### Positive

- Simplified system management with a single scheduling mechanism
- Better integration with systemd's service management
- Improved logging and monitoring capabilities
- Consistent configuration across all Garden Linux features

### Negative

- Migration effort required for existing cron jobs
- Learning curve for contributors more familiar with cron syntax

### Neutral

- Documentation updates needed to reflect the standardization
- Test updates required for features using scheduled tasks
