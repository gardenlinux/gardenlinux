# conf.d
## General
The [Garden Linux](https://gardenlinux.io/) [CIS](https://www.cisecurity.org) unit test is [Debian-CIS](https://github.com/ovh/debian-cis) (created by [OVH](https://github.com/ovh)) based. This test framework is mostly based on recommendations of [CIS (Center for Internet Security)](https://www.cisecurity.org) benchmarks for [Debian GNU/Linux](https://www.debian.org). However, Garden Linux may fit the needs in a slightly different way (e.g. for ACL it replaces `AppArmor` with `SELinux`) that needs to adjust and add further custom checks to make sure that the final artifact is fully CIS compliant. As a result, not all given upstream checks may work on Garden Linux. Therefore, this directory allows to whitelist specific tests.

## Whitelisting
Whitelisting tests can be easily done by placing a `.cfg` file within this directory with the equal name of the test including `status=disabled`.

**Example**

The CIS unit test `99.99_check_distribution.sh` may fail to validate the version of Garden Linux. As a result, we need to whitelist this check, because Garden Linux is Debian GNU/Linux `testing` based.

By the given check name:

```
99.99_check_distribution.sh
```
a corresponding config file called:
```
99.99_check_distribution.cfg
```
with the following content:
```
# 99.99_check_distribution
# Disabled: Garden Linux is Debian Testing based
status=disabled
```
will be placed within this directory.

Make sure to have at least `status=disabled` included. Next to this, it should cover the reason why the check got disabled.
