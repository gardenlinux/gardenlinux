## Feature: stigSshd
### Description
<website-feature>

This subfeature manages the sshd configuration according to the DISA STIG requirements. This features depends on its parents feature `stig`.
</website-feature>

### Features
This feature manages the sshd configuration, adjusts the used ciphers, and deploys the required DoD Notice and Consent Banner.

### Unit testing
Unit tests are only supported by its parent feature `stig`. See also [../stig/README.md](../stig/README.md).

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|stig|
|excluded_features|None|
