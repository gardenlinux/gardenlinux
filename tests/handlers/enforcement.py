import pytest
from plugins.shell import ShellRunner

TEST_FILE = "/tmp/audit_enforcement_test"
TIME_FILE = "/tmp/audit_enforcement_time"


def handle_enforcement_test(shell: ShellRunner):
    """
    Audit requirement handler to prepare a restricted
    file for permission enforcement testing.
    """

    shell(f"rm -f {TEST_FILE} {TIME_FILE}", ignore_exit_code=True)
    shell(f"touch {TEST_FILE}")
    shell(f"chmod 600 {TEST_FILE}")

    yield TEST_FILE, TIME_FILE

    shell(f"rm -f {TEST_FILE} {TIME_FILE}", ignore_exit_code=True)


@pytest.fixture
def enforcement_test(shell: ShellRunner):
    """fixture for enforcement audit test"""
    yield from handle_enforcement_test(shell)
