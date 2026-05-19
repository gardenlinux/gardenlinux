import shutil
from tempfile import TemporaryDirectory

import pytest

"""
Ref: SRG-OS-000354-GPOS-00142

Verify the operating system does not alter original content or time ordering of
audit records when it provides a report generation capability.
"""


@pytest.mark.feature("log")
@pytest.mark.root(reason="Needs to access root-owned audit.log")
def test_audit_report_does_not_alter_original_audit_logs(shell, file):
    with TemporaryDirectory(prefix="pytest-disa-stig-") as tmpd:
        shutil.copy("/var/log/audit/audit.log", f"{tmpd}/audit.log")
        before_report_checksum = file.checksum(f"{tmpd}/audit.log")
        shell(f"aureport -if {tmpd}/audit.log")
        after_report_checksum = file.checksum(f"{tmpd}/audit.log")
    assert before_report_checksum == after_report_checksum
