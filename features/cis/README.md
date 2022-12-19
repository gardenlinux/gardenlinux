## Feature: cis
### Description
<website-feature>

The [Garden Linux](https://gardenlinux.io/) [CIS](https://www.cisecurity.org) unit test is [Debian-CIS](https://github.com/ovh/debian-cis) (created by [OVH](https://github.com/ovh)) based. This test framework is mostly based on recommendations of [CIS (Center for Internet Security)](https://www.cisecurity.org) benchmarks for [Debian GNU/Linux](https://www.debian.org). However, Garden Linux may fulfill them in a slightly different way. This becomes important for unit testing where ACL's like `AppArmor` are replaced by `SELinux` (which is also accepted by CIS benchmarks). `CIS`
 related unit tests can be performed on any cloud platform (see also [../../tests/README.md](../../tests/README.md)) except of `chroot`.
</website-feature>

### Features
## Overview
This `cis` feature represents a meta feature that includes multiple sub features. Most sub features are prefixed by `cis`. Working with sub features provides an easy overview, adjustment and administration for each sub feature. While only including all sub features fits the CIS benchmarks, it is in an operators decision to adjust sub features to his needs. This allows changes to be as near as possible to `CIS`, even it may not fit the `CIS` benchmarks.

Sub features are included by the `cis/info.yaml` configuration file. Sub features **can not** be used as a standalone feature and always depend on `cis`.

### Unit testing
The [CIS](https://www.cisecurity.org) unit test is [Debian-CIS](https://github.com/ovh/debian-cis) (created by [OVH](https://github.com/ovh)) based. This test framework is mostly based on recommendations of [CIS (Center for Internet Security)](https://www.cisecurity.org) benchmarks for [Debian GNU/Linux](https://www.debian.org). This tests will be proceeded for artifacts that are built with `CIS` feature and will validate all options, whether a sub feature is not included.

However, Garden Linux may fulfill them in a slightly different way. While the recommended way for ACL for Debian based distributions is `AppArmor`, Garden Linux used `SELinux`. As a result, `AppArmor` tests need to be whitelisted, as well as new `SeLinux` tests created.

Tests can be whitelisted by placing a `.cfg` file with equal name of the test in [test/conf.d](test/conf.d). More information can be found in [test/conf.d/README.md](test/conf.d/README.md).

Additional tests can be be included by placing an executable script nn [test/check_scripts](test/check_scripts). More information can be found in [test/check_scripts/README.md](test/check_scripts/README.md).

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|`aide`, `cisAudit`, `cisModprobe`, `cisOS`, `cisPackages`, `cisPartition`, `cisSshd`, `cisSysctl`, `clamav`, `firewall`|
|excluded_features|`fedramp`|
