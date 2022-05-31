from helper.tests.file_content import file_content
import pytest

# Parametrize the test unit with further
# options.
# First: File to process
# Second: Key to search
# Third: Value of Key
@pytest.mark.parametrize(
    "file,dict",
    [
        ("/etc/profile.d/50-autologout.sh", {
            "TMOUT": "600",
            "readonly": "TMOUT",
            "export": "TMOUT"
        })
    ]
)


# Run the test unit to perform the
# final tests by the given artifact.
def test_umask(client, file, dict):
    file_content(client, file, dict)
