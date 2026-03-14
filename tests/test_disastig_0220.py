import re


def test_sshd_unit_is_journald_friendly(shell):
    """
    The sshd.service unit must forward stdout/stderr to the journal.
    """
    result = shell(
        cmd="systemctl show -p StandardOutput,StandardError sshd.service",
        capture_output=True,
    )
    assert (
        "StandardOutput=journal" in result.stdout
    ), f"sshd stdout not directed to journal: {result.stdout}"
    assert re.search(
        r"StandardError=(journal|inherit)", result.stdout
    ), f"sshd stderr not directed to journal or inherit: {result.stdout}"


def test_pam_unix_is_in_use():
    """
    pam_unix is responsible for user sessions logging
    """
    pam_unix_required = re.compile(
        r"^session\s+required\s+pam_unix\.so\s*$", re.MULTILINE
    )
    with open("/etc/pam.d/common-session") as f:
        assert re.search(pam_unix_required, f.read())
