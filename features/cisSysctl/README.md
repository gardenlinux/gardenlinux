## Feature: cisSysctl
### Description
<website-feature>

This subfeature manages the required sysctl options according to the CIS benchmarks. This features depends on its parents feature `cis`.
</website-feature>

### Features
This deactivates IPv6 fully and also disabled redirects, forwarding for IPv4.

### Unit testing
Unit tests are only supported by its parent feature `cis`. See also [../cis/README.md](../cis/README.md).

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|cis|
|excluded_features|None|
