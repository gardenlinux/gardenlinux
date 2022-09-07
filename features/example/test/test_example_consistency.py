####################################################################
## NOTE: This check will never be called and includes samples for  #
#        creating new unit tests.                                  #
####################################################################


# You may use and place new additional helper functions and
# libraries in tests/helper 
# (see also: https://github.com/gardenlinux/gardenlinux/tree/main/tests/helper)

# Within this example we import the function "mount"
# which is placed as a dedicated library in tests/helper/tests/mount.py
from helper.tests.mount import mount

# This examples shows how to import a single function from the utils library.
# Within the "utils.py" library general functions should be placed, that can
# be used from multiple tests. This can be found in tests/helper/utils.py
from helper.utils import execute_remote_command

# Often it may make sense to use PyTest's parametrize function. This allows
# adding/removing test cases within a single file and should never need
# further changes on the test framework's code itself. However, we need
# to import "pytest".
import pytest

# Afterwards, the parametrize can be configured and is defined as a Python
# list object. However, this may include complex data types like dicts.
# Within this example we use touples and assign them for the first element as:
# mount_point: /opt
# opt: ro
# test_type: test_readable
# test_val: True
@pytest.mark.parametrize(
    "mount_point,opt,test_type,test_val",
    [
        # Define the options within the first test element
        ("/opt", "ro", "test_readable", True),
        # Define the options within the second test element
        ("/usr", "rw", "test_readable", True),
    ]
)

# Now, the actual test can be called. Make sure to pass all your defined
# vars to the test. Next to this, fixtures can be used to in-/exclude 
# target platforms or features. Within this example, we exclude the test
# from running on chroot platforms by using the fixute `non_chroot`.
def test_mount(client, mount_point, opt, test_type, test_val, non_chroot):
     mount(client, mount_point, opt, test_type, test_val)
