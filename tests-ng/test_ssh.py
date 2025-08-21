import pwd
import pytest
from plugins.sshd import Sshd
from plugins.systemd import Systemd
from plugins.utils import equals_ignore_case, get_normalized_sets, is_set
import os

required_sshd_config = {
    "HostKey": {
        "/etc/ssh/ssh_host_ed25519_key",
        "/etc/ssh/ssh_host_rsa_key",
    },
    "KexAlgorithms": {
        "sntrup761x25519-sha512",
        "sntrup761x25519-sha512@openssh.com",
        "mlkem768x25519-sha256",
        "curve25519-sha256",
        "curve25519-sha256@libssh.org",
        "ecdh-sha2-nistp256",
        "ecdh-sha2-nistp384",
        "ecdh-sha2-nistp521",
    },
    "Ciphers": {
        "chacha20-poly1305@openssh.com",
        "aes128-ctr",
        "aes192-ctr",
        "aes256-ctr",
        "aes128-gcm@openssh.com",
        "aes256-gcm@openssh.com",
    },
    "MACs": {
        "umac-64-etm@openssh.com",
        "umac-128-etm@openssh.com",
        "hmac-sha2-256-etm@openssh.com",
        "hmac-sha2-512-etm@openssh.com",
        "hmac-sha1-etm@openssh.com",
        "umac-64@openssh.com",
        "umac-128@openssh.com",
        "hmac-sha2-256",
        "hmac-sha2-512",
        "hmac-sha1",
    },
    "AuthenticationMethods": "publickey",
    "LogLevel": "VERBOSE",
    "Subsystem": "sftp /usr/lib/openssh/sftp-server -f AUTHPRIV -l INFO",
    "PermitRootLogin": "No",
    "X11Forwarding": "no",
    "UsePAM": "yes",
}


@pytest.mark.booted(reason="Calling sshd -T requires a booted system")
@pytest.mark.root(reason="Calling sshd -T requires root")
@pytest.mark.feature("ssh")
@pytest.mark.parametrize("sshd_config_item", required_sshd_config)
def test_sshd_has_required_config(sshd_config_item: str, sshd: Sshd):
    actual_value = sshd.get_config_section(sshd_config_item)
    expected_value = required_sshd_config[sshd_config_item]
    if is_set(expected_value):
        if not is_set(actual_value):
            actual_value = set(str(actual_value).split(','))
        actual_set, expected_set = get_normalized_sets(actual_value, expected_value)
        assert expected_set.issubset(actual_value), f"{sshd_config_item}: missing values {expected_set - actual_set}"
    else:
        assert equals_ignore_case(actual_value, expected_value), f"{sshd_config_item}: expected {expected_value}, got {actual_value}"

@pytest.mark.feature("ssh")
def test_users_have_no_authorized_keys():
    skip_users = {"nologin", "sync"}
    skip_shells = {"/bin/false"}
    files_to_check = ["authorized_keys", "authorized_keys2"]

    for entry in pwd.getpwall():
        if entry.pw_name in skip_users or entry.pw_shell in skip_shells:
            continue

        ssh_dir = os.path.join(entry.pw_dir, ".ssh")
        for filename in files_to_check:
            key_path = os.path.join(ssh_dir, filename)
            assert not os.path.exists(key_path), (
                f"user '{entry.pw_name}' should not have an authorized_keys file: {key_path}"
            )


@pytest.mark.booted(reason="Starting the unit requires a booted system")
@pytest.mark.modify(reason="Starting the unit modifies the system state")
@pytest.mark.root(reason="Starting the unit requires root")
@pytest.mark.feature("ssh")
def test_ssh_unit_running(systemd: Systemd):
    systemd.start_unit('ssh')
    assert systemd.is_running('ssh'), f"Required systemd unit for ssh.service is not running"
