import pytest

"""
Ref: SRG-OS-000118-GPOS-00060

Verify the operating system disables accounts inactive for more than 35 days.
Setting INACTIVE in /etc/default/useradd ensures new accounts inherit this
policy automatically.
"""

USERADD_DEFAULTS = "/etc/default/useradd"


@pytest.mark.testcov(["GL-TESTCOV-disaSTIGmedium-config-useradd-inactive"])
@pytest.mark.feature(
    "disaSTIGmedium", reason="account inactivity timeout is set by disaSTIGmedium"
)
@pytest.mark.security_id(203648)
def test_useradd_inactive_is_35(parse_file) -> None:
    """Verify INACTIVE in /etc/default/useradd is 35 (SRG-OS-000118-GPOS-00060)."""
    config = parse_file.parse(USERADD_DEFAULTS, format="keyval")
    assert (
        config["INACTIVE"] == "35"
    ), f"stigcompliance: INACTIVE in {USERADD_DEFAULTS} is {config['INACTIVE']!r}, expected '35'"
