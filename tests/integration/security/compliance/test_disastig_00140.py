import pytest

"""
Ref: SRG-OS-000352-GPOS-00140

Verify the operating system provides a report generation capability that
supports after-the-fact investigations of security incidents.
"""


@pytest.mark.feature("log")
def test_report_generation_capability(file):
    assert file.exists("/usr/sbin/ausearch")
    assert file.exists("/usr/sbin/aureport")
