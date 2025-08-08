import pytest
from plugins.shell import ShellRunner

required_sshd_config = [
    # Supported HostKey algorithms.
    "HostKey /etc/ssh/ssh_host_ed25519_key",
    "HostKey /etc/ssh/ssh_host_rsa_key",
    # "HostKey /etc/ssh/ssh_host_ecdsa_key",
    # "KexAlgorithms sntrup761x25519-sha512,sntrup761x25519-sha512@openssh.com,mlkem768x25519-sha256,curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521",
    # "Ciphers chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com",
    # "MACs umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1",
    # Password based logins are disabled - only public key based logins are allowed.
    "AuthenticationMethods publickey",
    # LogLevel VERBOSE logs user's key fingerprint on login. Needed to have a clear audit track of which key was using to log in.
    "LogLevel VERBOSE",
    # Log sftp level file access (read/write/etc.) that would not be easily logged otherwise - be aware that the path has to be adapted to the Distribution installed.
    "Subsystem sftp /usr/lib/openssh/sftp-server -f AUTHPRIV -l INFO",
    # Root login is not allowed for auditing reasons. This is because it's difficult to track which process belongs to which root user:
    #
    # On Linux, user sessions are tracking using a kernel-side session id, however, this session id is not recorded by OpenSSH.
    # Additionally, only tools such as systemd and auditd record the process session id.
    # On other OSes, the user session id is not necessarily recorded at all kernel-side.
    # Using regular users in combination with /bin/su or /usr/bin/sudo ensure a clear audit track.
    "PermitRootLogin No",
    # Use kernel sandbox mechanisms where possible in unprivileged processes
    # Systrace on OpenBSD, Seccomp on Linux, seatbelt on MacOSX/Darwin, rlimit elsewhere.
    # "UsePrivilegeSeparation sandbox",
    # Disable Tunneling and Forwarding
    # AllowTcpForwarding no # required for Gardener
    "X11Forwarding no",
    # use PAM
    "UsePAM yes",
]

def trim_and_lower(s):
    return str.lower(str.lstrip(s))


def _create_list_of_tuples(input):
    """Takes a multiline string and returns a list containing every line 
    as a tuple. The 1st value of the tuple is the ssh option, the 2nd is
    value"""
    out = []
    for line in input.lower().splitlines():
        l = line.split(' ', 1)
        option = l[0]
        value = l[1]
        normalized_value = _normalize_value(value)
        out.append((option, normalized_value))
    return out

def _normalize_value(string):
    """Convert a given string.
    The string will be returned as a set. If the element contains a comma
    separated string, it will be split into a list first."""
    normalized = string.split(" ")
    if len(normalized) == 1 and "," in normalized[0]:
        value_as_set = set(normalized[0].split(','))
    else:
        value_as_set = set(normalized)
    return value_as_set


@pytest.mark.feature("ssh")
@pytest.mark.parametrize("sshd_config_item", required_sshd_config)
def test_sshd_has_required_config(sshd_config_item: str, shell: ShellRunner):

    shell('ssh-keygen -A')
    shell('systemctl daemon-reload')

    result = shell(
        "/usr/sbin/sshd -T", capture_output=True, ignore_exit_code=True
    )
    assert result.returncode == 0, f"Expected return code 0, got {result.returncode}"

    sshd_config = _create_list_of_tuples(result.stdout)

    expected = _create_list_of_tuples(sshd_config_item)


    assert all(option in sshd_config for option in expected), \
            f"{expected} not found in sshd_config"


    # found = any(trim_and_lower(sshd_config_item) in trim_and_lower(line) for line in config_content)
    # assert found, f"Expected {sshd_config_item} in sshd config, but did not find it"


# @pytest.mark.feature("ssh")
# def test_sshd_parse_config(shell: ShellRunner):
#     result = shell(
#         "sudo -u root /usr/sbin/sshd -T", capture_output=True, ignore_exit_code=True
#     )
#     assert result.returncode == 0
