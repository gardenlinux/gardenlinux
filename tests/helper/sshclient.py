""" Client to manage connections and run commands via ssh on a remote host."""
import logging
import time
import pytest
import subprocess
from binascii import hexlify
from os import environ, path
from typing import Optional

from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.ssh_exception import (
    NoValidConnectionsError,
    AuthenticationException,
    SSHException
)

from scp import SCPClient, SCPException

logger = logging.getLogger(__name__)


class RemoteClient:
    """Client to interact with a remote host via SSH & SCP."""

    @classmethod
    def generate_key_pair(
        cls,
        filename: str = None,
        fileobj = None,
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
        if filename and path.exists(filename) and path.getsize(filename) > 0:
            pub = RSAKey(filename=filename, password=passphrase)
            logger.info("SSH key already exists, skipping generating SSH key")
        else:
            priv = RSAKey.generate(bits=bits)
            if filename:
                priv.write_private_key_file(filename, password=passphrase)
            elif fileobj:
                priv.write_private_key(file_obj=fileobj, password=passphrase)
            pub = RSAKey(filename=filename, password=passphrase)
            logger.info(f"generated RSA key pair: {filename}")
            with open(f"{filename}.pub", "w") as f:
                f.write(f"{pub.get_name()} {pub.get_base64()}")
                if comment:
                    f.write(f" {comment}")
        hash = hexlify(pub.get_fingerprint()).decode(encoding="utf-8")
        fingerprint = ":".join([hash[i : 2 + i] for i in range(0, len(hash), 2)])
        logger.info(f"fingerprint: {bits} {fingerprint} {filename}.pub (RSA)")
        return fingerprint

    def __init__(
        self,
        host,
        sshconfig,
        port="22",
        sudo=False,
        ssh_connect_timeout: int=60,
        ssh_max_retries: Optional[int]=None,
        ssh_retry_wait_seconds: Optional[int]=None,
    ) -> None:
        self.host = host
        self.port = port
        self.sudo = sudo
        self.conn = None
        self._client = None
        self._scp = None

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

        if 'passphrase' in sshconfig:
            self.passphrase = sshconfig['passphrase']
        if 'remote_path' in sshconfig:
            self.remote_path = sshconfig['remote_path']

        if not "user" in sshconfig:
            raise Exception('user not given in ssh config')
        if not 'ssh_key_filepath' in sshconfig:
            raise Exception('ssh_key_filepath not in sshconfig')
        self.user = sshconfig['user']
        self.ssh_key_filepath = path.expanduser(sshconfig['ssh_key_filepath'])

    @property
    def client(self):
        if self._client is None:
            """Open connection to remote host."""
            self._client = SSHClient()
            self._client.load_system_host_keys()
            self._client.set_missing_host_key_policy(AutoAddPolicy())

            private_key = None
            with open(self.ssh_key_filepath, "r") as keyfile:
                private_key = RSAKey.from_private_key(keyfile, password=self.passphrase)

            logger.info(f"Attempting to establish an SSH connection to {self.host}:{self.port}...")
            self._client_connect(
                hostname=self.host,
                port=self.port,
                username=self.user,
                passphrase=self.passphrase,
                pkey=private_key,
                look_for_keys=True,
                banner_timeout=10,
                auth_timeout=30,
                timeout=self._ssh_connect_timeout,
            )

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
        """Fetch locally stored SSH key."""
        try:
            self.ssh_key = RSAKey.from_private_key_file(self.ssh_key_filepath)
            logger.info(f"Found SSH key at self {self.ssh_key_filepath}")
        except SSHException as error:
            logger.exception(error)
        return self.ssh_key

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
        disable_sudo: bool = False
    ) -> tuple[int, str, str]:
        """
        Execute commands on remote host

        :param command: unix command as string.
        :param timeout: timeout in seconds.

        :returns: the command's exit status, standard and error output
        """
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
