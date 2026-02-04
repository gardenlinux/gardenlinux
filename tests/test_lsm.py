import pytest


@pytest.mark.booted
@pytest.mark.feature("_selinux")
def test_lsm_selinux(lsm):
    assert "selinux" in lsm
    assert "apparmor" not in lsm


@pytest.mark.booted
@pytest.mark.feature("gardener")
def test_lsm_gardener(lsm):
    assert "apparmor" in lsm
    assert "selinux" not in lsm


@pytest.mark.booted
def test_lsm_common(lsm):
    required = {"landlock", "lockdown", "capability", "yama"}
    missing = required - set(lsm)
    assert not missing, f"missing lsm(s): {', '.join(sorted(missing))}"
