from helper.tests.file_content import file_content
import pytest

@pytest.mark.parametrize(
    "file,args,sudo",
    [
        ("/etc/sudoers", {"Defaults": "secure_path"}, True)
    ]
)

def test_secure_path_is_set(client, file, args, sudo):
    file_content(client, file, args, invert=False, ignore_missing=False, sudo=sudo)
