# Check Scripts
## General
The [Garden Linux](https://gardenlinux.io/) [CIS](https://www.cisecurity.org) unit test is [Debian-CIS](https://github.com/ovh/debian-cis) (created by [OVH](https://github.com/ovh)) based. This test framework is mostly based on recommendations of [CIS (Center for Internet Security)](https://www.cisecurity.org) benchmarks for [Debian GNU/Linux](https://www.debian.org). However, Garden Linux may fit the needs in a slightly different way (e.g. for ACL it replaces `AppArmor` with `SELinux`) that needs to adjust and add further custom checks to make sure that the final artifact is fully CIS compliant. All files from this directory are automatically taken and executed for `CIS` unit tests. Make sure that files placed within this directory are executable.

## Adjusted Scripts
Adjusting a check script results in replacing the whole script. Therefore, the script name must match the one to be replaced.

**Example**

The check script `4.2.3_logs_permissions.sh` only validates for log files with chmod 640 permissions. However, we also want to allow chmod 600 permissions which results in adjusting the script and placing it within this directory with the same file name `4.2.3_logs_permissions.sh`.

## Additional Scripts
Additional scripts can be added by placing them within this directory and executable files. Furthermore, they should be prefixed with `99.99_` and provide a short description after the underscore.
