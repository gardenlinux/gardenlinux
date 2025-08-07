import pytest
import subprocess

users = set()

def cloudinit_default_user():
    try:
        out = subprocess.check_output(
            ["cloud-init", "query", "system_info.default_user.name"],
            stderr=subprocess.DEVNULL,
            text=True
        )
        name = out.strip()
        return name or None
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None

def pytest_addoption(parser):
    parser.addoption(
        "--expected-users",
        action="store",
        default="",
        help="List of expected users (comma separated)"
    )

def pytest_configure(config):
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
