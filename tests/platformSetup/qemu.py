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
DEFAULT_PORT = "2223"

class QEMU:
    """Handle QEMU flavor"""

    @classmethod
    def fixture(cls, config):
        """Create and manage QEMU instance"""
        logger.info("Starting QEMU platform tests.")

        # We need to validate basic information
        # for 'RemoteClient' object first. Afterwards
        # we can run regular validation
        logger.info("Validation starting...")
        ip = config.get("ip", "127.0.0.1")
        logger.info(f"Using IP {ip} to connect to VM.")
        port = config.get("port", DEFAULT_PORT)
        logger.info(f"Using port tcp/{port} to connect to VM.")

        # Check if VM is already running
        if os.path.exists("/tmp/qemu.pid"):
            logger.info("Found existing qemu.pid - skipping VM customization and startup")
            qemu = None
        else:
            qemu = QEMU(config)
        cls.qemu = qemu

        # Initialize ssh as None before try block
        ssh = None
        
        try:
            ssh = RemoteClient(
                host=ip,
                sshconfig=config["ssh"],
                port=port,
            )
            ssh.wait_ssh()
            yield ssh

        except Exception as e:
            logger.error(f"Failed to establish SSH connection: {str(e)}")
            if qemu is not None:
                qemu.__del__()
            raise

        finally:
            if ssh is not None:
                try:
                    ssh.disconnect()
                except Exception as e:
                    logger.warning(f"Error disconnecting SSH: {str(e)}")
            
            if qemu is not None:
                try:
                    qemu.__del__()
                except Exception as e:
                    logger.warning(f"Error cleaning up QEMU: {str(e)}")

    @classmethod
    def instance(cls):
        return cls.qemu

    def __init__(self, config):

        # Define self.config
        self.config = config
        # Validate
        ssh_generate, arch, port = self._validate()
        # Create SSH
        if ssh_generate:
            self._generate_ssh_key()
        else:
            logger.info("Using defined SSH key for platform tests.")
        # Adjust QEMU image 
        self._adjust_qemu()
        # Start QEMU
        self._start_qemu(arch, port)


    def __del__(self):
        """ Cleanup resources held by this object """
        if "keep_running" in self.config and self.config["keep_running"] == True:
            logger.info("Keeping all resources")
        else:
            self._stop_qemu()
            logger.info("Done.")

    def _validate(self):
        """ Start basic config validation """
        # Validate if .raw image is defined
        image=None
        if not "image" in self.config:
            logger.error("'image' not defined. Please define path to image.")
        else:
            image = self.config["image"]
            logger.info(f"'image' defined. Using: {image}")

        # Validate if image extension is defined corretly
        allowed_image_ext = (
                            ".raw",
                            ".qcow2"
                            )
        file_name = os.path.basename(image)
        # Fail on unsupported image types
        if not file_name.endswith(allowed_image_ext):
            msg_err = f"{file_ext} is not supported for this platform test type."
            logger.error(msg_err)
            pytest.exit(msg_err, 1)

        # Validate target arch
        if "arch" in self.config:
            arch = self.config["arch"]
            logger.info(f"'arch' is defined. Executing for {arch}")
        else:
            # Setting amd64 as default if not defined
            arch = "amd64"
            logger.info("'arch' is not defined. Executing for amd64")

        # Validate if VM should remain after tests
        if "keep_running" in self.config:
            if self.config["keep_running"]:
                logger.info("'keep_running' is true. VM will remain after tests.")
            else:
                logger.info("'keep_running' is false. VM will be terminated after tests.")
        else:
            logger.info("'keep_running' not defined. VM will be terminated after tests.")

        # Get port
        port = self.config.get("port", DEFAULT_PORT)

        # Validate SSH configuration
        if "ssh" not in self.config:
            logger.error("'ssh' configuration not defined")
            pytest.exit("Missing SSH configuration", 1)

        # Check if we should generate SSH keys (default to True if not specified)
        ssh_generate = self.config["ssh"].get("ssh_key_generate", True)
        if ssh_generate:
            logger.info("Will generate new SSH keys")
        else:
            logger.info("Using existing SSH keys")

        return ssh_generate, arch, port

    def _generate_ssh_key(self):
        """ Generate new SSH key for platform test """
        logger.info("Generating new SSH key for platform tests.")
        ssh_key_path = self.config["ssh"]["ssh_key_filepath"]
        keyfp = RemoteClient.generate_key_pair(
            filename = ssh_key_path,
        )
        logger.info("SSH key for platform tests generated.")

    def _adjust_qemu(self):
        """ Adjust QEMU image and inject needed files """
        logger.info("Adjusting QEMU image. This will take some time for each command...")
        image = self.config["image"].replace("file://", "")
        image_name = os.path.basename(image)
        ssh_key_path = self.config["ssh"]["ssh_key_filepath"]
        ssh_key = os.path.basename(ssh_key_path)
        authorized_keys_file = f"{ssh_key_path}.pub"
        sshd_config_file = "platformSetup/misc/sshd_config_platform_tests"
        sshd_systemd_file = "platformSetup/misc/sshd-platform.test.service"
        nft_ssh_platform_test_config = "platformSetup/misc/nft_ssh_platform_test_ports.conf"
        authorized_keys_dir = "/root/.ssh"
        sshd_config_dir = "/etc/ssh"
        systemd_dir = "/etc/systemd/system"
        nft_dropin_config_dir = "/etc/nft.d"

        # Command list for adjustments
        cmds = []

        # Create a snapshot of the image
        # so that we can modify it for our tests
        snapshot_cmd = (
            f"qemu-img create -f qcow2 -F raw -b {image} "
            f"/tmp/{image_name}.snapshot.qcow2 4G"
        )
        cmds.append(snapshot_cmd)

        # Copy some files to the snapshot
        copy_cmd = (
            f"virt-copy-in -a /tmp/{image_name}.snapshot.qcow2 "
            f"{authorized_keys_file} {sshd_systemd_file} {sshd_config_file} "
            f"{nft_ssh_platform_test_config} /root")

        cmds.append(copy_cmd)

        # Modify the snapshot via guestfish
        authorized_keys_file = os.path.basename(authorized_keys_file)
        sshd_systemd_file = os.path.basename(sshd_systemd_file)
        sshd_config_file = os.path.basename(sshd_config_file)
        nft_ssh_platform_test_config = os.path.basename(nft_ssh_platform_test_config)
        guestfish_cmd = (
            f"guestfish -a /tmp/{image_name}.snapshot.qcow2 -i "
            f"mkdir-p {authorized_keys_dir} : "
            f"mkdir-p {nft_dropin_config_dir} : "
            f"chown 0 0 {authorized_keys_dir} : "
            f"chmod 0700 {authorized_keys_dir} : "
            f"mv /root/{authorized_keys_file} {authorized_keys_dir}/test_authorized_keys : "
            f"mv /root/{sshd_systemd_file} {systemd_dir} : "
            f"mv /root/{sshd_config_file} {sshd_config_dir} : "
            f"mv /root/{nft_ssh_platform_test_config} {nft_dropin_config_dir} : "
            f"chown 0 0 {authorized_keys_dir}/test_authorized_keys : "
            f"chmod 0600 {authorized_keys_dir}/test_authorized_keys : "
            f"chown 0 0 {sshd_config_dir}/{sshd_config_file} : "
            f"chmod 0644 {sshd_config_dir}/{sshd_config_file} : "
            f"write-append /etc/hosts.allow 'ALL: 10.\n' : "
            f"ln-s "
            f"  {systemd_dir}/{sshd_systemd_file} "
            f"  {systemd_dir}/multi-user.target.wants/{sshd_systemd_file} : "
            # Remove google services as they cannot reach their APIs
            f"rm-f /usr/lib/systemd/system/google-guest-agent.service : "
            f"rm-f /usr/lib/systemd/system/gce-workload-cert-refresh.service : "
            f"rm-f /usr/lib/systemd/system/google-startup-scripts.service")

        cmds.append(guestfish_cmd)

        # Execute all prepared commands
        for cmd in cmds:
            logger.info(f"Running: {cmd}")
            p = subprocess.run([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            rc = p.returncode
            if rc == 0:
                logger.info(f"Succeeded: {cmd}")
            else:
                error = p.stdout
                logger.error(f"Failed: {cmd}: {error}")

    def _start_qemu(self, arch, port):
        """ Start VM in QEMU for defined arch """
        logger.info("Starting VM in QEMU.")

        image = self.config["image"]
        image_name = os.path.basename(image)

        # Base command parts
        base_cmd = f"/gardenlinux/bin/start-vm \
              --daemonize \
              --port {port} \
              --destport 2222 \
              --pidfile /tmp/qemu.pid"

        # Add TPM2 flag if enabled
        if self.config.get("tpm2", False):
            base_cmd += " --tpm2"

        if arch == "amd64":
            cmd = f"{base_cmd} \
              --arch x86_64 \
              /tmp/{image_name}.snapshot.qcow2"
            logger.info(cmd)

        elif arch == "arm64":
            cmd = f"{base_cmd} \
              --arch aarch64 \
              /tmp/{image_name}.snapshot.qcow2"
            logger.info(cmd)
        else:
            logger.error("Unsupported architecture.")

        logger.info(f"VM starting as {arch} in QEMU.")
        p = subprocess.Popen([cmd], shell=True)

    def _stop_qemu(self):
        """ Stop VM and remove injected file """
        logger.info("Stopping VM and cleaning up")
        image = self.config["image"]
        image_name = os.path.basename(image)
        p = subprocess.run("pkill qemu", shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        rc = p.returncode
        if rc == 0:
            logger.info("Succeeded stopping qemu")
            if os.path.exists(f"/tmp/{image_name}.snapshot.qcow2"):
                os.remove(f"/tmp/{image_name}.snapshot.qcow2")
            else:
                logger.info(f"/tmp/{image_name}.snapshot.qcow2 does not exist")
            if os.path.exists("/tmp/qemu.pid"):
                os.remove("/tmp/qemu.pid")
        else:
            logger.error("Failed stopping qemu")
