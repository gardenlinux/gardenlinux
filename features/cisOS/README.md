## Feature: cisOS
### Description
<website-feature>

This subfeature adjusts the OS settings according to CIS benchmarks. This features depends on its parents feature `cis`.
</website-feature>

### Features
Settings according to the CIS benchmarks are defined within this subfeatures that sets pwquality options, file permissions, login options, manages PAM and udev rules.

### Unit testing
Unit tests are only supported by its parent feature `cis`. See also [../cis/README.md](../cis/README.md).

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|cis|
|excluded_features|None|
