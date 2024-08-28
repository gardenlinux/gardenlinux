""" Client to manage connections and run commands via ssh on a remote host."""
import logging
import time
import pytest
import hashlib
import base64
import subprocess
from os import path
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519, ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from paramiko import SSHClient, AutoAddPolicy, RSAKey, ECDSAKey, Ed25519Key
from paramiko.ssh_exception import NoValidConnectionsError, AuthenticationException, SSHException
from scp import SCPClient, SCPException

logger = logging.getLogger(__name__)

class RemoteClient:
    """Client to interact with a remote host via SSH & SCP."""

    @classmethod
    def generate_key_pair(
        cls,
        filename: str = None,
        key_type: str = "ed25519",  # Default to ed25519
        bits: int = 2048,
        passphrase: str = None,
    ):
        """Generate key pair (RSA, ECDSA, or Ed25519) compatible with OpenSSH.

        :param filename: name of private key file
        :param key_type: type of key (rsa, ecdsa, ed25519)
        :param bits: length of RSA or ECDSA key (ignored for Ed25519)
        :param passphrase: passphrase of the key
        """
        if key_type == "rsa":
            private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=bits, backend=default_backend()
            )
        elif key_type == "ecdsa":
            private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        elif key_type == "ed25519":
            private_key = ed25519.Ed25519PrivateKey.generate()
        else:
            raise ValueError("Unsupported key type. Use 'rsa', 'ecdsa', or 'ed25519'.")

        # Serialize private key
        if key_type == "ed25519":
            # Use OpenSSH format for Ed25519 keys to ensure compatibility with OpenSSH
            private_key_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.OpenSSH,
                encryption_algorithm=serialization.BestAvailableEncryption(passphrase.encode()) if passphrase else serialization.NoEncryption(),
            )
        else:
            # Use PEM format for RSA and ECDSA keys
            private_key_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.BestAvailableEncryption(passphrase.encode()) if passphrase else serialization.NoEncryption(),
            )

        # Write private key to file
        with open(filename, "wb") as f:
            f.write(private_key_bytes)

        # Write public key to file
        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH,
        )
        with open(f"{filename}.pub", "wb") as f:
            f.write(public_key_bytes)

        # Calculate fingerprint (SHA256 of the public key)
        digest = hashlib.sha256(public_key_bytes).digest()
        fingerprint = base64.b64encode(digest).decode('utf-8')

        logger.info(f"Generated {key_type.upper()} key pair: {filename}")
        logger.info(f"Fingerprint: {fingerprint}")

        return fingerprint        


    def _determine_key_type(self):
        """Determine the key type by reading the key file."""
        with open(self.ssh_key_filepath, "rb") as keyfile:
            key_data = keyfile.read()
            if b"BEGIN RSA PRIVATE KEY" in key_data:
                return "rsa"
            elif b"BEGIN EC PRIVATE KEY" in key_data:
                return "ecdsa"
            elif b"BEGIN OPENSSH PRIVATE KEY" in key_data:  # Ed25519 keys use this header
                return "ed25519"
            else:
                raise ValueError("Unsupported or unknown key type")


    def __init__(
        self,
        host,
        sshconfig,
        port="22",
        sudo=False,
        ssh_connect_timeout: int = 60,
        ssh_max_retries: int = 20,
        ssh_retry_timeout_seconds: int = 15,
    ) -> None:
        self.host = host
        self.port = port
        self.sudo = sudo
        self.ssh_connect_timeout = ssh_connect_timeout
        self.ssh_max_retries = ssh_max_retries
        self.ssh_retry_timeout_seconds = ssh_retry_timeout_seconds
        self.client = None
        self.scp = None
        self.retry_count = 0

        self.passphrase = None
        self.remote_path = "/"

        if "passphrase" in sshconfig:
            self.passphrase = sshconfig["passphrase"]
        if "remote_path" in sshconfig:
            self.remote_path = sshconfig["remote_path"]

        if "user" not in sshconfig:
            raise Exception("user not given in ssh config")
        if "ssh_key_filepath" not in sshconfig:
            raise Exception("ssh_key_filepath not in sshconfig")

        self.user = sshconfig["user"]
        self.ssh_key_filepath = path.expanduser(sshconfig["ssh_key_filepath"])

        # Check if the SSH key file exists
        if not path.exists(self.ssh_key_filepath):
            # If file does not exist, generate a new key pair with default to Ed25519
            logger.info(
                f"No SSH key found at {self.ssh_key_filepath}, generating a new key."
            )
            self.generate_key_pair(filename=self.ssh_key_filepath)
            self.key_type = self._determine_key_type()
        else:
            # If file exists, determine the key type
            self.key_type = self._determine_key_type()
            logger.info(f"Found {self.key_type.upper()} key at {self.ssh_key_filepath}")
        self.ssh_key_file_private = self.ssh_key_filepath
        self.ssh_key_file_public = self.ssh_key_filepath + ".pub"
        with open(self.ssh_key_filepath, "r") as keyfile:
            if self.key_type == "rsa":
                self.ssh_key_private = RSAKey.from_private_key(keyfile, password=self.passphrase)
            elif self.key_type == "ecdsa":
                self.ssh_key_private = ECDSAKey.from_private_key(keyfile, password=self.passphrase)
            elif self.key_type == "ed25519":
                self.ssh_key_private = Ed25519Key.from_private_key(keyfile, password=self.passphrase)


    def _increase_retry_count_and_wait(self):
        if self.retry_count >= self.ssh_max_retries:
            max_timeout = self.retry_count * self.ssh_retry_timeout_seconds
            # FIXME: this should not be pytest.exit() as it will exit immediately without cleanup
            pytest.exit(f"Unable to establish an SSH connection after {max_timeout=} seconds. Aborting all tests.", returncode=5) 
        self.retry_count += 1
        logger.warning(f"Retrying in {self.ssh_retry_timeout_seconds} seconds...")
        time.sleep(self.ssh_retry_timeout_seconds)


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


    def __connect(self):
        """Open connection to remote host."""
        self.client = SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(AutoAddPolicy())

        try:
            logger.info(f"Attempting to establish an SSH connection to {self.host}:{self.port}...")
            while self.retry_count < self.ssh_max_retries:
                try:
                    self.client.connect(
                        hostname=self.host,
                        port=self.port,
                        username=self.user,
                        passphrase=self.passphrase,
                        pkey=self.ssh_key_private,
                        look_for_keys=True,
                        auth_timeout=30,
                        timeout=self.ssh_connect_timeout,
                    )
                    self.scp = SCPClient(self.client.get_transport())
                    break
                except NoValidConnectionsError as e:
                    logger.warning(f"Unable to connect")
                    self._increase_retry_count_and_wait()
                except AuthenticationException as e:
                    auth_banner = self.client.get_transport().get_banner().decode()
                    logger.warning(f"Failed to login - {auth_banner=}")
                    if "pam_nologin(8)" in auth_banner:
                        # SSH is already accepting connections but PAM refuses to let anyone in ("System is booting up"), have to retry
                        self._increase_retry_count_and_wait()
                    else:
                        raise e
        except AuthenticationException as error:
            logger.exception("Authentication failed")
            raise error
        except SSHException as error:
            logger.exception("SSH exception")
            raise error
        except Exception as error:
            logging.exception("unexpected error")
            raise error
        finally:
            return self.client


    def disconnect(self):
        """Close ssh connection."""
        if self.client:
            self.client.close()
        if self.scp:
            self.scp.close()
        self.client = None
        self.scp = None
        logger.info(f"disconnected from {self.host=}")

    def wait_ssh(self, counter_max=20, sleep=5):
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
        if self.client is None:
            self.client = self.__connect()
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
        if self.conn is None:
            self.conn = self.__connect()
        self.scp.get(file)

    def execute_command(
        self,
        command: str,
        timeout: int = 30,
        quiet: bool = False,
        disable_sudo: bool = False
    ) -> tuple[int, str, str]:
        """
        Execute commands on remote host

        :param command: unix command as string.
        :param timeout: timeout in seconds.

        :returns: the command's exit status, standard and error output
        """
        if self.client is None:
            self.client = self.__connect()
        if not quiet:
            logger.info(f"$ {command.rstrip()}")
        if self.sudo and not disable_sudo:
            command = f"sudo {command}"

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
