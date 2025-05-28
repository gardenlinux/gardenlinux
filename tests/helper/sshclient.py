""" Client to manage connections and run commands via ssh on a remote host."""
import logging
import time
import pytest
import hashlib
import base64
import subprocess
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519, ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from os import environ, path, makedirs
from typing import Optional

from paramiko import SSHClient, AutoAddPolicy, RSAKey, ECDSAKey, Ed25519Key, PKey
from paramiko.ssh_exception import NoValidConnectionsError, AuthenticationException, SSHException

from scp import SCPClient, SCPException

logger = logging.getLogger(__name__)

class RemoteClient:
    """Client to interact with a remote host via SSH & SCP."""

    @staticmethod
    def generate_key_pair(
        filename: str = None,
        key_type: str = "ed25519",  # Default to ed25519
        bits: int = 2048,
        passphrase: str = None,
    ):
        """Generate a key pair for SSH authentication.
        
        Args:
            filename: Path where the private key should be saved
            key_type: Type of key to generate ('rsa', 'ed25519', or 'ecdsa')
            bits: Key size in bits (for RSA keys)
            passphrase: Optional passphrase for the private key
            
        Returns:
            str: The key fingerprint
        """
        if filename is None:
            filename = path.expanduser("~/.ssh/id_ed25519_gardenlinux")

        # Create ~/.ssh directory if it doesn't exist
        ssh_dir = path.dirname(filename)
        makedirs(ssh_dir, mode=0o700, exist_ok=True)
        logger.info(f"Ensuring SSH directory exists: {ssh_dir}")

        if not path.exists(filename):
            if key_type == "ed25519":
                private_key = ed25519.Ed25519PrivateKey.generate()
            elif key_type == "rsa":
                private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=bits,
                    backend=default_backend()
                )
            elif key_type == "ecdsa":
                private_key = ec.generate_private_key(
                    curve=ec.SECP256R1(),
                    backend=default_backend()
                )
            else:
                raise ValueError(f"Unsupported key type: {key_type}")

            # Serialize private key in OpenSSH format
            private_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.OpenSSH,
                encryption_algorithm=serialization.NoEncryption() if passphrase is None
                else serialization.BestAvailableEncryption(passphrase.encode())
            )

            # Get public key and serialize in OpenSSH format
            public_key = private_key.public_key()
            public_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.OpenSSH,
                format=serialization.PublicFormat.OpenSSH
            )

            # Save private key
            with open(filename, 'wb') as f:
                f.write(private_bytes)
            
            # Save public key
            with open(f"{filename}.pub", 'wb') as f:
                f.write(public_bytes)

            # Set correct permissions
            subprocess.run(['chmod', '600', filename])
            subprocess.run(['chmod', '644', f"{filename}.pub"])

            # Calculate fingerprint
            key_hash = hashlib.sha256(public_bytes).digest()
            fingerprint = base64.b64encode(key_hash).decode('utf-8')
            
            logger.info(f"Generated {key_type.upper()} key pair at {filename}")
            logger.debug(f"Key fingerprint: SHA256:{fingerprint}")
            
            return f"SHA256:{fingerprint}"
        else:
            logger.info(f"Using existing key at {filename}")
            return filename


    class File:
        """
            This File class is designed to allow using the RemoteClient as a Context Manager. By
            now, we're using execute to invoke utilzing the exec_command method. With this subclass
            we add a way to utizing python’s built-in python:file to return a file object.

            It can be used: 
                with client.open("/etc/sudoers") as file:
                    for line in file.readlines():
                    ...

        """
        def __init__(self, client, file):
            self.file = file
            self.client = client
            self.sftp = self.client.open_sftp()
            self.file_descriptor = None

        def __enter__(self):
            self.file_descriptor = self.sftp.file(self.file, 'r')
            return self.file_descriptor

        def __exit__(self, exc_type, exc_value, traceback):
           self.file_descriptor.close()

    def open(self, file):
        return self.File(self.client, file)


    def ls(self, path):
        listdir(self, path)


    def listdir(self, path):
        fp = self.File(self.client, path)
        return fp.sftp.listdir(path=path)


    def _determine_key_type(self):
        """Determine the key type by reading the key file."""
        with open(self.ssh_key_filepath, "rb") as keyfile:
            key_data = keyfile.read()
            
            # First check for OpenSSH format keys
            if b"BEGIN OPENSSH PRIVATE KEY" in key_data:
                # Need to parse the actual key type from the OpenSSH format
                if b"ssh-rsa" in key_data:
                    return "rsa"
                elif b"ssh-ed25519" in key_data:
                    return "ed25519"
                elif b"ecdsa-sha2" in key_data:
                    return "ecdsa"
                else:
                    # If we can't determine the type but it's OpenSSH format, assume RSA
                    logger.warning(f"Could not determine specific key type for OpenSSH key at {self.ssh_key_filepath}, assuming RSA")
                    return "rsa"
                
            # Check for traditional PEM format keys
            elif b"BEGIN RSA PRIVATE KEY" in key_data:
                return "rsa"
            elif b"BEGIN EC PRIVATE KEY" in key_data:
                return "ecdsa"
            
            # If we get here, we couldn't identify the key type
            raise ValueError(f"Could not determine key type for {self.ssh_key_filepath}. " +
                            "File may be corrupted or in an unsupported format.")


    def __init__(
        self,
        host,
        sshconfig,
        port="22",
        sudo=False,
        ssh_connect_timeout: int=60,
        ssh_max_retries: Optional[int]=None,
        ssh_retry_wait_seconds: Optional[int]=None,
        wait_for_systemd: Optional[bool]=False,
    ) -> None:
        self.host = host
        self.port = port
        self.sshconfig = sshconfig  # Store the SSH config
        self._default_to_sudo = sudo
        self.conn = None
        self._client = None
        self._scp = None

        # For this test environment, it is ok to ignore host key checking
        self._ignore_host_keys = sshconfig.get("ignore_host_keys", True)

        if ssh_max_retries is None and "GL_REMOTE_CLIENT_SSH_MAX_RETRIES" in environ:
            try: ssh_max_retries = int(environ["GL_REMOTE_CLIENT_SSH_MAX_RETRIES"])
            except ValueError: pass
        if ssh_max_retries is None:
            ssh_max_retries = 20

        if ssh_retry_wait_seconds is None and "GL_REMOTE_CLIENT_SSH_RETRY_WAIT_SECONDS" in environ:
            try: ssh_retry_wait_seconds = int(environ["GL_REMOTE_CLIENT_SSH_RETRY_WAIT_SECONDS"])
            except ValueError: pass
        if ssh_retry_wait_seconds is None:
            ssh_retry_wait_seconds = 15

        self._ssh_connect_timeout = ssh_connect_timeout
        self._ssh_retry_wait_seconds = ssh_retry_wait_seconds
        self._ssh_max_retries = ssh_max_retries
        self._ssh_retry_count = 0

        self.passphrase = None
        self.remote_path = "/"

        if "passphrase" in sshconfig:
            self.passphrase = sshconfig["passphrase"]
        if "remote_path" in sshconfig:
            self.remote_path = sshconfig["remote_path"]

        if not "user" in sshconfig:
            raise Exception('user not given in ssh config')
        if not 'ssh_key_filepath' in sshconfig:
            raise Exception('ssh_key_filepath not in sshconfig')
        self.user = sshconfig['user']
        self.ssh_key_filepath = path.expanduser(sshconfig['ssh_key_filepath'])
        self.ssh_key_private = self.__get_ssh_key()

        self.wait_for_systemd = wait_for_systemd

    @property
    def client(self):
        if self._client is None:
            """Open connection to remote host."""
            self._client = SSHClient()
            
            if self._ignore_host_keys:
                # For test environments, ignore host keys
                self._client.set_missing_host_key_policy(AutoAddPolicy())
                # Also remove any existing host key to prevent mismatches
                known_hosts = path.expanduser('~/.ssh/known_hosts')
                if path.exists(known_hosts):
                    try:
                        subprocess.run(["ssh-keygen", "-R", f"[{self.host}]:{self.port}"], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
                    except Exception as e:
                        logger.warning(f"Failed to remove host key: {e}")
            else:
                # For production environments, use system host keys
                self._client.load_system_host_keys()
                self._client.set_missing_host_key_policy(AutoAddPolicy())

            logger.info(f"Attempting to establish an SSH connection to {self.host}:{self.port}...")
            self._client_connect(
                hostname=self.host,
                port=self.port,
                username=self.user,
                passphrase=self.passphrase,
                pkey=self.ssh_key_private,
                look_for_keys=True,
                banner_timeout=10,
                auth_timeout=30,
                timeout=self._ssh_connect_timeout,
            )

            # After establishing connection, optionally wait for systemd
            if self.wait_for_systemd:
                logger.info("Waiting for systemd to complete system initialization...")
                exit_status, output, error = self.execute_command(
                    "systemctl is-system-running --wait",
                    timeout=600,  # 10 minute timeout
                    quiet=True
                )
                if exit_status == 0:
                    logger.info("System initialization complete")
                else:
                    logger.warning(f"System initialization status: {output.strip() or error.strip()}")

        return self._client

    @property
    def scp(self):
        if self._scp is None:
            self._scp = SCPClient(self.client.get_transport())

        return self._scp

    def _client_connect(self, *args, **kwargs):
        while self._ssh_retry_count < self._ssh_max_retries:
            try:
                self._client.connect(*args, **kwargs)
                break
            except NoValidConnectionsError:
                logger.warning(f"Unable to connect")
                self._increase_retry_count_and_wait()
            except AuthenticationException as exc:
                auth_banner = self._client.get_transport().get_banner().decode()
                logger.warning(f"Failed to login - {auth_banner=}")
                if "pam_nologin(8)" in auth_banner:
                    # SSH is already accepting connections but PAM refuses to let anyone in ("System is booting up"), have to retry
                    self._increase_retry_count_and_wait()
                else:
                    logger.exception(exc)
                    raise exc
            except Exception as exc:
                logger.exception(exc)
                raise exc

    def __get_ssh_key(self):
        """Fetch locally stored SSH key or generate a new one."""
        # Check if we should generate a new key
        should_generate = self.sshconfig.get("ssh_key_generate", True)
        
        # Generate key if it doesn't exist and generation is enabled
        if not path.exists(self.ssh_key_filepath):
            if should_generate:
                logger.info(f"No SSH key found at {self.ssh_key_filepath}, generating a new key.")
                self.generate_key_pair(filename=self.ssh_key_filepath)
            else:
                raise FileNotFoundError(f"SSH key file not found: {self.ssh_key_filepath} and key generation is disabled")

        # Read first line of key file to determine type
        with open(self.ssh_key_filepath, "r") as keyfile:
            first_line = keyfile.readline().strip()
            keyfile.seek(0)  # Reset file pointer for key loading
            
            if "OPENSSH PRIVATE KEY" in first_line:
                # For OpenSSH format, try each key type
                try:
                    return Ed25519Key.from_private_key(keyfile, password=self.passphrase)
                except Exception:
                    keyfile.seek(0)
                    try:
                        return RSAKey.from_private_key(keyfile, password=self.passphrase)
                    except Exception:
                        keyfile.seek(0)
                        try:
                            return ECDSAKey.from_private_key(keyfile, password=self.passphrase)
                        except Exception as e:
                            raise ValueError(f"Could not load OpenSSH key: {str(e)}")
            elif "RSA PRIVATE KEY" in first_line:
                return RSAKey.from_private_key(keyfile, password=self.passphrase)
            elif "EC PRIVATE KEY" in first_line:
                return ECDSAKey.from_private_key(keyfile, password=self.passphrase)
            else:
                raise ValueError(f"Unrecognized key format in {self.ssh_key_filepath}")

    def _increase_retry_count_and_wait(self):
        if self._ssh_retry_count >= self._ssh_max_retries:
            max_timeout = self._ssh_retry_count * self._ssh_retry_wait_seconds
            # FIXME: this should not be pytest.exit() as it will exit immediately without cleanup
            raise SSHException(f"Unable to establish an SSH connection after {max_timeout=} seconds.")

        self._ssh_retry_count += 1
        logger.warning(f"Retrying in {self._ssh_retry_wait_seconds} seconds...")
        time.sleep(self._ssh_retry_wait_seconds)

    def __upload_ssh_key(self):
        try:
            subprocess.run(
                [
                    "ssh-copy-id",
                    "-i",
                    self.ssh_key_filepath,
                    f"{self.user}@{self.host}",
                    ">/dev/null",
                    "2>&1",
                ],
                check=True,
            )
            subprocess.run(
                [
                    "ssh-copy-id",
                    "-i",
                    f"{self.ssh_key_filepath}.pub",
                    f"{self.user}@{self.host}",
                    ">/dev/null",
                    "2>&1",
                ],
                check=True,
            )
            logger.info(f"{self.ssh_key_filepath} uploaded to {self.host}")
        except FileNotFoundError as error:
            logger.exception(error)

    def disconnect(self):
        """Close ssh connection."""
        if self._client is not None:
            self._client.close()
        if self._scp:
            self._scp.close()

        self._client = None
        self._scp = None

        logger.info(f"disconnected from {self.host=}")

    def wait_ssh(self, counter_max=100, sleep=5):
        """ Wait for defined SSH port to become ready in test environment """
        port = self.port
        ip = self.host
        logger.info("Waiting for SSHD in test env to become ready on tcp/{port} and {ip}".format(
          port=port, ip=ip))
        cmd = "ssh-keyscan -p {port} {ip}".format(
          port=port, ip=ip)

        counter = 0
        err_msg = "Too many retries. Something went wrong."
        rc = 1
        while rc != 0:
            if counter == counter_max:
                logger.error(err_msg)
                # Do not only raise log msg; let it fail
                pytest.exit(err_msg, 1)
            p = subprocess.run(
                [cmd],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            rc = p.returncode
            counter = counter + 1
            logger.info(str(p.returncode) + " Waiting... Run: {counter}/{max} ".format(
                counter=counter, max=counter_max))
            time.sleep(sleep)
        logger.info("SSH ready in test env.")

    def bulk_upload(self, files):
        """
        Upload multiple files to a remote directory.

        :param files: List of strings representing file paths to local files.
        """
        uploads = [self.__upload_single_file(file) for file in files]
        logger.info(
            f"Finished uploading {len(uploads)} files to {self.remote_path} on {self.host}"
        )

    def __upload_single_file(self, file):
        """Upload a single file to a remote directory."""
        try:
            self.scp.put(file, recursive=True, remote_path=self.remote_path)
        except SCPException as error:
            logger.exception(error)
            raise error
        finally:
            logger.info(f"Uploaded {file} to {self.remote_path}")

    def download_file(self, file):
        """Download file from remote host."""
        self.scp.get(file)

    def execute_command(
        self,
        command: str,
        timeout: int = 30,
        quiet: bool = False,
        disable_sudo: bool = False,
        force_sudo: bool = False
    ) -> tuple[int, str, str]:
        """
        Execute commands on remote host

        :param command: unix command as string.
        :param timeout: timeout in seconds.

        :returns: the command's exit status, standard and error output
        """
        if not quiet:
            logger.info(f"$ {command.rstrip()}")
        if (self._default_to_sudo and not disable_sudo) or force_sudo:
            command = f'sudo /bin/bash -c "{command.replace('"', '\"')}"'

        _, stdout, stderr = self.client.exec_command(command=command, timeout=timeout)
        exit_status = stdout.channel.recv_exit_status()
        if not quiet:
            logger.info(f"{exit_status=}")

        output, error = stdout.read().decode(), stderr.read().decode()
        if not quiet:
            if len(error) > 0:
                logger.info(error)
            else:
                logger.info(output)

        return exit_status, output, error
