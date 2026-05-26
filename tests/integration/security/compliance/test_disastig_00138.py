import pytest

"""
Ref: SRG-OS-000351-GPOS-00138

Verify the operating system provides a report generation capability that
supports on-demand audit review and analysis.
"""


@pytest.mark.feature("log")
def test_disastig_00138():
    pytest.skip(reason="covered by test_disastig_00140.py")
