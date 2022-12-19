## Feature: cisSysctl
### Description
<website-feature>

This subfeature manages the required sysctl options according to the CIS benchmarks. This features depends on its parents feature `cis`.
</website-feature>

### Features
IPv6: IPv6 gets fully deactivated by this feature.
IPv4: `forward` and `redirects` are deactivated for IPv4.

### Unit testing
Unit tests are only supported by its parent feature `cis`. See also [../cis/README.md](../cis/README.md).

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|cis|
|excluded_features|None|
