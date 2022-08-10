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
        ("/etc/login.defs", {"UMASK": "077"})
    ]
)


# Run the test unit to perform the
# final tests by the given artifact.
def test_umask(client, file, dict):
    file_content(client, file, dict)
