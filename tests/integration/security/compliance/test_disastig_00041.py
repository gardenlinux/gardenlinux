import pytest

"""
Ref: SRG-OS-000073-GPOS-00041

Verify the operating system stores only encrypted representations of passwords.
"""


@pytest.mark.security_id(203629)
@pytest.mark.feature("not container")
@pytest.mark.booted(reason="requires booted system")
@pytest.mark.root(reason="required for passwd checks")
def test_passwd_does_not_store_passwords(passwd_entries):
    assert all(
        entry.password in ("x", "*", "!") for entry in passwd_entries
    ), "stigcompliance: plaintext password found in /etc/passwd"


@pytest.mark.security_id(203629)
@pytest.mark.feature("not container")
@pytest.mark.booted(reason="requires booted system")
@pytest.mark.root(reason="required for passwd checks")
def test_shadow_passwords_are_hashed(shadow_entries):
    assert all(
        entry.encrypted_password == ""
        or entry.encrypted_password.startswith(("!", "*", "$"))
        for entry in shadow_entries
    ), "stigcompliance: non-hashed password detected in /etc/shadow"


@pytest.mark.security_id(203629)
@pytest.mark.feature("not container")
@pytest.mark.booted(reason="requires booted system")
@pytest.mark.root(reason="required for passwd checks")
def test_shadow_uses_strong_hashing_algorithm(shadow_entries):
    assert all(
        entry.encrypted_password == ""
        or entry.encrypted_password.startswith(("!", "*", "$y$", "$6$"))
        for entry in shadow_entries
    ), "stigcompliance: weak password hashing algorithm detected"
