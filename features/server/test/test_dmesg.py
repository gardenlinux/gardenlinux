import pytest
from helper.tests.file_content import file_content
from helper.utils import execute_remote_command


@pytest.mark.parametrize(
    "file,args",
    [
        ("/etc/sysctl.d/40-restric-dmesg.conf", {"kernel.dmesg_restrict": "1"}),
        ("/tmp/sysctl.txt", {"kernel.dmesg_restrict": "1"})
    ]
)


def test_dmesg(client, file, args, non_provisioner_chroot, non_feature_gardener):
    cmd = "sysctl -a > /tmp/sysctl.txt"
    execute_remote_command(client, cmd)
    file_content(client, file, args)
