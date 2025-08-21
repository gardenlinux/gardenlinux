import pytest
from plugins.dpkg import Dpkg
from plugins.shell import ShellRunner

denylist = [
    "rlogin",
    "rsh",
    "rcp",
    "telnet",
    "libdb5.3",
    "libssl1.1",
]


@pytest.mark.parametrize("denied_package", denylist)
def test_no_denylisted_packages(denied_package: str, dpkg: Dpkg):
    assert not dpkg.package_is_installed(
        denied_package
    ), f"Denylisted package {denied_package} is installed"
