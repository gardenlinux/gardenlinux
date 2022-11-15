## Feature: cisAudit
### Description
<website-feature>
This subfeature installs and configures `auditd`. This features depends on its parents feature `cis`.
</website-feature>

### Features
This feature adjust the basic `auditd` configuration regarding the logging of events. This includes changes of date/time, sudo logging, as well as options how to proceed if disk space get low or is full.

### Unit testing
Unit tests are only supported by its parent feature `cis`. See also [../cis/README.md](../cis/README.md).

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|cis|
|excluded_features|None|
