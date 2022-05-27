from helper.tests.key_val_in_file import key_val_in_file
from helper.utils import unset_env_var
import pytest

# Parametrize the test unit with further
# options.
# First: File to process
# Second: Key to search
# Third: Value of Key
@pytest.mark.parametrize(
    "file,args",
    [
        ("/etc/profile.d/50-nohistory.sh", {
            "HISTFILE": "/dev/null",
            "readonly": "HISTFILE",
            "export": "HISTFILE"
        })
    ]
)


# Run the test unit to perform the
# final tests by the given artifact.
# Testing:
#  - The key/value search lookup is inverted. As a
#    resulty any found pattern is an error.
#  - Files that can not be found are ignored
#    and will not fail the test.
def test_history(client, file, args):
    # Test is config is present in file
    key_val_in_file(client, file, args)

    # Test write protection of an ENV var
    env_var = "HISTFILE"
    unset_var = unset_env_var(client, env_var)
    assert unset_var == 1, f"ENV VAR {env_var} is not write protected or was not present."
