import logging
import json
import time
import os
import subprocess
import threading
import tempfile
import time
import paramiko
import pytest
import sys
import tempfile
import lzma
import tarfile
import shutil
import socket
from contextlib import closing
from novaclient import client
from .sshclient import RemoteClient
from . import util

# Define global logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BIN_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "bin")

class CHROOT:
    """Handle CHROOT flavour"""

    @classmethod
    def fixture(cls, config):

        logger.info("Starting CHROOT integration tests.")

        # We need to validate basic information
        # for 'RemoteClient' object first. Afterwards
        # we can run regular validation
        logger.info("Validation starting...")
        ip = config.get("ip", "127.0.0.1")
        logger.info(f"Using IP {ip} to connect to chroot.")
        port = config.get("port", "2222")
        logger.info(f"Using port tcp/{port} to connect to chroot.")

        chroot = CHROOT(config)
        cls.chroot = chroot

        try:
            ssh = RemoteClient(
                host=ip,
                port=port,
                sshconfig=config["ssh"],
            )
            yield ssh
        finally:
            if ssh is not None:
                ssh.disconnect()
            if chroot is not None:
                chroot.__del__()

    @classmethod
    def instance(cls):
        return cls.chroot


    def __init__(self, config):
        """ Creating self config """
        # Define self.config
        self.config = config
        # Perform basic validation
        self._validate()
        # Unarchive defined tar ball
        tmp_dir = self._unarchive_image()
        # Generate temporary keys for integration testing
        self._generate_ssh_key()
        # Adjust chroot to be able to connect
        self._adjust_chroot(tmp_dir)
        # Start sshd inside the chroot
        self._start_sshd_chroot(tmp_dir)
        # Make sure ssh is up and running to avoid
        # Paramiko error messages
        self._wait_sshd()


    def __del__(self):
        """ Cleanup resources held by this object """
        if "keep_running" in self.config and self.config["keep_running"] == True:
            logger.info("Keeping all resources")


    def _validate(self):
        """ Validate basic settings befor running the tests """
        # Check if tar archive as image path is defined
        if not "image" in self.config:
            logger.error("No path to image archive defined.")
        else:
            logger.info("Path to image archive defined: {path}".format(
              path=self.config["image"]))

        # Check if tar archive as image path  is present
        image_archive = os.path.exists(self.config["image"])
        if image_archive:
            logger.info("Image archive is present: {path}".format(
              path=self.config["image"]))
        else:
            logger.error("Image archive is not present: {path}".format(
              path=self.config["image"]))

        # Check if port is defined
        if not "port" in self.config:
            logger.error("No port for ssh connection defined.")
        else:
            logger.info("Port for ssh connection defined: {port}".format(
              port=self.config["port"]))

        # Check if sshd port can be used
        self._port_val(self.config["ip"], self.config["port"])


    def _unarchive_image(self):
        """ Unarchive image tar ball """
        image = self.config["image"]
        logger.info("Creating tmp_dir")
        tmp_dir = tempfile.mkdtemp(prefix="gl-int-chroot-")
        logger.info("Created tmp_dir in {tmp_dir}".format(
          tmp_dir=tmp_dir))
        logger.info("Unarchiving image {image} to {tmp_dir}".format(
          image=image, tmp_dir=tmp_dir))
        try:
            with lzma.open(self.config["image"]) as f:
                with tarfile.open(fileobj=f) as tar:
                    content = tar.extractall(tmp_dir)
        except IOError:
            logger.error("Could not unarchive image file due to IO Error.")
        except lzma.LZMAError:
            logger.error("LZMA decompression error.")
        except tarfile.ReadError:
            logger.error(("Archive is present but can not be handled by tar."+
                          "Validate that your tar archive is not corrupt."))
        except tarfile.CompressionError:
            logger.error("Used compression is not supported.")
        except tarfile.HeaderError:
            logger.error("Malformed tar header information.")
        logger.info("Unarchived image {image} to {tmp_dir}".format(
          image=image, tmp_dir=tmp_dir))
        return tmp_dir


    def _generate_ssh_key(self):
        """ Generate new SSH key for integration test """
        logger.info("Generating new SSH key for integration tests.")
        ssh_key_path = self.config["ssh"]["ssh_key_filepath"]
        keyfp = RemoteClient.generate_key_pair(
            filename = ssh_key_path,
        )
        logger.info("SSH key for integration tests generated.")


    def _adjust_chroot(self, tmp_dir):
        """ Adjust chroot to make it usable """
        logger.info("Adjusting chroot environment")
        # Adjust garden-epoch to dev
        chroot_epoch = tmp_dir + "/" + "garden-epoch"
        chroot_epoch_bool = os.path.exists(chroot_epoch)
        if chroot_epoch_bool:
            logger.warning("'garden-epoch' already present. This will be set to 'dev', now.")
        try:
            with open(chroot_epoch, 'w') as f:
                f.write("dev")
            logger.info("Wrote garden-epoch to chroot in {tmp_dir}".format(
              tmp_dir=tmp_dir))
        except IOError:
            logger.error("Could not write garden-epoch to chroot in {tmp_dir}".format(
              tmp_dir=tmp_dir))
        # Generate SSH hostkeys for chroot
        # (this way we do not need to execute this inside the 'chroot'
        #  environment and still support amd64 and arm64 architectures)
        chroot_ssh_dir = tmp_dir + "/etc/ssh/"
        cmd_ssh_keys = []
        cmd_ssh_keys.append('ssh-keygen -q -N "" -t dsa -f {ssh_dir}/ssh_host_dsa_key'.format(
          ssh_dir=chroot_ssh_dir))
        logger.info(cmd_ssh_keys)
        cmd_ssh_keys.append('ssh-keygen -q -N "" -t rsa -b 4096 -f {ssh_dir}/ssh_host_rsa_key'.format(
          ssh_dir=chroot_ssh_dir))
        cmd_ssh_keys.append('ssh-keygen -q -N "" -t ecdsa -f {ssh_dir}/ssh_host_ecdsa_key'.format(
          ssh_dir=chroot_ssh_dir))
        cmd_ssh_keys.append('ssh-keygen -q -N "" -t ed25519 -f {ssh_dir}/ssh_host_ed25519_key'.format(
          ssh_dir=chroot_ssh_dir))
        for i in cmd_ssh_keys:
            logger.info("Running command: {cmd}".format(
              cmd=i))
            p = subprocess.run([i], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            rc = p.returncode
            if rc != 0:
                logger.error("Command failed.")
            else:
                logger.info("Command sucessfully executed.")
        # Generate chroot sshd directory for run/pid
        chroot_sshd_run_dir = tmp_dir + "/run/sshd"
        try:
            os.mkdir(tmp_dir + "/run/sshd")
            logger.info("Created directory: {dir}".format(
              dir=chroot_sshd_run_dir))
        except OSError:
            logger.error("Could not create directory: {dir}".format(
              dir=chroot_sshd_run_dir))
        # Copy dedicated sshd config to chroot
        sshd_config_src_file = "integration/misc/sshd_config_integration_tests"
        chroot_sshd_cfg_dir = tmp_dir + "/etc/ssh/"
        try:
            shutil.copyfile(sshd_config_src_file, chroot_sshd_cfg_dir+"sshd_config_integration_tests")
            logger.info("Copied sshd_config_integration_tests to: {dir}".format(
              dir=chroot_sshd_cfg_dir))
        except OSError:
            logger.error("Could not copy sshd_config_integration_tests to {dir}".format(
              dir=chroot_sshd_cfg_dir))
        # Copy ssh / authorized_keys file for root user
        local_ssh_key_path = self.config["ssh"]["ssh_key_filepath"] + ".pub"
        chroot_root_dir = tmp_dir + "/root/"
        chroot_ssh_authorized_keys = chroot_root_dir + ".ssh/authorized_keys"
        ssh_authorized_keys = "/tmp/authorized_keys"
        self._create_dir(chroot_root_dir+".ssh", 0o600)
        try:
            shutil.copyfile(local_ssh_key_path, chroot_ssh_authorized_keys)
            logger.info("Copied authorized_keys to: {dir}".format(
              dir=chroot_ssh_authorized_keys))
        except OSError:
            logger.error("Could not copy authorized_keys to {dir}".format(
              dir=chroot_ssh_authorized_keys))


    def _start_sshd_chroot(self, tmp_dir):
        """ Start sshd inside the chroot """
        # Define vars to have it more readable
        gl_chroot_bin = "/gardenlinux/bin/garden-chroot"
        chroot = tmp_dir
        chroot_cmd = "/usr/sbin/sshd -D -f /etc/ssh/sshd_config_integration_tests"
        # Execute in Popen as background task
        # while we may perform our integration tests
        proc_exec = "{chroot_bin} {chroot_env} {chroot_cmd}".format(
          chroot_bin=gl_chroot_bin,
          chroot_env=chroot,
          chroot_cmd=chroot_cmd)
        p = subprocess.Popen([proc_exec], shell=True)
        logger.info("Started SSHD in chroot environment.")


    def _wait_sshd(self):
        """ Wait for defined SSH port to become ready in chroot environment """
        port = self.config["port"]
        logger.info("Waiting for SSHD in chroot to be ready on tcp/{port}...".format(
          port=port))
        cmd_kvm = "ssh-keyscan -p {port} localhost".format(
          port=port)

        rc = 1
        while rc != 0:
            p = subprocess.Popen([cmd_kvm], shell=True, stdout=subprocess.PIPE, \
              stderr=subprocess.STDOUT)
            output = p.stdout.read()
            output, error = p.communicate()
            rc = p.returncode
            logger.info(str(p.returncode) + " Waiting...")
            time.sleep(5)
        logger.info("SSH ready in chroot.")


    def _create_dir(self, dir, mode):
        """ Helper func: Create directory by given path and mode """
        try:
            orig_mask = os.umask(000)
            os.makedirs(dir, mode)
            os.umask(orig_mask)
            logger.info("Created {dir} with mode {mode}.".format(
                dir=dir, mode=mode))
        except OSError:
            logger.error("Directory {dir} already present.".format(
                dir=dir))


    def _port_val(self, host, port):
        """ Helper func: Check if a port is already in use """
        logger.info("Validating if {port} on {host} is already in use.".format(
          host=host, port=port))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        try:
            s.connect((host, port))
            logger.error("Port {port} on {host} is alread in use.".format(
              host=host, port=port))
            return True
        except:
            logger.info("Port {port} on {host} can be used.".format(
              host=host, port=port))
            return False
