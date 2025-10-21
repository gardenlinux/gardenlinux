import pytest


# @pytest.mark.security_id(325)
@pytest.mark.parametrize(
    "pam_config", ["/etc/pam.d/common-password"], indirect=["pam_config"]
)
def test_password_entry_present(pam_config):
    """
    Ensure that exactly one password entry with [success=... default=ignore]
    exists in PAM config.
    """
    candidates = pam_config.find_entries(
        type_="password",
        control_contains={"success": "*", "default": "ignore"},
        match_all=True,
    )
    assert (
        len(candidates) == 1
    ), f"Expected exactly one password entry, found {len(candidates)}: {candidates}"


# @pytest.mark.security_id(325)
@pytest.mark.parametrize(
    "pam_config", ["/etc/pam.d/common-password"], indirect=["pam_config"]
)
def test_password_entry_uses_strong_hash(pam_config):
    """
    Ensure that the password entry uses a strong hash algorithm (yescrypt or sha512).
    """
    candidates = pam_config.find_entries(
        type_="password",
        control_contains={"success": "*", "default": "ignore"},
        match_all=True,
    )

    # Validate that this is only defined a single time
    # to ensure no feature has appended different options
    # multiple times
    assert (
        len(candidates) == 1
    ), f"Expected exactly one 'password ... [success=... default=ignore] ...' entry, found {len(candidates)}: {candidates}"
    entry = candidates[0]

    # Validate the entry for 'sha512' or 'yescrypt'
    # We're using YESCRYPT instead of sha512 because it offers more
    # resistance to offline attacks.
    # https://www.openwall.com/yescrypt/
    assert (
        "yescrypt" in entry.options or "sha512" in entry.options
    ), f"Weak or unknown hash algorithm used: {entry.options}"
