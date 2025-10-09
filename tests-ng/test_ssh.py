import os
import pwd

import pytest
from handlers.services import service_ssh
from plugins.sshd import Sshd
from plugins.systemd import Systemd
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


@pytest.mark.booted(reason="Calling sshd -T requires a booted system")
@pytest.mark.root(reason="Calling sshd -T requires root")
@pytest.mark.feature("ssh")
@pytest.mark.parametrize("sshd_config_item", required_sshd_config)
def test_sshd_has_required_config(sshd_config_item: str, sshd: Sshd):
    actual_value = sshd.get_config_section(sshd_config_item)
    expected_value = required_sshd_config[sshd_config_item]
    if is_set(expected_value):
        if actual_value is None:
            actual_value = set()
        elif not is_set(actual_value):
            actual_value = set(str(actual_value).split(","))
        # Ensure actual_value is a set at this point
        assert isinstance(
            actual_value, set
        ), f"actual_value should be a set, got {type(actual_value)}"
        actual_set, expected_set = get_normalized_sets(actual_value, expected_value)
        assert expected_set.issubset(
            actual_set
        ), f"{sshd_config_item}: missing values {expected_set - actual_set}"
    else:
        assert equals_ignore_case(
            str(actual_value or ""), str(expected_value)
        ), f"{sshd_config_item}: expected {expected_value}, got {actual_value}"


@pytest.mark.feature(
    "ssh and not (ali or aws or azure or openstack)",
    reason="We want no authorized_keys for unmanaged users",
)
def test_users_have_no_authorized_keys(expected_users):
    skip_users = {"nologin", "sync"}
    skip_shells = {"/bin/false"}
    files_to_check = ["authorized_keys", "authorized_keys2"]

    for entry in pwd.getpwall():
        if any(
            [
                entry.pw_name in skip_users,
                entry.pw_shell in skip_shells,
                entry.pw_name in expected_users,
            ]
        ):
            continue

        ssh_dir = os.path.join(entry.pw_dir, ".ssh")
        for filename in files_to_check:
            key_path = os.path.join(ssh_dir, filename)
            assert not os.path.exists(
                key_path
            ), f"user '{entry.pw_name}' should not have an authorized_keys file: {key_path}"


@pytest.mark.feature(
    "ssh and (ali or aws or azure or openstack)",
    reason="ALI, AWS, Azure and OpenStack auto generate authorized_keys for root with a hint to use another user",
)
def test_users_have_only_root_authorized_keys_cloud(expected_users):
    skip_users = {"nologin", "sync"}
    skip_shells = {"/bin/false"}
    files_to_check = ["authorized_keys", "authorized_keys2"]

    for entry in pwd.getpwall():
        if any(
            [
                entry.pw_name in skip_users,
                entry.pw_shell in skip_shells,
                entry.pw_name in expected_users,
            ]
        ):
            continue

        ssh_dir = os.path.join(entry.pw_dir, ".ssh")
        for filename in files_to_check:
            key_path = os.path.join(ssh_dir, filename)
            if os.path.exists(key_path):
                if entry.pw_name != "root":
                    assert (
                        False
                    ), f"user '{entry.pw_name}' should not have an authorized_keys file: {key_path}"
                else:
                    # Check if the file contains only the specific restricted root key
                    with open(key_path, "r") as f:
                        content = f.read()
                        lines = content.split("\n")
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith("#"):
                                # Only allow root with specific redirect command
                                if any(
                                    f'command="echo \'Please login as the user \\"{user}\\" rather than the user \\"root\\".\''
                                    in line
                                    for user in expected_users
                                ):
                                    continue
                                else:
                                    assert (
                                        False
                                    ), f"user '{entry.pw_name}' has unauthorized SSH key in file: {key_path}"


@pytest.mark.booted(reason="Starting the unit requires a booted system")
@pytest.mark.modify(reason="Starting the unit modifies the system state")
@pytest.mark.root(reason="Starting the unit requires root")
@pytest.mark.feature("ssh")
def test_ssh_service_running(systemd: Systemd, service_ssh):
    assert systemd.is_active("ssh"), f"Required systemd unit for ssh.service is not running"
