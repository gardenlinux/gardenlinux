from helper.tests.mount import mount
import pytest


@pytest.mark.parametrize(
    "mount_point,opt,test_type,test_val",
    [
        ("/opt", "ro", "opt_in_option", True)
    ]
)

def test_mount(client, mount_point, opt, test_type, test_val, non_chroot):
     mount(client, mount_point, opt, test_type, test_val)
