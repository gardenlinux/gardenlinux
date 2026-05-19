import pytest

"""
Ref: SRG-OS-000142-GPOS-00071

Verify the operating system is configured to prevent unauthorized connection
of devices. The disaSTIG sysctl configuration file must be present to ensure
kernel parameter hardening is applied.
"""

SYSCTL_DISASTIG = "/etc/sysctl.d/99-disaSTIG.conf"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-sysctl-disaSTIG"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="sysctl hardening config is deployed by disaSTIGmedium"
)
def test_sysctl_disastig_conf_exists(file) -> None:
    """Verify /etc/sysctl.d/99-disaSTIG.conf exists (SRG-OS-000142-GPOS-00071)."""
    assert file.exists(
        SYSCTL_DISASTIG
    ), f"stigcompliance: {SYSCTL_DISASTIG} does not exist"
