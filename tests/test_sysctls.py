import pytest


@pytest.mark.booted
def test_sysctl_rp_filter(sysctl):
    assert sysctl["net.ipv4.conf.all.rp_filter"] != 1
    assert sysctl["net.ipv4.conf.default.rp_filter"] != 1


@pytest.mark.booted
@pytest.mark.feature("gardener")
def test_sysctl_dmesg_restrict(sysctl):
    assert sysctl["kernel.dmesg_restrict"] == 0
