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


@pytest.mark.feature(
    "gcp",
    reason="To ensure high performance network and disk capability, disable or remove the irqbalance daemon. This daemon does not correctly balance IRQ requests for the guest operating systems on virtual machine (VM) instances.",
)  # https://docs.cloud.google.com/compute/docs/import/configuring-imported-images
def test_package_irqbalance_not_installed_on_gcp(dpkg: Dpkg):
    assert not dpkg.package_is_installed(
        "irqbalance"
    ), f"Denylisted package irqbalance is installed on gcp"
