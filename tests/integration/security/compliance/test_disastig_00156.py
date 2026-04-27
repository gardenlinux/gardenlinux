import re

import pytest
from plugins.find import Find
from plugins.parse_file import ParseFile


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.root(reason="requires access to /etc/sudoers and /etc/sudoers.d")
def test_sudoers_no_nopasswd(find: Find, parse_file: ParseFile):
    """
    As per DISA STIG compliance requirements, the operating system must require
    users to re-authenticate for privilege escalation.
    This test verifies that no sudoers file grants passwordless privilege escalation
    via NOPASSWD or !authenticate.
    Ref: SRG-OS-000373-GPOS-00156
    """
    nopasswd_pattern = re.compile(r"NOPASSWD", re.IGNORECASE)
    noauthenticate_pattern = re.compile(r"!authenticate", re.IGNORECASE)

    find.root_paths = "/etc/sudoers.d"
    find.entry_type = "files"
    paths_to_check = ["/etc/sudoers"] + list(find)

    for path in paths_to_check:
        lines = parse_file.lines(path, ignore_missing=True)
        if not lines:
            continue
        assert (
            nopasswd_pattern not in lines
        ), f"stigcompliance: NOPASSWD found in sudoers file {path}"
        assert (
            noauthenticate_pattern not in lines
        ), f"stigcompliance: !authenticate found in sudoers file {path}"
