import pytest
from plugins.sshd import Sshd


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires SSH runtime configuration")
@pytest.mark.root(reason="requires access to SSH configuration")
def test_x11_forwarding_is_disabled(sshd: Sshd):
    """
    As per DISA STIG compliance requirements, the operating system must be configured
    so that the SSH daemon does not allow X11 Forwarding.
    This test verifies that X11Forwarding is set to no in the SSH daemon configuration.
    Ref: SRG-OS-000480-GPOS-00227
    """
    assert sshd.get_config_section("x11forwarding") == "no", (
        "stigcompliance: X11Forwarding must be set to no in sshd configuration"
    )


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires SSH runtime configuration")
@pytest.mark.root(reason="requires access to SSH configuration")
def test_x11_use_localhost_is_enabled(sshd: Sshd):
    """
    As per DISA STIG compliance requirements, the operating system must be configured
    so that the SSH daemon does not allow X11 Forwarding.
    This test verifies that X11UseLocalhost is set to yes in the SSH daemon configuration.
    Ref: SRG-OS-000480-GPOS-00227
    """
    assert sshd.get_config_section("x11uselocalhost") == "yes", (
        "stigcompliance: X11UseLocalhost must be set to yes in sshd configuration"
    )
