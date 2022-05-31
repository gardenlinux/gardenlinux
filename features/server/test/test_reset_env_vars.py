from helper.tests.file_content import file_content
import pytest

@pytest.mark.parametrize(
    "file,args",
    [
        ("/etc/sudoers", {"Defaults": "env_reset"})
    ]
)

def test_reset_env_vars(client, file, args):
    file_content(client, file, args, invert=False, ignore_missing=False)
