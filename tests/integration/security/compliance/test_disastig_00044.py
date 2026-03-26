import re

import pytest
from plugins.file import File
from plugins.parse_file import ParseFile

LOGIN_DEFS = "/etc/login.defs"


@pytest.mark.feature("stig")
@pytest.mark.booted(reason="required to read system password policy configuration")
@pytest.mark.root(reason="required to read system password policy configuration")
def test_maximum_password_lifetime_file_exists(file: File):
    """
    As per DISA STIG requirement, the operating system must enforce
    a maximum password lifetime of 60 days.
    Ref: SRG-OS-000076-GPOS-00044
    """
    assert file.exists(LOGIN_DEFS), f"stigcompliance: {LOGIN_DEFS} does not exist"


@pytest.mark.feature("stig")
@pytest.mark.booted(reason="required to read system password policy configuration")
@pytest.mark.root(reason="required to read system password policy configuration")
def test_maximum_password_lifetime_value(parse_file: ParseFile):
    """
    As per DISA STIG requirement, the operating system must enforce
    a maximum password lifetime of 60 days.
    Ref: SRG-OS-000076-GPOS-00044
    """

    lines = parse_file.lines(LOGIN_DEFS)

    pattern = re.compile(r"^PASS_MAX_DAYS\s+(\d+)")

    for line in lines:
        match = pattern.search(line)
        if match:
            value = int(match.group(1))

            assert (
                value <= 60
            ), f"stigcompliance: PASS_MAX_DAYS is {value}, must be 60 or less"

            return

    assert False, "stigcompliance: PASS_MAX_DAYS not configured in login.defs"
