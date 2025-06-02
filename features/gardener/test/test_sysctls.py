import pytest
from helper.tests.sysctl import check_sysctl


@pytest.mark.parametrize(
    "key,operator,value",
    [
        ("net.ipv4.conf.all.rp_filter", "isnotornotset", "1"),
        ("net.ipv4.conf.default.rp_filter", "isnotornotset", "1"),
    ],
)
def test_sysctls(client, key, operator, value, non_provisioner_chroot):
    check_sysctl(client, key, operator, value)
