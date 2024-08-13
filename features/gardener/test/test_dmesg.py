import pytest
from helper.tests.file_content import file_content
from helper.utils import execute_remote_command


@pytest.mark.parametrize(
    "file,args",
    [
        ("/etc/sysctl.d/40-allow-nonroot-dmesg.conf", {"kernel.dmesg_restrict": "0"}),
        ("/tmp/sysctl.txt", {"kernel.dmesg_restrict": "0"})
    ]
)


def test_dmesg(client, file, args, non_chroot):
    cmd = "/usr/sbin/sysctl -a > /tmp/sysctl.txt"
    execute_remote_command(client, cmd)
    file_content(client, file, args)
