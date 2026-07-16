import pytest
from plugins.shell import ShellRunner

TEST_USER = "audit_test_user"


@pytest.fixture
def audit_user(shell: ShellRunner):
    shell(f"id {TEST_USER} || useradd -m -s /bin/sh {TEST_USER}")
    yield TEST_USER
    shell(f"userdel -r {TEST_USER}", ignore_exit_code=True)
    shell(
        "rm -f /etc/group- /etc/gshadow- /etc/passwd- /etc/shadow- /etc/subgid- /etc/subuid-"
    )
