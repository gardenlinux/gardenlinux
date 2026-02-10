import os
import pwd

import pytest
from plugins.file import File
from plugins.parse_file import ParseFile
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


FIPS_REASON = "FIPS uses different values for the KEX and Cipher."


@pytest.mark.setting_ids(["GL-SET-ssh-config-ssh-sshd-config"])
@pytest.mark.booted(reason="Calling sshd -T requires a booted system")
@pytest.mark.root(reason="Calling sshd -T requires root")
@pytest.mark.feature("ssh")
@pytest.mark.parametrize("sshd_config_item", required_sshd_config)
@pytest.mark.feature("not _fips", reason=FIPS_REASON)
@pytest.mark.feature("not cis", reason="CIS has specific KEX and MACs")
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
def test_users_have_no_authorized_keys(expected_users, file: File):
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
            assert not file.exists(
                key_path
            ), f"user '{entry.pw_name}' should not have an authorized_keys file: {key_path}"


@pytest.mark.feature(
    "ssh and (ali or aws or azure or openstack)",
    reason="ALI, AWS, Azure and OpenStack auto generate authorized_keys for root with a hint to use another user",
)
def test_users_have_only_root_authorized_keys_cloud(
    expected_users, file, parse_file: ParseFile
):
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
            if file.exists(key_path):
                if entry.pw_name != "root":
                    assert (
                        False
                    ), f"user '{entry.pw_name}' should not have an authorized_keys file: {key_path}"
                else:
                    # Check if the file contains only the specific restricted root key
                    lines = parse_file.lines(key_path)
                    if not lines.content.strip():
                        # Allow empty authorized_keys for root on cloud images
                        continue
                    expected_patterns = [
                        f'command="echo \'Please login as the user \\"{user}\\" rather than the user \\"root\\".\''
                        for user in expected_users
                    ]
                    # Check that at least one expected pattern exists in the file
                    # (The file should only contain authorized keys with redirect commands)
                    if not any(pattern in lines for pattern in expected_patterns):
                        assert (
                            False
                        ), f"user '{entry.pw_name}' has unauthorized SSH key in file: {key_path}"


@pytest.mark.booted(reason="Starting the unit requires a booted system")
@pytest.mark.modify(reason="Starting the unit modifies the system state")
@pytest.mark.root(reason="Starting the unit requires root")
@pytest.mark.feature("ssh")
def test_ssh_service_running(systemd: Systemd, service_ssh):
    assert systemd.is_active(
        "ssh"
    ), f"Required systemd unit for ssh.service is not running"


# =============================================================================
# ssh Feature - SSH Extended Configuration
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-ssh-config-no-init-ssh",
    ]
)
@pytest.mark.feature("ssh")
def test_ssh_no_init_script(file: File):
    """Test that SSH does not have init script"""
    assert not file.exists(
        "/etc/init.d/ssh"
    ), "SSH should not have init.d script (using systemd)"


@pytest.mark.setting_ids(
    [
        "GL-SET-ssh-config-ssh-ssh-config",
    ]
)
@pytest.mark.feature("ssh")
def test_ssh_client_config_exists(file: File):
    """Test that SSH client configuration exists"""
    assert file.exists("/etc/ssh/ssh_config"), "SSH client configuration should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-ssh-config-ssh-ssh-config",
    ]
)
@pytest.mark.feature("ssh")
def test_ssh_client_config_content(parse_file: ParseFile):
    """Test that SSH client configuration exists"""
    lines = parse_file.lines("/etc/ssh/ssh_config")
    lines_expected = [
        "Host *",
        "Protocol 2",
        "ForwardAgent no",
        "ForwardX11 no",
        "HostbasedAuthentication no",
        "StrictHostKeyChecking no",
        "Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr",
        "MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-512,hmac-sha2-256,umac-128@openssh.com",
        "KexAlgorithms curve25519-sha256@libssh.org,ecdh-sha2-nistp521,ecdh-sha2-nistp384,ecdh-sha2-nistp256,diffie-hellman-group-exchange-sha256",
        "Tunnel no",
        "ServerAliveInterval 420",
    ]
    assert (
        lines == lines_expected
    ), "SSH client configuration should contain the expected content"


@pytest.mark.setting_ids(
    [
        "GL-SET-ssh-config-sudoers-wheel-permissions",
    ]
)
@pytest.mark.feature("ssh")
def test_ssh_sudoers_wheel_permissions(file: File):
    """Test that sudoers wheel file has correct permissions"""
    assert file.has_mode(
        "/etc/sudoers.d/wheel", "0440"
    ), "Sudoers wheel file should have 0440 permissions"


@pytest.mark.setting_ids(
    [
        "GL-SET-ssh-service-sshguard-nftables-configure",
    ]
)
@pytest.mark.feature(
    "ssh and firewall", reason="nftables package is installed on firewall"
)
def test_ssh_sshguard_nftables_configured(parse_file: ParseFile):
    """Test that sshguard nftables is configured"""

    content = parse_file.lines("/etc/systemd/system/sshguard.service.d/override.conf")
    assert (
        "Requires=nftables.service" in content
    ), "SSHGuard systemd service override configuration should require nftables.service"
    assert (
        "PartOf=nftables.service" in content
    ), "SSHGuard systemd service override configuration should part of nftables.service"
    assert (
        "WantedBy=multi-user.target nftables.service" in content
    ), "SSHGuard systemd service override configuration should want to be started by multi-user.target and nftables.service"


@pytest.mark.setting_ids(
    [
        "GL-SET-ssh-service-sshguard-iptables-configure",
    ]
)
@pytest.mark.feature("ssh and server", reason="iptables package is installed on server")
def test_ssh_sshguard_iptables_configured(parse_file: ParseFile):
    """Test that sshguard iptables is configured"""

    content = parse_file.lines("/etc/systemd/system/sshguard.service.d/override.conf")
    assert (
        "ExecStartPre=-/sbin/iptables -N sshguard" in content
    ), "SSHGuard systemd service override configuration should have ExecStartPre=-/sbin/iptables -N sshguard"
    assert (
        "ExecStartPre=-/sbin/ip6tables -N sshguard" in content
    ), "SSHGuard systemd service override configuration should have ExecStartPre=-/sbin/ip6tables -N sshguard"
    assert (
        "ExecStopPost=-/sbin/iptables -X sshguard" in content
    ), "SSHGuard systemd service override configuration should have ExecStopPost=-/sbin/iptables -X sshguard"
    assert (
        "ExecStopPost=-/sbin/ip6tables -X sshguard" in content
    ), "SSHGuard systemd service override configuration should have ExecStopPost=-/sbin/ip6tables -X sshguard"


@pytest.mark.setting_ids(
    [
        "GL-SET-ssh-service-sshguard-iptables-configure",
    ]
)
@pytest.mark.feature("ssh and server", reason="iptables package is installed on server")
def test_ssh_sshguard_iptables_backend_configured(parse_file: ParseFile):
    """Test that sshguard iptables backend is configured"""

    content = parse_file.parse("/etc/sshguard/sshguard.conf", format="keyval")
    assert (
        content["BACKEND"] == "/usr/libexec/sshguard/sshg-fw-iptables"
    ), "SSHGuard configuration should reference iptables backend"
