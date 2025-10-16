import os
import pwd
import subprocess
from typing import Optional, Tuple

import pytest

default_user: Optional[Tuple[int, int]] = None


class ShellRunner:
    def __init__(self, user: Optional[Tuple[int, int]]):
        self.user = user

    def __call__(
        self, cmd: str, capture_output: bool = False, ignore_exit_code: bool = False
    ) -> subprocess.CompletedProcess:
        def _setuid():
            if self.user != None:
                os.setgid(self.user[1])
                os.setuid(self.user[0])

        result = subprocess.run(
            ["/bin/sh", "-e", "-c", cmd],
            shell=False,
            capture_output=capture_output,
            text=True,
            check=False,
            preexec_fn=_setuid,
        )

        if result.returncode != 0 and not ignore_exit_code:
            raise RuntimeError(
                f"command {cmd} failed with exit code {result.returncode}"
            )

        return result


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--default-user",
        action="store",
        default="",
        help="User to switch to before executing shell commands",
    )


def pytest_configure(config: pytest.Config):
    global default_user

    default_user_name = config.getoption("--default-user")
    if default_user_name != "":
        passwd_entry = pwd.getpwnam(default_user_name)
        default_user = (passwd_entry.pw_uid, passwd_entry.pw_gid)
    if default_user is None and os.geteuid() == 0:
        default_user = (65534, 65534)

    config.addinivalue_line(
        "markers",
        "root(reason=None): mark test to run as root user, with optional reason",
    )


@pytest.fixture
def shell(request: pytest.FixtureRequest) -> ShellRunner:
    root_marker = request.node.get_closest_marker("root")
    if root_marker:
        reason = root_marker.kwargs.get("reason") if root_marker.kwargs else None
        if os.geteuid() != 0:
            skip_msg = "tests marked as root but running as unprivileged user"
            if reason:
                skip_msg += f" (reason: {reason})"
            pytest.skip(skip_msg)
        return ShellRunner((0, 0))
    else:
        return ShellRunner(default_user)
