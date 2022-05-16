from helper.tests.key_val_in_file import key_val_in_file
import pytest

@pytest.mark.parametrize(
    "file,args",
    [
        ("/etc/sudoers", {"Defaults": "env_reset"})
    ]
)

def test_reset_env_vars(client, file, args):
    key_val_in_file(client, file, args, invert=False, ignore_missing=False)