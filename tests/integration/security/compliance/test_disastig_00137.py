import pytest

"""
Ref: SRG-OS-000351-GPOS-00137

Verify the operating system provides an audit reduction capability that
supports after-the-fact investigations of security incidents.
"""


@pytest.mark.feature("log")
def test_disastig_00137():
    pytest.skip(reason="covered by test_disastig_00140.py")
