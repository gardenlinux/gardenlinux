from helper.tests.mount import mount
from helper.tests.mount import MOUNT_TEST_TYPE_VERIFY_OPTION
import pytest


@pytest.mark.parametrize(
    "mount_point,opt,test_type,test_val",
    [
        ("/usr", "ro", MOUNT_TEST_TYPE_VERIFY_OPTION, True)
    ]
)


def test_mount(client, mount_point, opt, test_type, test_val, non_chroot):
     mount(client, mount_point, opt, test_type, test_val)
