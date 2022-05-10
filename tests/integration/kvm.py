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
from helper.sshclient import RemoteClient
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
            ssh.wait_ssh()
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
        ssh_generate, arch = self._validate()
        # Create SSH
        if ssh_generate:
            self._generate_ssh_key()
        else:
            logger.info("Using defined SSH key for integration tests.")
        # Adjust KVM image 
        self._adjust_kvm()
        # Start KVM
        self._start_kvm(arch)


    def __del__(self):
        """ Cleanup resources held by this object """
        if "keep_running" in self.config and self.config["keep_running"] == True:
            logger.info("Keeping all resources")
        else:
            self._stop_kvm()
            logger.info("Done.")

    def _validate(self):
        """ Start basic config validation """
        # Validate if .raw image is defined
        if not "image" in self.config:
            logger.error("'image' not defined. Please define path to image.")
        else:
            logger.info("'image' defined. Using: {image}".format(image=self.config["image"]))

        # Validate if image extension is defined corretly
        allowed_image_ext = [
                            "raw",
                            "qcow2"
                            ]
        file_name = os.path.basename(self.config["image"])
        # Get extensions by dot counting in reverse order
        file_ext = file_name.split(".")[1:]
        # Join file extension if we have multiple ones (e.g. .tar.gz)
        file_ext = ".".join(file_ext)
        # Fail on unsupported image types
        if not file_ext in allowed_image_ext:
            msg_err = f"{file_ext} is not supported for this platform test type."
            logger.error(msg_err)
            pytest.exit(msg_err, 1)

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

        return ssh_generate, arch

    def _generate_ssh_key(self):
        """ Generate new SSH key for integration test """
        logger.info("Generating new SSH key for integration tests.")
        ssh_key_path = self.config["ssh"]["ssh_key_filepath"]
        keyfp = RemoteClient.generate_key_pair(
            filename = ssh_key_path,
        )
        logger.info("SSH key for integration tests generated.")

    def _adjust_kvm(self):
        """ Adjust KVM image and inject needed files """
        logger.info("Adjusting KVM image. This will take some time for each command...")
        image = self.config["image"]
        image_name = os.path.basename(image)
        ssh_key_path = self.config["ssh"]["ssh_key_filepath"]
        ssh_key = os.path.basename(ssh_key_path)
        authorized_keys_file = f"{ssh_key_path}.pub"
        sshd_config_src_file = "integration/misc/sshd_config_integration_tests"
        sshd_config_dst_file = "/etc/ssh/sshd_config_integration_tests"
        sshd_systemd_src_file = "integration/misc/sshd-integration.test.service"
        systemd_dst_path = "/etc/systemd/system/"

        # Command list for adjustments
        cmd_kvm_adj = []
        # Create a snapshot image and inject SSH key
        cmd_kvm_adj.append("qemu-img create -f qcow2 -F raw -b {image} /tmp/{image_name}.snapshot.img 2G".format(
            image=image, image_name=image_name))
        cmd_kvm_adj.append("guestfish -a /tmp/{image_name}.snapshot.img -i mkdir /root/.ssh".format(
            image_name=image_name))
        cmd_kvm_adj.append("virt-copy-in -a /tmp/{image_name}.snapshot.img {authorized_keys_file} /root/.ssh/".format(
            image_name=image_name, authorized_keys_file=authorized_keys_file))
        cmd_kvm_adj.append("guestfish -a /tmp/{image_name}.snapshot.img -i mv /root/.ssh/{ssh_key}.pub /root/.ssh/test_authorized_keys".format(
            image_name=image_name, ssh_key=ssh_key))
        cmd_kvm_adj.append("guestfish -a /tmp/{image_name}.snapshot.img -i chown 0 0 /root/.ssh".format(
            image_name=image_name))
        cmd_kvm_adj.append("guestfish -a /tmp/{image_name}.snapshot.img -i chown 0 0 /root/.ssh/test_authorized_keys".format(
            image_name=image_name))
        cmd_kvm_adj.append("guestfish -a /tmp/{image_name}.snapshot.img -i chmod 0700 /root/.ssh".format(
            image_name=image_name))
        cmd_kvm_adj.append("guestfish -a /tmp/{image_name}.snapshot.img -i chmod 0600 /root/.ssh/test_authorized_keys".format(
            image_name=image_name))
        cmd_kvm_adj.append("guestfish -a /tmp/{image_name}.snapshot.img -i write-append /etc/hosts.allow 'ALL: 10.\n'".format(
            image_name=image_name))
        # Copy custom SSHD config for executing remote integration tests
        # without changing the production sshd_config. This SSHD runs on
        # port tcp/2222
        cmd_kvm_adj.append("virt-copy-in -a /tmp/{image_name}.snapshot.img {sshd_systemd_src_file} {systemd_dst_path}".format(
          image_name=image_name, sshd_systemd_src_file=sshd_systemd_src_file, systemd_dst_path=systemd_dst_path))
        cmd_kvm_adj.append("virt-copy-in -a /tmp/{image_name}.snapshot.img {sshd_config_src_file} /etc/ssh/".format(
          image_name=image_name, sshd_config_src_file=sshd_config_src_file))
        cmd_kvm_adj.append("guestfish -a /tmp/{image_name}.snapshot.img -i chown 0 0 {sshd_config_dst_file}".format(
          image_name=image_name, sshd_config_dst_file=sshd_config_dst_file))
        cmd_kvm_adj.append("guestfish -a /tmp/{image_name}.snapshot.img -i chmod 0644 {sshd_config_dst_file}".format(
          image_name=image_name, sshd_config_dst_file=sshd_config_dst_file))
        # Create a symlink since Debian watches for type 'link'
        cmd_kvm_adj.append(("guestfish -a /tmp/{image_name}.snapshot.img -i ln-s ".format(image_name=image_name) +
          "{systemd_path}sshd-integration.test.service ".format(systemd_path=systemd_dst_path) +
          "{systemd_path}multi-user.target.wants/sshd-integration.test.service".format(
            systemd_path=systemd_dst_path)))

        for i in cmd_kvm_adj:
            logger.info("Running: {cmd}".format(cmd=i))
            p = subprocess.run([i], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            rc = p.returncode
            if rc == 0:
                logger.info("Succeeded: {cmd}".format(cmd=i))
            else:
                logger.error("Failed: {cmd}".format(cmd=i))

    def _start_kvm(self, arch):
        """ Start VM in KVM for defined arch """
        logger.info("Starting VM in KVM.")
        image = self.config["image"]
        image_name = os.path.basename(image)
        port = self.config["port"]

        if arch == "amd64":
            cmd_kvm = "qemu-system-x86_64 \
              -display none \
              -daemonize \
              -pidfile /tmp/qemu.pid \
              -m 1024M \
              -device virtio-net-pci,netdev=net0,mac=02:9f:ec:22:f8:89 \
              -netdev user,id=net0,hostfwd=tcp::{port}-:2222,hostname=garden \
              /tmp/{image_name}.snapshot.img".format(port=port, image_name=image_name)
            logger.info(cmd_kvm)
            p = subprocess.Popen([cmd_kvm], shell=True)
            logger.info("VM starting as amd64 in KVM.")
        elif arch == "arm64":
            cmd_kvm = "qemu-system-aarch64 \
              -display none \
              -daemonize \
              -cpu cortex-a72 \
              -machine virt \
              -bios /usr/share/qemu-efi-aarch64/QEMU_EFI.fd \
              -pidfile /tmp/qemu.pid \
              -m 1024M \
              -device virtio-net-pci,netdev=net0,mac=02:9f:ec:22:f8:89 \
              -netdev user,id=net0,hostfwd=tcp::{port}-:2222,hostname=garden \
              /tmp/{image_name}.snapshot.img".format(port=port, image_name=image_name)
            logger.info(cmd_kvm)
            p = subprocess.Popen([cmd_kvm], shell=True)
            logger.info("VM starting as arm64 in KVM.")
        else:
            logger.error("Unsupported architecture.")

    def _stop_kvm(self):
        """ Stop VM and remove injected file """
        logger.info("Stopping VM and cleaning up")
        image = self.config["image"]
        image_name = os.path.basename(image)
        p = subprocess.run("pkill qemu", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        rc = p.returncode
        if rc == 0:
            logger.info("Succeeded stopping qemu")
            if os.path.exists("/tmp/{image_name}.snapshot.img".format(image_name=image_name)):
                os.remove("/tmp/{image_name}.snapshot.img".format(image_name=image_name))
            else:
                logger.info("/tmp/{image_name}.snapshot.img does not exist".format(image_name=image_name))
            if os.path.exists("/tmp/qemu.pid"):
                os.remove("/tmp/qemu.pid")
        else:
            logger.error("Failed stopping qemu")
