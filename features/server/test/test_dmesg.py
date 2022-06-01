import pytest
from helper.utils import get_kernel_version
from helper.tests.file_content import file_content


@pytest.mark.parametrize(
    "file,args",
    [
        ("/etc/sysctl.d/restric-dmesg.conf", {"kernel.dmesg_restrict": "1"}),
        ("/tmp/sysctl.txt", {"kernel.dmesg_restrict": "1"})
    ]
)


def test_dmesg(client, file, args, non_chroot, non_feature_gardener):
    cmd = "sysctl -a > /tmp/sysctl.txt"
    execute_remote_command(client, cmd)
    file_content(client, file, args)
