"""
Ref: SRG-OS-000324-GPOS-00125

Verify that the operating system prevents non-privileged users from executing
privileged functions to include disabling, circumventing, or altering
implemented security safeguards/countermeasures.
"""

import pytest


@pytest.mark.security_id(203695)
@pytest.mark.feature("disaSTIGhigh")
def test_ctrl_alt_del_burst_is_disabled(parse_file):
    """Verify systemd disables the Ctrl-Alt-Del reboot burst action."""
    config = parse_file.parse("/etc/systemd/system.conf", format="keyval")
    assert config["CtrlAltDelBurstAction"] == "none"
