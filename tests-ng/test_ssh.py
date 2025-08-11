import pytest
from plugins.shell import ShellRunner
from plugins.systemd import Systemd
from plugins.sshd import Sshd
from plugins.utils import equals_ignore_case, get_normalized_sets, is_set

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

@pytest.fixture
@pytest.mark.booted
@pytest.mark.root
@pytest.mark.feature("ssh")
@pytest.mark.parametrize("sshd_config_item", required_sshd_config)
def test_sshd_has_required_config(sshd_config_item: str, shell: ShellRunner):
    sshd = Sshd(shell)
    yield sshd
    actual_value = sshd.get_config_section(sshd_config_item)
    expected_value = required_sshd_config[sshd_config_item]
    if is_set(expected_value):
        assert is_set(actual_value), f"{actual_value} should be a set"
        actual_set, expected_set = get_normalized_sets(actual_value, expected_value)
        missing_sshd_configuration = expected_set - actual_set
        assert not missing_sshd_configuration, f"{sshd_config_item}: missing values {missing_sshd_configuration}"
    else:
        assert equals_ignore_case(actual_value, expected_value), f"{sshd_config_item}: expected {expected_value}, got {actual_value}"
