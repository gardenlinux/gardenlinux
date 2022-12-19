## Feature: cisModprobe
### Description
<website-feature>

This subfeature removes and blacklists unwanted kernel modules. This features depends on its parents feature `cis`.
</website-feature>

### Features
Regarding `CIS` benchmark, the `fat` module should also be blacklisted. However, this is needed for booting `UEFI`. Therefore, we can not blacklist this one (see also unit testing).

The following modules are blacklisted:
* cramfs
* dccp
* freevxfs
* jffs2
* rds
* sctp
* squashfs
* tipc
* udf

### Unit testing
Unit tests are only supported by its parent feature `cis`. See also [../cis/README.md](../cis/README.md).

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|cis|
|excluded_features|None|
