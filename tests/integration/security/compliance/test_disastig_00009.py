import re

import pytest
from plugins.find import Find
from plugins.parse_file import ParseFile

PAM_DIR = "/etc/pam.d"


@pytest.mark.feature("not container and not lima and not gardener")
@pytest.mark.root(reason="required to verify PAM authentication enforcement")
def test_session_lock_requires_reauthentication(parse_file: ParseFile, find: Find):
    """
    As per DISA STIG compliance requirements, the operating system must retain a
    user's session lock until that user reestablishes access using established
    identification and authentication procedures.
    This test verifies that PAM configuration enforces authentication using
    standard authentication modules and does not allow bypass mechanisms.
    Ref: SRG-OS-000028-GPOS-00009
    """

    find.root_paths = PAM_DIR
    find.entry_type = "files"

    auth_required_pattern = re.compile(r"^\s*auth\s+.*pam_unix\.so", re.IGNORECASE)
    insecure_pattern = re.compile(r"\b(nullok|nopasswd)\b", re.IGNORECASE)

    auth_found = False

    for path in find:
        lines = parse_file.lines(path, ignore_missing=True)

        if auth_required_pattern in lines:
            auth_found = True

        assert (
            insecure_pattern not in lines
        ), f"stigcompliance: insecure PAM option allowing authentication bypass found in {path}"

    assert (
        auth_found
    ), "stigcompliance: no PAM authentication mechanism enforcing re-authentication found"
