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
from helper.sshclient import RemoteClient
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
            ssh.wait_ssh()
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
        rootfs = self._unarchive_image()
        # Generate temporary keys for integration testing
        self._generate_ssh_key()
        # Adjust chroot to be able to connect
        self._adjust_chroot(rootfs)
        # Start sshd inside the chroot
        self._start_sshd_chroot(rootfs)


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

        # Validate if image extension is defined corretly
        allowed_image_ext = (
                            ".tar.xz",
                            ".txz",
                            ".tgz",
                            ".tar",
                            ".tar.gz"
                            )
        file_name = os.path.basename(self.config["image"])
        # Fail on unsupported image types
        if not file_name.endswith(allowed_image_ext):
            msg_err = f"{file_ext} is not supported for this platform test type."
            logger.error(msg_err)
            pytest.exit(msg_err, 1)

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
        logger.info("Creating rootfs as tmpdir")
        rootfs = tempfile.mkdtemp(prefix="gl-int-chroot-")
        logger.info("Created rootfs in {rootfs}".format(
          rootfs=rootfs))
        logger.info("Unarchiving image {image} to {rootfs}".format(
          image=image, rootfs=rootfs))
        try:
            cmd = (("tar -xp --acl --selinux --anchored --xattrs ")+
                   ("--xattrs-include='security.capability' ")+
                   ("-f '{image}' -C '{rootfs}'".format(image=image,rootfs=rootfs)))
            p = subprocess.run([cmd], shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, check=True)
            logger.info("Unarchived image {image} to {rootfs}".format(
              image=image, rootfs=rootfs))
        except subprocess.CalledProcessError:
            logger.error("Error while unarchiving image {image} to {rootfs}".format(
              image=image, rootfs=rootfs))
            pytest.exit("Error", 1)
        except OSError:
            logger.error("Error while unarchiving image {image} to {rootfs}".format(
              image=image, rootfs=rootfs))
            pytest.exit("Error", 1)
        return rootfs


    def _generate_ssh_key(self):
        """ Generate new SSH key for integration test """
        logger.info("Generating new SSH key for integration tests.")
        ssh_key_path = self.config["ssh"]["ssh_key_filepath"]
        keyfp = RemoteClient.generate_key_pair(
            filename = ssh_key_path,
        )
        logger.info("SSH key for integration tests generated.")


    def _adjust_chroot(self, rootfs):
        """ Adjust chroot to make it usable """
        logger.info("Adjusting chroot environment")
        # Adjust garden-epoch to dev
        chroot_epoch = rootfs + "/" + "garden-epoch"
        if os.path.exists(chroot_epoch):
            logger.warning("'garden-epoch' already present. This will be set to 'dev', now.")
        try:
            with open(chroot_epoch, 'w') as f:
                f.write("dev")
            logger.info("Wrote garden-epoch to chroot in {rootfs}".format(
              rootfs=rootfs))
        except IOError:
            logger.error("Could not write garden-epoch to chroot in {rootfs}".format(
              rootfs=rootfs))
        # Install openssh-server if needed for platforms that were
        # created without ssh-server
        if not os.path.exists(f'{rootfs}/usr/sbin/sshd'):
            cmd_ssh_install = []
            cmd_ssh_install.append(f'chroot {rootfs} /bin/bash -c "apt-get update && apt-get -y install openssh-server"')
            cmd_ssh_install.append(f'chroot {rootfs} /bin/bash -c "apt --fix-broken install"')
            for i in cmd_ssh_install:
                logger.info("Running command: {cmd}".format(
                  cmd=i))
                p = subprocess.run([i], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                rc = p.returncode
                if rc != 0:
                    logger.error("Command failed.")
                else:
                    logger.info("Command sucessfully executed.")
        # Generate SSH hostkeys for chroot
        # (this way we do not need to execute this inside the 'chroot'
        #  environment and still support amd64 and arm64 architectures)
        chroot_ssh_dir = rootfs + "/etc/ssh/"
        cmd_ssh_keys = []
        cmd_ssh_keys.append('ssh-keygen -q -N "" -t dsa -f {ssh_dir}/ssh_host_dsa_key'.format(
          ssh_dir=chroot_ssh_dir))
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
        chroot_sshd_run_dir = rootfs + "/run/sshd"
        try:
            os.mkdir(chroot_sshd_run_dir)
            logger.info("Created directory: {dir}".format(
              dir=chroot_sshd_run_dir))
        except OSError:
            logger.error("Could not create directory: {dir}".format(
              dir=chroot_sshd_run_dir))
        # Copy dedicated sshd config to chroot
        sshd_config_src_file = "integration/misc/sshd_config_integration_tests"
        chroot_sshd_cfg_dir = rootfs + "/etc/ssh/"
        try:
            shutil.copy(sshd_config_src_file, chroot_sshd_cfg_dir)
            logger.info("Copied sshd_config_integration_tests to: {dir}".format(
              dir=chroot_sshd_cfg_dir))
        except OSError:
            logger.error("Could not copy sshd_config_integration_tests to {dir}".format(
              dir=chroot_sshd_cfg_dir))
        # Copy ssh / authorized_keys file for root user
        local_ssh_key_path = self.config["ssh"]["ssh_key_filepath"] + ".pub"
        chroot_root_dir = rootfs + "/root/"
        chroot_ssh_authorized_keys = chroot_root_dir + ".ssh/test_authorized_keys"
        self._create_dir(chroot_root_dir+".ssh", 0o600)
        try:
            shutil.copyfile(local_ssh_key_path, chroot_ssh_authorized_keys)
            logger.info("Copied authorized_keys to: {dir}".format(
              dir=chroot_ssh_authorized_keys))
        except OSError:
            logger.error("Could not copy authorized_keys to {dir}".format(
              dir=chroot_ssh_authorized_keys))


    def _start_sshd_chroot(self, rootfs):
        """ Start sshd inside the chroot """
        # Define vars to have it more readable
        gl_chroot_bin = "/gardenlinux/bin/garden-chroot"
        chroot_cmd = "/usr/sbin/sshd -D -f /etc/ssh/sshd_config_integration_tests"
        # Execute in Popen as background task
        # while we may perform our integration tests
        proc_exec = "{chroot_bin} {chroot_env} {chroot_cmd}".format(
          chroot_bin=gl_chroot_bin,
          chroot_env=rootfs,
          chroot_cmd=chroot_cmd)
        p = subprocess.Popen([proc_exec], shell=True)
        logger.info("Started SSHD in chroot environment.")


    def _create_dir(self, dir, mode):
        """ Helper func: Create directory by given path and mode """
        orig_mask = os.umask(000)
        try:
            os.makedirs(dir, mode)
            logger.info("Created {dir} with mode {mode}.".format(
                dir=dir, mode=mode))
        except OSError:
            logger.error("Directory {dir} already present.".format(
                dir=dir))
        os.umask(orig_mask)


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
