from typing import List

import pytest
from plugins.file import File
from plugins.parse_file import ParseFile


@pytest.mark.testcov("GL-TESTCOV-disaSTIGmedium-config-kernel-cmdline-audit")
@pytest.mark.feature("disaSTIGmedium")
def test_audit_cmdline_config_file_exists(file: File):
    """
    As per DISA STIG compliance requirements, the operating system must begin
    auditing sessions when the system starts up.
    This test verifies that the audit kernel cmdline config file exists.
    Ref: SRG-OS-000254-GPOS-00095
    """
    assert file.is_regular_file(
        "/etc/kernel/cmdline.d/90-audit.cfg"
    ), "stigcompliance: /etc/kernel/cmdline.d/90-audit.cfg must exist"


@pytest.mark.testcov("GL-TESTCOV-disaSTIGmedium-config-kernel-cmdline-audit")
@pytest.mark.feature("disaSTIGmedium")
def test_audit_cmdline_config_file_content(parse_file: ParseFile):
    """
    As per DISA STIG compliance requirements, the operating system must begin
    auditing sessions when the system starts up.
    This test verifies that the audit kernel cmdline config contains audit=1.
    Ref: SRG-OS-000254-GPOS-00095
    """
    lines = parse_file.lines("/etc/kernel/cmdline.d/90-audit.cfg")
    assert (
        "audit=1" in lines
    ), "stigcompliance: /etc/kernel/cmdline.d/90-audit.cfg must contain audit=1"


@pytest.mark.testcov("GL-TESTCOV-disaSTIGmedium-config-kernel-cmdline-audit")
@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.booted(reason="kernel cmdline is only available on a booted system")
def test_audit_enabled_in_kernel_cmdline(kernel_cmdline: List[str]):
    """
    As per DISA STIG compliance requirements, the operating system must begin
    auditing sessions when the system starts up.
    This test verifies that audit=1 is present in the runtime kernel cmdline.
    Ref: SRG-OS-000254-GPOS-00095
    """
    assert (
        "audit=1" in kernel_cmdline
    ), "stigcompliance: kernel must be booted with audit=1"
