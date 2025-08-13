import pytest
from plugins.dpkg import Dpkg
from plugins.shell import ShellRunner

denylist = [
    "rlogin",
    "rsh",
    "rcp",
    "telnet",
    "libdb5.3:amd64",
    "libdb5.3:arm64",
    "libssl1.1:amd64",
    "libssl1.1:arm64",
]


@pytest.mark.parametrize("denied_package", denylist)
def test_no_denylisted_packages(denied_package: str, shell: ShellRunner):
    dpkg = Dpkg(shell)
    assert not dpkg.package_is_installed(
        denied_package
    ), f"Denylisted package {denied_package} is installed"
