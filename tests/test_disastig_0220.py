import pytest

"""
Ref: SRG-OS-000475-GPOS-00220

Verify the operating system generates audit records for all direct access to the information system.
"""


@pytest.mark.booted(reason="requires running systemd")
def test_journald_should_not_store_logs_in_memory(shell):
    """
    Confirm that journald is not configured to store logs in memory
    """
    result = shell(
        "systemd-analyze cat-config /etc/systemd/journald.conf", capture_output=True
    )
    config = [
        v
        for line in result.stdout.splitlines()
        if line.startswith("Storage=")
        for k, v in [line.split("=")]
    ]
    if config:
        assert config[0] != "volatile"


@pytest.mark.feature("ssh")
def test_sshd_log_level_is_set_to_verbose(parse_file):
    """
    Confirm sshd log level is not manipulated
    """
    config = parse_file.parse("/etc/ssh/sshd_config", format="spacedelim")
    assert config["LogLevel"] == "VERBOSE"


@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="requires running systemd")
def test_sshd_unit_is_journald_friendly(systemd):
    """
    The sshd.service unit must forward stdout/stderr to the journal.
    """
    result = systemd.get_unit_properties("ssh", "StandardOutput", "StandardError")
    assert (
        result["StandardOutput"] == "journal"
    ), f"sshd stdout not directed to journal: {result['StandardOutput']}"
    assert result["StandardError"] in [
        "journal",
        "inherit",
    ], f"sshd stderr not directed to journal or inherit: {result['StandardError']}"


@pytest.mark.parametrize(
    "pam_config", ["/etc/pam.d/common-session"], indirect=["pam_config"]
)
def test_pam_unix_is_in_use(pam_config):
    """
    pam_unix is responsible for user sessions logging
    """
    results = pam_config.find_entries(
        type_="session",
        control_contains="required",
        module_contains="pam_unix.so",
    )
    assert (
        len(results) == 1
    ), "pam_unix should be required for user sessions logging to work"
