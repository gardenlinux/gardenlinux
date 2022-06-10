from helper.tests.file_content import file_content
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
        ("/etc/systemd/system/getty@tty1.service.d/autologin.conf", {"ExecStart": "autologin"})
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
    file_content(client, file, args, invert=True, ignore_missing=True)
