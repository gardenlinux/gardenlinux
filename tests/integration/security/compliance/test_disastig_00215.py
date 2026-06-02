import pytest

"""
Ref: SRG-OS-000471-GPOS-00215

Verify the operating system generates audit records for privileged activities
or other system-level access.
"""


def test_disastig_00215():
    pytest.skip(
        reason="covered by test_disastig_00209.py, test_disastig_00210.py, test_disastig_00211.py test_disastig_00220.py test_disastig_00222.py"
    )
