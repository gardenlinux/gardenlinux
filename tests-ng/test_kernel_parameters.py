import pytest


@pytest.mark.feature("cloud or openstackbaremetal")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_kernel_parameters_cannot_hardlink_what_you_do_not_own(sysctl):
    assert sysctl["fs.protected_hardlinks"] == "1"


@pytest.mark.feature("cloud or openstackbaremetal")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_kernel_parameters_cannot_symlink_what_you_do_not_own(sysctl):
    assert sysctl["fs.protected_symlinks"] == "1"


@pytest.mark.feature("cloud or openstackbaremetal")
@pytest.mark.booted(reason="sysctl needs a booted system")
def test_kernel_parameters_randomize_memory_allocation(sysctl):
    assert sysctl["kernel.randomize_va_space"] == "2"
