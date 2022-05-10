from helper.tests.blacklisted_packages import blacklisted_packages
import pytest

@pytest.mark.parametrize(
    "package",
    [
        "rlogin",
        "rsh",
        "rcp",
        "telnet",
        "libdb5.3:amd64",
        "libdb5.3:arm64",
        "libssl1.1:amd64",
        "libssl1.1:arm64"
    ]
)
@pytest.mark.skip_feature("base")
def test_blacklisted_packages(client, package):
    blacklisted_packages(client, package)
