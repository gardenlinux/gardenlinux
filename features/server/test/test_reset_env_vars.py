from helper.tests.file_content import file_content
import pytest

@pytest.mark.parametrize(
    "file,args,sudo",
    [
        ("/etc/sudoers", {"Defaults": "env_reset"}, True)
    ]
)

def test_reset_env_vars(client, file, args, sudo):
    file_content(client, file, args, invert=False, ignore_missing=False, sudo=sudo)
