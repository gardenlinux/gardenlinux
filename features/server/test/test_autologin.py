from helper.tests.key_val_in_file import key_val_in_file
import pytest

# Parametrize the test unit with further
# options.
# First: File to process
# Second: Key to search
# Third: Value of Key
@pytest.mark.parametrize(
    "file,args",
    [
        ("/etc/systemd/system/serial-getty@.service.d/autologin.conf", {"ExecStart": "autologin"}),
        ("/system/getty@tty1.service.d/autologin.conf", {"ExecStart": "autologin"})
    ]
)


# Run the test unit to perform the
# final tests by the given artifact.
# Testing:
#  - The key/value search lookup is inverted. As a
#    resulty any found pattern is an error.
#  - Files that can not be found are ignored
#    and will not fail the test.
def test_autologin(client, file, args, non_dev):
    key_val_in_file(client, file, args, invert=True, ignore_missing=True)
