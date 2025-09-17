import re

import pytest


@pytest.mark.security_id(325)
def test_password_entry_present(pam_candidates):
    """
    Ensure that exactly one password entry with [success=... default=ignore]
    exists in PAM config.
    """
    assert (
        len(pam_candidates) == 1
    ), f"Expected exactly one password entry, found {len(pam_candidates)}: {pam_candidates}"


@pytest.mark.security_id(325)
def test_password_entry_uses_strong_hash(pam_candidates):
    """
    Ensure that the password entry uses a strong hash algorithm (yescrypt or sha512).
    """
    assert (
        len(pam_candidates) == 1
    ), "No valid password entry to check for hash algorithm"
    test_line = pam_candidates[0]

    has_yescrypt = re.search(r"\byescrypt\b", test_line, re.IGNORECASE)
    has_sha512 = re.search(r"\bsha512\b", test_line, re.IGNORECASE)

    assert (
        has_yescrypt or has_sha512
    ), f"No 'yescrypt' or 'sha512' found in password entry: {test_line}"
