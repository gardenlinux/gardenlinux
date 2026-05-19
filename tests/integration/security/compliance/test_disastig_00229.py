import pytest

"""
Ref: SRG-OS-000480-GPOS-00229

Verify the operating system does not allow an unattended or automatic logon to
the system.
"""


@pytest.mark.booted(reason="Requires functioning systemd")
def test_systemd_getty_autologin_is_not_enabled(systemd):
    for i in range(7):
        props = systemd.get_unit_properties(f"getty@tty{i}")
        assert "--autologin" not in props.get(
            "ExecStart", ""
        ), f"Autologin enabled on getty@tty{i}"
