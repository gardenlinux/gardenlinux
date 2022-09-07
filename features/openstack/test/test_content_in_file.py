import pytest
from helper.tests.file_content import file_content
from helper.utils import execute_remote_command


@pytest.mark.parametrize(
    "file,args",
    [
        ("/etc/cloud/cloud.cfg", "ntp"),
        ("/etc/cloud/cloud.cfg", "resizefs"),
        ("/etc/cloud/cloud.cfg", "growpart")
    ]
)


def test_file_content(client, file, args):
    file_content(client, file, args, only_line_match=True, invert=True)
