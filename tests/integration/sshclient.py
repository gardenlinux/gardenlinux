""" Client to manage connections and run commands via ssh on a remote host."""
import logging
import subprocess
from os import path
from binascii import hexlify

from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException
from paramiko.py3compat import u
from scp import SCPClient, SCPException

logger = logging.getLogger(__name__)


class RemoteClient:
    """Client to interact with a remote host via SSH & SCP."""

    @classmethod
    def generate_key_pair(
        cls,
        filename: str,
        bits: int = 2048,
        passphrase: str = None,
        comment: str = None,
    ):
        """Generate RSA key pair.

        :param filename: name of private key file
        :param bits: length of RSA key
        :param passphrase: passphrase of the RSA key
        :param comment: comment for RSA key
        """
        priv = RSAKey.generate(bits=bits)
        priv.write_private_key_file(filename, password=passphrase)
        pub = RSAKey(filename=filename, password=passphrase)
        logger.info(f"generated RSA key pair: {filename}")
        with open(f"{filename}.pub", "w") as f:
            f.write(f"{pub.get_name()} {pub.get_base64()}")
            if comment:
                f.write(f" {comment}")
        hash = u(hexlify(pub.get_fingerprint()))
        fingerprint = ":".join([hash[i : 2 + i] for i in range(0, len(hash), 2)])
        logger.info(f"fingerprint: {bits} {fingerprint} {filename}.pub (RSA)")
        return fingerprint

    def __init__(
        self,
        host: str,
        user: str,
        ssh_key_filepath: str,
        passphrase: str,
        remote_path: str,
    ) -> None:
        self.host = host
        self.user = user
        self.ssh_key_filepath = path.expanduser(ssh_key_filepath)
        self.passphrase = passphrase
        self.remote_path = remote_path
        self.client = None
        self.scp = None
        self.conn = None

    def __get_ssh_key(self):
        """Fetch locally stored SSH key."""
        try:
            self.ssh_key = RSAKey.from_private_key_file(self.ssh_key_filepath)
            logger.info(f"Found SSH key at self {self.ssh_key_filepath}")
        except SSHException as error:
            logger.exception(error)
        return self.ssh_key

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
        try:
            self.client = SSHClient()
            self.client.load_system_host_keys()
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            pk = None
            with open(self.ssh_key_filepath) as keyfile:
                pk = RSAKey.from_private_key(keyfile, password=self.passphrase)

            if pk is None:
                logger.error(f"private key {self.ssh_key_filepath} not found")
                exit(1)
            self.client.connect(
                hostname=self.host,
                username=self.user,
                passphrase=self.passphrase,
                pkey=pk,
                look_for_keys=True,
                auth_timeout=30,
                timeout=60,
            )
            self.scp = SCPClient(self.client.get_transport())
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
        logger.info("disconnected from {self.host=}")

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

    def execute_command(self, command: str, timeout: int = 30) -> (int, str, str):
        """
        Execute commands on remote host

        :param command: unix command as string.
        :param timeout: timeout in seconds.

        :returns: the command's exit status, standard and error output
        """
        if self.client is None:
            self.client = self.__connect()

        logger.info(f"$ {command.rstrip()}")

        _, stdout, stderr = self.client.exec_command(command=command, timeout=timeout)
        exit_status = stdout.channel.recv_exit_status()
        logger.info(f"{exit_status=}")

        output, error = stdout.read().decode(), stderr.read().decode()
        if len(error) > 0:
            logger.info(error)
        else:
            logger.info(output)

        return exit_status, output, error
