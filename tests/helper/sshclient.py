""" Client to manage connections and run commands via ssh on a remote host."""
import logging
import time
import pytest
import subprocess
from os import path
from binascii import hexlify

from paramiko import SSHClient, AutoAddPolicy, RSAKey
from paramiko.auth_handler import AuthenticationException, SSHException
from paramiko.ssh_exception import NoValidConnectionsError
from paramiko.util import u
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
        hash = u(hexlify(pub.get_fingerprint()))
        fingerprint = ":".join([hash[i : 2 + i] for i in range(0, len(hash), 2)])
        logger.info(f"fingerprint: {bits} {fingerprint} {filename}.pub (RSA)")
        return fingerprint

    def __init__(
        self,
        host,
        sshconfig,
        port="22",
        sudo=False
    ) -> None:
        self.host = host
        self.port = port
        self.sudo = sudo
        self.client = None
        self.scp = None
        self.conn = None

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


            max_errors = 5
            errors = 0
            while errors < max_errors:
                try:
                    self.client.connect(
                        hostname=self.host,
                        port=self.port,
                        username=self.user,
                        passphrase=self.passphrase,
                        pkey=pk,
                        look_for_keys=True,
                        auth_timeout=30,
                        timeout=60,
                    )
                    self.scp = SCPClient(self.client.get_transport())
                    break
                except NoValidConnectionsError as e:
                    logger.exception("Unable to connect")
                    errors = errors + 1
                    if errors == 5:
                        raise Exception("Too many connection failures. Giving up.")
                    time.sleep(5)
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
