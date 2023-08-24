from helper.tests.sgid_suid_files import sgid_suid_files
import pytest

# Parametrize the test unit with further
# options to distinct 'sgid' and 'suid' tests.
@pytest.mark.parametrize(
     "test_type,whitelist_files",
    [
        ("sgid", [
                 "/usr/bin/expiry,root,shadow",
                 "/usr/bin/write,root,tty",
                 "/usr/bin/wall,root,tty",
                 "/usr/bin/chage,root,shadow",
                 "/usr/bin/ssh-agent,root,_ssh",
                 "/usr/sbin/unix_chkpwd,root,shadow",
                 "/usr/libexec/systemd-cron/crontab_setgid,root,crontab",
                 ]
        ),
        ("suid", [
                 "/usr/bin/chsh,root,root",
                 "/usr/lib/openssh/ssh-keysign,root,root",
                 "/usr/bin/newgrp,root,root",
                 "/usr/bin/su,root,root",
                 "/usr/lib/dbus-1.0/dbus-daemon-launch-helper,root,messagebus",
                 "/usr/bin/chfn,root,root",
                 "/usr/bin/gpasswd,root,root",
                 "/usr/bin/sudo,root,root",
                 "/usr/bin/passwd,root,root",
                 "/usr/lib/polkit-1/polkit-agent-helper-1,root,root",
                 "/usr/bin/pkexec,root,root"
                 ]
        )
    ]
)


# Run the test unit to perform the
# final tests by the given artifact.
def test_sgid_suid_files(client, test_type, whitelist_files, non_vhost):
    sgid_suid_files(client, test_type, whitelist_files)
