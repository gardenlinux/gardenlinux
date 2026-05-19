import pytest

"""
Ref: SRG-OS-000205-GPOS-00083

Verify the operating system defines proper permissions on the system log
directory /var/log so that unauthorized users cannot access log data.
"""

VAR_LOG = "/var/log"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-var-log-file-permissions"])
@pytest.mark.feature("disaSTIGmedium", reason="log directory permissions are hardened by disaSTIGmedium")
def test_var_log_has_755_permissions(file) -> None:
    """Verify /var/log directory has permissions 755 (SRG-OS-000205-GPOS-00083)."""
    assert file.has_permissions(
        VAR_LOG, "rwxr-xr-x"
    ), f"stigcompliance: {VAR_LOG} permissions are {file.get_mode(VAR_LOG)!r}, expected 0755"
