from helper.tests.blacklisted_packages import blacklisted_packages
import pytest

@pytest.mark.parametrize(
    "package",
    [
        "irqbalance"
    ]
)
@pytest.mark.skip_feature("gcp")
def test_blacklisted_packages(client, package):
    blacklisted_packages(client, package)
