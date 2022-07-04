from helper.tests.sgid_suid_files import sgid_suid_files
import pytest

# Parametrize the test unit with further
# options to distinct 'sgid' and 'suid' tests.
@pytest.mark.parametrize(
     "test_type,whitelist_files",
    [
        ("sgid", [
                 "/usr/bin/expiry,0,42",
                 "/usr/bin/write,0,5",
                 "/usr/bin/wall,0,5",
                 "/usr/bin/chage,0,42",
                 "/usr/bin/ssh-agent,0,114",
                 "/usr/bin/ssh-agent,0,113",
                 "/usr/bin/ssh-agent,0,112",
                 "/usr/sbin/unix_chkpwd,0,42",
                 "/usr/lib/systemd-cron/crontab_setgid,0,104",
                 "/usr/lib/systemd-cron/crontab_setgid,0,106",
                 "/usr/lib/systemd-cron/crontab_setgid,0,114",
                 "/usr/lib/systemd-cron/crontab_setgid,0,115",
                 "/usr/lib/systemd-cron/crontab_setgid,0,116"
                 ]
        ),
        ("suid", [
                 "/usr/bin/chsh,0,0",
                 "/usr/lib/openssh/ssh-keysign,0,0",
                 "/usr/bin/newgrp,0,0",
                 "/usr/bin/su,0,0",
                 "/usr/lib/dbus-1.0/dbus-daemon-launch-helper,0,113",
                 "/usr/lib/dbus-1.0/dbus-daemon-launch-helper,0,112",
                 "/usr/lib/dbus-1.0/dbus-daemon-launch-helper,0,111",
                 "/usr/lib/dbus-1.0/dbus-daemon-launch-helper,0,110",
                 "/usr/bin/chfn,0,0",
                 "/usr/bin/gpasswd,0,0",
                 "/usr/bin/sudo,0,0",
                 "/usr/bin/passwd,0,0"
                 ]
        )
    ]
)


# Run the test unit to perform the
# final tests by the given artifact.
def test_sgid_suid_files(client, test_type, whitelist_files):
    sgid_suid_files(client, test_type, whitelist_files)
