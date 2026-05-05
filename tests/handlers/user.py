import pytest
from plugins.shell import ShellRunner


def handle_user(shell: ShellRunner, username: str):
    """
    Generic handler to manage lifecycle of a system user.
    Creates the user if it does not exist and restores the system state after test.
    """

    user_exists = shell(f"id {username}", ignore_exit_code=True).returncode == 0

    if not user_exists:
        shell(f"useradd -m {username}")

    yield username

    shell(f"pkill -u {username}", ignore_exit_code=True)

    if not user_exists:
        shell(f"userdel -r {username}", ignore_exit_code=True)


@pytest.fixture
def temp_user(shell: ShellRunner):
    """Fixture for temporary user."""
    yield from handle_user(shell, "temp_user")
