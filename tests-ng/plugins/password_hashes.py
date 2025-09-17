from pathlib import Path

import pytest


@pytest.fixture
def pam_common_password_text():
    """
    Read the raw text from /etc/pam.d/common-password file.
    """
    path = Path("/etc/pam.d/common-password")
    assert path.exists(), f"'{path}' is missing"
    return path.read_text(encoding="utf-8", errors="ignore")


@pytest.fixture
def pam_candidates(pam_common_password_text):
    """
    Parse /etc/pam.d/common-password and return all relevant
    'password ... [success=... default=ignore] ...' entries.
    """
    text = pam_common_password_text
    # Exclude comments and blank lines
    lines = [
        ln
        for ln in (l.rstrip() for l in text.splitlines())
        if ln and not ln.lstrip().startswith("#")
    ]

    # Find candidate lines: start with 'password' and contain success= and default=ignore
    candidates = []
    for line in lines:
        # check start token is 'password' (allow leading whitespace)
        if (
            line.lstrip().lower().startswith("password")
            and "success=" in line
            and "default=ignore" in line
        ):
            candidates.append(line)

    return candidates
