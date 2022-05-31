import pytest
from helper.utils import get_kernel_version
from helper.tests.file_content import file_content


@pytest.mark.parametrize(
    "file,args",
    [
        ("/boot/config-", {"CONFIG_SECURITY_DMESG_RESTRICT": "y"}),
        ("/etc/sysctl.d/restric-dmesg.conf", {"kernel.dmesg_restrict": "1"})
    ]
)


def test_dmesg(client, file, args, non_chroot):
    kernel_ver = get_kernel_version(client)
    if '/boot/config-' in file:
        file = f"{file}{kernel_ver}"
    file_content(client, file, args)
