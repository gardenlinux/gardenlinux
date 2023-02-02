import pytest
from helper.tests.file_content import file_content


@pytest.mark.parametrize(
    "file,args",
    [
        ("/etc/kernel/cmdline", "security=selinux"),
    ]
)


def test_kernel_cmdline(client, file, args):
    file_content(client, file, args, only_line_match=True)
