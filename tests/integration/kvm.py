import logging
import json
import time
import os
import subprocess
import threading
import tempfile
import time
import paramiko
import sys

from novaclient import client
from .sshclient import RemoteClient
from . import util

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BIN_DIR=os.path.join(os.path.dirname(__file__), "..", "..", "bin")

class KVM:
    """Handle KVM flavour"""

    @classmethod
    def fixture(cls, config):

        if not 'image' in config:
            logger.error("Image not defined.")
            pytest.exit("Image not defined.", 1)

        logger.info("Image %s" % config["image"])

        ip = config.get("ip)", "127.0.0.1")
        logger.info(f"Using IP {ip} to connect to VM.")
        port = config.get("port)", "2223")
        logger.info(f"Using port tcp/{port} to connect to VM.")

        kvm = KVM(config)
        cls.kvm = kvm 

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
            if kvm is not None:
                kvm.__del__()

    @classmethod
    def instance(cls):
        return cls.kvm

    def __init__(self, config):

        self.floating_ip_attached = False
        self.config = config
        if "credentials" in self.config and self.config["credentials"] != None:
            logger.info("Credentials: %s" % config["credentials"])
            self.env = self._load_credentials(self.config["credentials"])
        else:
            logger.info("No credentials")
            self.env = None

        # Create SSH
        self._generate_ssh_key()

        # Adjust KVM image 
        self._adjust_kvm()

        # Start KVM
        self._start_kvm()

        # Wait for VM in KVM to be ready
        self._wait_kvm()


    def __del__(self):
        """Cleanup resources held by this object"""
        if "keep_running" in self.config and self.config["keep_running"] == True:
            logger.info("Keeping all resources")

    # Create SSH
    def _generate_ssh_key(self):
        logger.info("Generating temporary SSH key for integration tests.")
        # Private key
        key = paramiko.RSAKey.generate(2048)
        key.write_private_key_file("/tmp/ssh_priv_key")
        # Public key (as authorized_keys)
        public_key = key.get_base64()
        with open("/tmp/authorized_keys", "w") as f:
            f.write("ssh-rsa " + public_key)
        logger.info("SSH key for integration tests generated.")

    # Adjust KVM 
    def _adjust_kvm(self):
        logger.info("Adjusting KVM image.")
        image = self.config["image"]
        authorized_keys_file = "/tmp/authorized_keys"
        sshd_config_file = "integration/misc/sshd_config"

        # Commands
        cmd_kvm_adjust = []
        cmd_kvm_adjust.append("guestfish -a {image} -i mkdir /root/.ssh".format(image=image))
        cmd_kvm_adjust.append("virt-copy-in -a {image} {authorized_keys_file} /root/.ssh/".format(image=image, authorized_keys_file=authorized_keys_file))
        cmd_kvm_adjust.append("guestfish -a {image} -i chown 0 0 /root/.ssh".format(image=image))
        cmd_kvm_adjust.append("guestfish -a {image} -i chown 0 0 /root/.ssh/authorized_keys".format(image=image))
        cmd_kvm_adjust.append("guestfish -a {image} -i chmod 0700 /root/.ssh".format(image=image))
        cmd_kvm_adjust.append("guestfish -a {image} -i chmod 0600 /root/.ssh/authorized_keys".format(image=image))
        cmd_kvm_adjust.append("virt-copy-in -a {image} {sshd_config_file} /etc/ssh/".format(image=image, sshd_config_file=sshd_config_file))
        cmd_kvm_adjust.append("guestfish -a {image} -i chown 0 0 /etc/ssh/sshd_config".format(image=image))
        cmd_kvm_adjust.append("guestfish -a {image} -i chmod 0644 /etc/ssh/sshd_config".format(image=image))
        logger.info(cmd_kvm_adjust)

        for i in cmd_kvm_adjust:
            logger.info("Running: {cmd}".format(cmd=i))
            p = subprocess.Popen([i], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output, error = p.communicate()
            rc = p.returncode
            if rc == 0:
                logger.info("Succeeded: {cmd}".format(cmd=i))
            else:
                logger.error("Failed: {cmd}".format(cmd=i))

    # Start KVM 
    def _start_kvm(self):
        logger.info("Starting VM in KVM.")
        #cmd_kvm = "uptime > /tmp/uptime.txt"
        image = self.config["image"]
        port = self.config["port"]
        cmd_kvm = "qemu-system-x86_64 -display none -daemonize -pidfile /tmp/qemu.pid -m 1024M -device virtio-net-pci,netdev=net0,mac=02:9f:ec:22:f8:89 -netdev user,id=net0,hostfwd=tcp::{port}-:22,hostname=garden {image}".format(port=port, image=image)
        logger.info(cmd_kvm)
        p = subprocess.Popen([cmd_kvm], shell=True)
        logger.info("VM in KVM started.")

    # Wait KVM
    def _wait_kvm(self):
        logger.info("Waiting for VM in KVM to be ready...")
        cmd_kvm = "ssh-keyscan -p 2223 localhost"

        rc = 1
        while rc != 0:
            p = subprocess.Popen([cmd_kvm], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = p.stdout.read()
            output, error = p.communicate()
            rc = p.returncode
            logger.info(str(p.returncode) + " Waiting...")
            time.sleep(10)
        logger.info("VM in KVM ready.")
