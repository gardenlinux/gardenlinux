import pytest


@pytest.mark.testcov(
    [
        "GL-TESTCOV-cloud-config-sysctl-cloud",
        "GL-TESTCOV-openstackMetal-config-sysctl-cloud",
    ]
)
@pytest.mark.feature("cloud or (openstack and metal)")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_kernel_parameters_cannot_hardlink_what_you_do_not_own(sysctl):
    assert sysctl["fs.protected_hardlinks"] == 1


@pytest.mark.testcov(
    [
        "GL-TESTCOV-cloud-config-sysctl-cloud",
        "GL-TESTCOV-openstackMetal-config-sysctl-cloud",
    ]
)
@pytest.mark.feature("cloud or (openstack and metal)")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_kernel_parameters_cannot_symlink_what_you_do_not_own(sysctl):
    assert sysctl["fs.protected_symlinks"] == 1


@pytest.mark.testcov(
    [
        "GL-TESTCOV-cloud-config-sysctl-cloud",
        "GL-TESTCOV-openstackMetal-config-sysctl-cloud",
    ]
)
@pytest.mark.feature("cloud or (openstack and metal)")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_kernel_parameters_randomize_memory_allocation(sysctl):
    assert sysctl["kernel.randomize_va_space"] == 2


@pytest.mark.booted
def test_sysctl_rp_filter(sysctl):
    assert sysctl["net.ipv4.conf.all.rp_filter"] != 1
    assert sysctl["net.ipv4.conf.default.rp_filter"] != 1
