import re

import pytest
from plugins.file import File
from plugins.parse_file import ParseFile

LOGIN_DEFS = "/etc/login.defs"


@pytest.mark.feature("stig")
@pytest.mark.root(reason="required to read system password policy configuration")
def test_minimum_password_lifetime_configured(file: File):
    """
    As per DISA STIG requirement, the operating system must enforce
    a minimum password lifetime of at least 1 day.
    This test verifies that /etc/login.defs exists.
    Ref: SRG-OS-000075-GPOS-00043
    """
    assert file.exists(LOGIN_DEFS), f"stigcompliance: {LOGIN_DEFS} does not exist"


@pytest.mark.feature("stig")
@pytest.mark.root(reason="required to read system password policy configuration")
def test_minimum_password_lifetime_value(parse_file: ParseFile):
    """
    As per DISA STIG requirement, the operating system must enforce
    a minimum password lifetime of at least 1 day.
    This test verifies that PASS_MIN_DAYS is configured to 1 or greater.
    Ref: SRG-OS-000075-GPOS-00043
    """

    lines = parse_file.lines(LOGIN_DEFS)

    pattern = re.compile(r"^PASS_MIN_DAYS\s+(\d+)")

    for line in lines:
        match = pattern.search(line)
        if match:
            value = int(match.group(1))

            assert (
                value >= 1
            ), f"stigcompliance: PASS_MIN_DAYS is {value}, must be at least 1"

            return

    assert False, "stigcompliance: PASS_MIN_DAYS not configured in login.defs"
