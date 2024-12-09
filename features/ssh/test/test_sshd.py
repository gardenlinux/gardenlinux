from helper.tests.sshd import sshd
import pytest

@pytest.mark.security_id(322)
@pytest.mark.parametrize(
    "expected",
    [
        # Supported HostKey algorithms.
        "HostKey /etc/ssh/ssh_host_ed25519_key",
        "HostKey /etc/ssh/ssh_host_rsa_key",
        #"HostKey /etc/ssh/ssh_host_ecdsa_key",
        "KexAlgorithms sntrup761x25519-sha512,sntrup761x25519-sha512@openssh.com,mlkem768x25519-sha256,curve25519-sha256,curve25519-sha256@libssh.org,ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,diffie-hellman-group14-sha256",

        "Ciphers chacha20-poly1305@openssh.com,aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com",
        
        "MACs umac-64-etm@openssh.com,umac-128-etm@openssh.com,hmac-sha2-256-etm@openssh.com,hmac-sha2-512-etm@openssh.com,hmac-sha1-etm@openssh.com,umac-64@openssh.com,umac-128@openssh.com,hmac-sha2-256,hmac-sha2-512,hmac-sha1",
        
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
        #"UsePrivilegeSeparation sandbox",
        
        # Disable Tunneling and Forwarding
        # AllowTcpForwarding no # required for Gardener
        "X11Forwarding no",
        
        #use PAM
        "UsePAM yes"
    ]
)

def test_sshd(client, expected):
        sshd(client, expected)
