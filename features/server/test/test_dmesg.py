import pytest
from helper.utils import get_kernel_version
from helper.tests.key_val_in_file import key_val_in_file


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
    key_val_in_file(client, file, args)
