import re

import pytest

"""
Ref: SRG-OS-000445-GPOS-00199

Verify the operating system verifies correct operation of all security
functions.
"""

AIDE_CONF = "/etc/aide/aide.conf"
AIDE_TOOLS = [
    "/sbin/auditctl",
    "/sbin/auditd",
    "/sbin/ausearch",
    "/sbin/aureport",
    "/sbin/autrace",
    "/sbin/audispd",
    "/sbin/augenrules",
]


@pytest.mark.security_id(203756)
@pytest.mark.feature("log")
@pytest.mark.booted("Needs working systemd")
def test_auditd_service_active(systemd):
    assert systemd.is_active("auditd")


@pytest.mark.security_id(203756)
@pytest.mark.feature("log")
@pytest.mark.booted("Needs working systemd")
def test_systemd_configured_to_restart_auditd_service(systemd):
    assert systemd.get_unit_properties("auditd")["Restart"] != "no"


@pytest.mark.security_id(203756)
@pytest.mark.feature("_selinux")
def test_selinux_enabled(lsm):
    assert "selinux" in lsm


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-service-aide-init-enable"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="aide-init.service is enabled by disaSTIGmedium"
)
@pytest.mark.security_id(203756)
@pytest.mark.testcov(["GL-TESTCOV-aide-service-aide-init-enable"])
@pytest.mark.feature("aide", reason="aide-init.service is enabled by the aide feature")
@pytest.mark.booted(reason="requires systemd to query unit enable state")
def test_aide_init_service_is_enabled(systemd) -> None:
    assert systemd.is_enabled(
        "aide-init.service"
    ), "stigcompliance: aide-init.service is not enabled"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-service-aide-check-timer-enable"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="aide-check.timer is enabled by disaSTIGmedium"
)
@pytest.mark.security_id(203756)
@pytest.mark.testcov(["GL-TESTCOV-aide-service-aide-check-timer-enable"])
@pytest.mark.feature("aide", reason="aide-check.timer is enabled by the aide feature")
@pytest.mark.booted(reason="requires systemd to query unit enable state")
def test_aide_check_timer_is_enabled(systemd) -> None:
    assert systemd.is_enabled(
        "aide-check.timer"
    ), "stigcompliance: aide-check.timer is not enabled"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-aide-audit-tools"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="AIDE monitors audit tools as configured by disaSTIGmedium"
)
def test_aide_conf_monitors_audit_tools(parse_file) -> None:
    missing = [
        tool
        for tool in AIDE_TOOLS
        if not re.compile(rf"^{re.escape(tool)}.+sha512", re.MULTILINE)
        in parse_file.lines(AIDE_CONF)
    ]
    assert (
        not missing
    ), f"stigcompliance: AIDE does not monitor these tools with sha512 in {AIDE_CONF}: {missing}"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-aide-silent-reports"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="AIDE SILENTREPORTS is configured by disaSTIGmedium"
)
def test_aide_default_silentreports_is_no(parse_file) -> None:
    config = parse_file.parse("/etc/default/aide", format="keyval")
    assert config.get("SILENTREPORTS") == "no", (
        f"stigcompliance: SILENTREPORTS in /etc/default/aide is "
        f"{config.get('SILENTREPORTS')!r}, expected 'no'"
    )
