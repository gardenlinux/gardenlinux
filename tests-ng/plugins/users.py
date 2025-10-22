import pwd
import subprocess
from typing import Optional, Set

import pytest

from .shell import ShellRunner

users: Set[str] = set()


class User:
    def __init__(self, shell: ShellRunner):
        self._shell = shell

    def is_user_sudo(self, user):
        command = f"sudo --list --other-user={user}"
        output = self._shell(command, capture_output=True)
        output_lines = output.stdout.strip().splitlines()
        for line in output_lines:
            if "may run the following commands on" in line:
                return True
        return False


def cloudinit_default_user() -> Optional[str]:
    try:
        out = subprocess.check_output(
            ["cloud-init", "query", "system_info.default_user.name"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        name = out.strip()
        return name or None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--expected-users",
        action="store",
        default="",
        help="List of expected users (comma separated)",
    )


def pytest_configure(config: pytest.Config):
    global users
    arg = config.getoption("--expected-users")
    if arg:
        users.update(u.strip() for u in arg.split(",") if u.strip())
    cloudinit_user = cloudinit_default_user()
    if cloudinit_user:
        users.add(cloudinit_user)


@pytest.fixture
def expected_users():
    return users


@pytest.fixture
def user(shell: ShellRunner):
    return User(shell)


@pytest.fixture
def get_regular_users(regular_user_uid_range):
    regular_users = set()

    for entry in pwd.getpwall():
        if entry.pw_uid in regular_user_uid_range:
            regular_users.add(entry.pw_name)
    return regular_users
