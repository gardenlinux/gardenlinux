import pytest

"""
Ref: SRG-OS-000324-GPOS-00125

Verify that the operating system prevents non-privileged users from executing
privileged functions to include disabling, circumventing, or altering
implemented security safeguards/countermeasures.
"""


@pytest.mark.feature("disaSTIGhigh")
def test_ctrl_alt_del_burst_is_disabled(parse_file):
    assert "CtrlAltDelBurstAction=none" in parse_file.lines("/etc/systemd/system.conf")
