import pytest
from plugins.sshd import Sshd


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires sshd effective configuration")
@pytest.mark.root(reason="required to inspect SSH configuration")
def test_x11_forwarding_disabled(sshd: Sshd):
    """
    As per DISA STIG compliance requirements, the operating system must be
    configured to disable X11 forwarding to prevent unauthorized graphical
    session redirection over SSH.
    Ref: SRG-OS-000480-GPOS-00227
    """
    value = sshd.get_config_section("x11forwarding")

    assert value == "no", (
        f"stigcompliance: X11Forwarding is not disabled (value={value!r})"
    )


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="requires sshd effective configuration")
@pytest.mark.root(reason="required to inspect SSH configuration")
def test_x11_use_localhost_enabled(sshd: Sshd):
    """
    As per DISA STIG compliance requirements, the operating system must restrict
    X11 forwarding to localhost only to limit exposure when X11 forwarding is used.
    Ref: SRG-OS-000480-GPOS-00227
    """
    value = sshd.get_config_section("x11uselocalhost")

    assert value == "yes", (
        f"stigcompliance: X11UseLocalhost is not enabled (value={value!r})"
    )
