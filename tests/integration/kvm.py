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
from novaclient import client
from .sshclient import RemoteClient
from . import util

# Define global logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BIN_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "bin")

class KVM:
    """Handle KVM flavour"""

    @classmethod
    def fixture(cls, config):

        logger.info("Starting KVM integration tests.")

        # We need to validate basic information
        # for 'RemoteClient' object first. Afterwards
        # we can run regular validation
        logger.info("Validation starting...")
        ip = config.get("ip", "127.0.0.1")
        logger.info(f"Using IP {ip} to connect to VM.")
        port = config.get("port", "2223")
        logger.info(f"Using port tcp/{port} to connect to VM.")

        kvm = KVM(config)
        cls.kvm = kvm 

        try:
            ssh = RemoteClient(
                host=ip,
                sshconfig=config["ssh"],
                port=port,
            )
            yield ssh
        finally:
            if ssh is not None:
                ssh.disconnect()
            if kvm is not None:
                kvm.__del__()

    @classmethod
    def instance(cls):
        return cls.kvm

    def __init__(self, config):

        # Define self.config
        self.config = config
        # Validate
        ssh_inject, ssh_generate, arch = self._validate()
        # Create SSH
        if ssh_generate:
            self._generate_ssh_key()
        else:
            logger.info("Using defined SSH key for integration tests.")
        # Adjust KVM image 
        self._adjust_kvm(ssh_inject)
        # Start KVM
        self._start_kvm(arch)
        # Wait for VM in KVM to be ready
        self._wait_kvm()

    def __del__(self):
        """ Cleanup resources held by this object """
        if "keep_running" in self.config and self.config["keep_running"] == True:
            logger.info("Keeping all resources")

    def _validate(self):
        """ Start basic config validation """
        # Validate if .raw image is defined
        if not "image" in self.config:
            logger.error("'image' not defined. Please define path to image.")
        else:
            logger.info("'image' defined. Using: {image}".format(image=self.config["image"]))

        # Validate if image is already running
        pid = os.path.exists("/tmp/qemu.pid")
        if pid:
            logger.warning(("PID file is present. Probably a VM for integrationtest "+
                           "is already running. This may cause issues for SSH key injection."))
        else:
            logger.info("No PID file found. We can adjust and start the VM.")

        # Validate target arch
        if "arch" in self.config:
                logger.info("'arch' is defined. Executing for {arch}".format(
                  arch=self.config["arch"]))
                arch = self.config["arch"]
        else:
                # Setting amd64 as default if not defined
                logger.info("'arch' is not defined. Executing for amd64")
                arch = "amd64"

        # Validate if VM should remain after tests
        if "keep_running" in self.config:
            if self.config["keep_running"]:
                logger.info("'keep_running' is true. VM will remain after tests.")
            else:
                logger.info("'keep_running' is false. VM will be terminated after tests.")
        else:
            logger.info("'keep_running' not defined. VM will be terminated after tests.")

        # Validate if SSH key should be generated (default)
        if self.config["ssh"]["ssh_key_generate"]:
            logger.info("'ssh_key_generate' is true. New random SSH keys will be generated.")
            # Validate if key files are present on filesystem
            # to avoid overwriting them
            ssh_keys = os.path.exists(self.config["ssh"]["ssh_key_filepath"])
            if ssh_keys:
                ssh_generate = False
                logger.error(("'ssh_key_filepath' is defined and private key is present. " +
                              "We can NOT safely generate keys without overwriting them."))
                pytest.exit("Stopping!", 1)
            else:
                logger.info("'ssh_key_filepath' is not defined. We can safely generate keys.")
                ssh_generate = True
        else:
            logger.info("'ssh_key_generate' is false. No SSH keys will be generated.")
            ssh_generate = False

        # Validate if a SSH user is defined
        if not "user" in self.config["ssh"]:
            user = "root"
            logger.info("'user' is not defined. Default user root will be used.")
        else:
            user = self.config["ssh"]["user"]
            logger.info("'user' is defined. Using user {user}.".format(user=user))

        # Validate if a SSH key was already injected
        # (Check for an 'authorized_keys' file for 'root')
        logger.info("Validating if a SSH key already got injected to image.")
        image = self.config["image"]
        kvm_file_val = "/root/.ssh/authorized_keys"
        cmd_kvm_val = "guestfish --ro -a {image} -i checksum sha256 {fname}".format(
          image=image, fname=kvm_file_val)
        p = subprocess.Popen([cmd_kvm_val], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output, error = p.communicate()
        rc = p.returncode
        if rc == 0:
            logger.warning("SSH file already present: {fname}".format(fname=kvm_file_val))
            logger.warning("No SSH key will be injected.")
            ssh_inject = False
        else:
            logger.info("SSH file not present: {fname}".format(fname=kvm_file_val))
            logger.info("SSH key will be injected.")
            ssh_inject = True
        return ssh_inject, ssh_generate, arch

    def _generate_ssh_key(self):
        """ Generate new SSH key for integration test if needed """
        logger.info("Generating new SSH key for integration tests.")
        ssh_key_path = self.config["ssh"]["ssh_key_filepath"]
        # Private key
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file(ssh_key_path)
        # Public key (as authorized_keys)
        public_key = key.get_base64()
        with open("/tmp/authorized_keys", "w") as f:
            f.write("ssh-rsa " + public_key)
        logger.info("SSH key for integration tests generated.")

    def _adjust_kvm(self, ssh_inject):
        """ Adjust KVM image and inject needed files """
        logger.info("Adjusting KVM image. This will take some time for earch command...")
        image = self.config["image"]
        authorized_keys_file = "/tmp/authorized_keys"
        sshd_config_file = "integration/misc/sshd_config"

        # Command list for adjustments
        cmd_kvm_adj = []
        # Only inject SSH keys if they're not
        # already present in .raw image
        if ssh_inject:
            cmd_kvm_adj.append("guestfish -a {image} -i mkdir /root/.ssh".format(
              image=image))
            cmd_kvm_adj.append("virt-copy-in -a {image} {authorized_keys_file} /root/.ssh/".format(
              image=image, authorized_keys_file=authorized_keys_file))
            cmd_kvm_adj.append("guestfish -a {image} -i chown 0 0 /root/.ssh".format(
              image=image))
            cmd_kvm_adj.append("guestfish -a {image} -i chown 0 0 /root/.ssh/authorized_keys".format(
              image=image))
            cmd_kvm_adj.append("guestfish -a {image} -i chmod 0700 /root/.ssh".format(
              image=image))
            cmd_kvm_adj.append("guestfish -a {image} -i chmod 0600 /root/.ssh/authorized_keys".format(
              image=image))
        cmd_kvm_adj.append("virt-copy-in -a {image} {sshd_config_file} /etc/ssh/".format(
          image=image, sshd_config_file=sshd_config_file))
        cmd_kvm_adj.append("guestfish -a {image} -i chown 0 0 /etc/ssh/sshd_config".format(
          image=image))
        cmd_kvm_adj.append("guestfish -a {image} -i chmod 0644 /etc/ssh/sshd_config".format(
          image=image))

        for i in cmd_kvm_adj:
            logger.info("Running: {cmd}".format(cmd=i))
            p = subprocess.Popen([i], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output, error = p.communicate()
            rc = p.returncode
            if rc == 0:
                logger.info("Succeeded: {cmd}".format(cmd=i))
            else:
                logger.error("Failed: {cmd}".format(cmd=i))

    def _start_kvm(self, arch):
        """ Start VM in KVM for defined arch """
        logger.info("Starting VM in KVM.")
        image = self.config["image"]
        port = self.config["port"]

        if arch == "amd64":
            cmd_kvm = "qemu-system-x86_64 \
              -display none \
              -daemonize \
              -pidfile /tmp/qemu.pid \
              -m 1024M \
              -device virtio-net-pci,netdev=net0,mac=02:9f:ec:22:f8:89 \
              -netdev user,id=net0,hostfwd=tcp::{port}-:22,hostname=garden \
              {image}".format(port=port, image=image)
            logger.info(cmd_kvm)
            p = subprocess.Popen([cmd_kvm], shell=True)
            logger.info("VM starting as amd64 in KVM.")
        if arch == "arm64":
            cmd_kvm = "qemu-system-aarch64 \
              -display none \
              -daemonize \
              -cpu cortex-a72 \
              -machine virt \
              -bios /usr/share/qemu-efi-aarch64/QEMU_EFI.fd \
              -pidfile /tmp/qemu.pid \
              -m 1024M \
              -device virtio-net-pci,netdev=net0,mac=02:9f:ec:22:f8:89 \
              -netdev user,id=net0,hostfwd=tcp::{port}-:22,hostname=garden \
              {image}".format(port=port, image=image)
            logger.info(cmd_kvm)
            p = subprocess.Popen([cmd_kvm], shell=True)
            logger.info("VM starting as arm64 in KVM.")
        else:
            logger.info("Unsupported architecture.")

    def _wait_kvm(self):
        """ Wait for defined SSH port to become ready in VM """
        logger.info("Waiting for VM in KVM to be ready...")
        port = self.config["port"]
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
            time.sleep(10)
        logger.info("VM in KVM ready.")
