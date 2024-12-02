import logging
import json
import os
import subprocess
import shutil
import tempfile
import paramiko
import pytest
from novaclient import client
from helper.sshclient import RemoteClient
from . import util

# Define global logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Constants
BIN_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "bin")
DEFAULT_IP = '169.254.0.21'
DEFAULT_PORT = '2222'

class FireCracker:
    """ Handle Firecracker flavor """

    @classmethod
    def fixture(cls, config):
        logger.info('Starting Firecracker platform tests.')
        # IP and SSH port need to be pre evaluated for the RemoteClient object
        logger.info('Validation starting...')
        ip = config['network'].get('ip_vm', DEFAULT_IP)
        logger.info(f'Using IP {ip} to connect to VM.')
        port = config['network'].get('port_ssh_vm', DEFAULT_PORT)
        logger.info(f'Using port tcp/{port} to connect to Firecracker instance.')

        firecracker = FireCracker(config)
        cls.firecracker = firecracker

        try:
            ssh = RemoteClient(
                host=ip,
                sshconfig=config['ssh'],
                port=port,
            )
            ssh.wait_ssh()
            yield ssh

        finally:
            if ssh is not None:
                ssh.disconnect()
            if firecracker is not None:
                firecracker.__del__()

    @classmethod
    def instance(cls):
        return cls.firecracker

    def __init__(self, config):
        self.config = config
        self._validate_config()
        self._generate_ssh_key()
        firecracker_config = self._write_config()
        self._configure_network()
        self._copy_image()
        self._modify_image()
        self._start_microvm(firecracker_config)


    def __del__(self):
        """ Cleanup resources held by this object """
        # Keep the instance running if configured or remove all created objects
        if 'keep_running' in self.config and self.config['keep_running'] == True:
            logger.warn('Keeping all resources')
        else:
            self._stop_firecracker()
            logger.info('Done.')


    def _stop_firecracker(self):
        """ Stop Firecracker microvm """
        logger.info('Stopping Firecracker microvm instance.')
        # Remap var(s) from config file
        image = self.config['image']

        # While running without socket control interface we can
        # only kill the firecracker proc
        cmd = 'killall firecracker'
        p = subprocess.run([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        rc = p.returncode
        if rc == 0:
            logger.info(f'Succeeded: {cmd}')
        else:
            error = p.stdout
            logger.error(f'Failed: {cmd}: {error}')


    def _validate_config(self):
        """ Validate PyTest config for Firecracker """
        logger.info('Validating PyTest config for Firecracker.')
        # Validate for kernel boot image
        if not 'kernel' in self.config:
            msg_err = f'No kernel image defined in config.'
            logger.error(msg_err)
            pytest.exit(msg_err, 1)

        # Validate for filesystem image
        if not 'image' in self.config:
            msg_err = f'No filesystem image defined in config.'
            logger.error(msg_err)
            pytest.exit(msg_err, 1)

        # Remap var(s) from config file
        image = self.config['image']
        kernel = self.config['kernel']

        if not os.path.isfile(kernel):
            msg_err = f'Could not find defined kernel image: {kernel}'
            logger.error(msg_err)
            pytest.exit(msg_err, 1)

        # Validate for filesystem image
        if not os.path.isfile(image):
            msg_err = f'Could not find defined filesystem image: {image}'
            logger.error(msg_err)
            pytest.exit(msg_err, 1)

        # Validate if readonly mode is set
        if not 'readonly' in self.config:
            logger.info('readonly mode is undefined. Setting to False.')
            self.config['readonly'] = False
        else:
            if type(self.config['readonly']) != bool:
                msg_err = 'VAR readonly is not type bool'
                logger.error(msg_err)
                pytest.exit(msg_err, 1)

        # Validate for a image mount path
        # Fallback to tmpdir is unset
        if not 'image_mount' in self.config:
            image_mount = tempfile.mkdtemp()
            self.config['image_mount'] = image_mount

        # Create tmp path for filesystem image
        image_copy_tmp = tempfile.mkdtemp()
        image_copy_tmp = f'{image_copy_tmp}/image_fs.ext4'
        self.config['image_copy_tmp'] = image_copy_tmp

        # Validate for a defined MAC address
        if not 'mac_vm' in self.config['network']:
            self.config['network']['mac_vm'] = '02:FC:00:00:00:05'

        # Validate for a tap host device
        if not 'if_tap_host' in self.config['network']:
            self.config['network']['if_tap_host'] = 'tap0'

        # Validate for a tap host device
        if not 'if_bridge_host' in self.config['network']:
            self.config['network']['if_bridge_host'] = 'br0'

        # Validate for a interface vm device
        if not 'if_vm' in self.config['network']:
            self.config['network']['if_vm'] = 'eth0'

        # Validate for a interface host device
        if not 'if_host' in self.config['network']:
            self.config['network']['if_host'] = 'eth0'

        # Validate for a ip vm
        if not 'ip_vm' in self.config['network']:
            self.config['network']['ip_vm'] = '169.254.0.21'

        # Validate for a netmask vm
        if not 'netmask_vm' in self.config['network']:
            self.config['network']['netmask_vm'] = '255.255.255.252'

        # Validate for a ip host
        if not 'ip_host' in self.config['network']:
            self.config['network']['ip_host'] = '169.254.0.22'

        # Validate for a netmask host
        if not 'netmask_host' in self.config['network']:
            self.config['network']['netmask_host'] = '255.255.255.252'


    def _generate_ssh_key(self):
        """ Generate new SSH key for platform test """
        logger.info('Generating new SSH key for platform tests.')
        ssh_key_path = self.config['ssh']['ssh_key_filepath']
        keyfp = RemoteClient.generate_key_pair(
            filename = ssh_key_path,
        )
        logger.info('SSH key for platform tests generated.')


    def _write_config(self):
        """ Write Firecracker JSON config file """
        logger.info(f'Writing Firecracker JSON config file.')
        # Remap vars from config file
        kernel = self.config['kernel']
        image_copy_tmp = self.config['image_copy_tmp']
        readonly = self.config['readonly']
        ip_vm = self.config['network']['ip_vm']
        netmask_vm = self.config['network']['netmask_vm']
        if_vm = self.config['network']['if_vm']
        mac_vm = self.config['network']['mac_vm']
        ip_host = self.config['network']['ip_host']
        if_tap_host = self.config['network']['if_tap_host']

        # Create config tmp file
        _firecracker_config_file = tempfile.NamedTemporaryFile(delete=False)
        firecracker_config_file = _firecracker_config_file.name

        # Generate JSON config
        firecracker_config = {
            'boot-source': {
                'boot_args': f'ro console=ttyS0 noapic reboot=k panic=1 pci=off nomodules random.trust_cpu=on ip={ip_vm}::{ip_host}:{netmask_vm}::{if_vm}:off',
                'kernel_image_path': kernel
            },
            'drives': [
                {
                    'drive_id': 'rootfs',
                    'is_read_only': readonly,
                    'is_root_device': True,
                    'path_on_host': image_copy_tmp
                }
            ],
            'machine-config': {
                'mem_size_mib': 1024,
                'vcpu_count': 2
            },
            'network-interfaces': [
                {
                    'guest_mac': mac_vm,
                    'host_dev_name': if_tap_host,
                    'iface_id': if_vm
                }
            ]
        }

        # Write JSON config file for Firecracker
        try:
            with open(firecracker_config_file, 'w') as f:
                json.dump(firecracker_config, f, indent=4, sort_keys=True)
            logger.info(f'Firecracker JSON config file written to: {firecracker_config_file}.')
        except json.JSONDecodeError:
            logger.error('Unable to write JSON config file. Please verify config content.')

        return firecracker_config_file


    def _configure_network(self):
        """ Configure network settings for container """
        logger.info(f'Configuring network in container.')
        # Remap vars from config file
        ip_host = self.config['network']['ip_host']
        if_host = self.config['network']['if_host']
        if_bridge_host = self.config['network']['if_bridge_host']
        if_tap_host = self.config['network']['if_tap_host']

        # Configure network bridge and enable proxy arp on
        # tap interface within the container
        cmds = []
        cmds.append(f'ip link add {if_bridge_host} type bridge')
        cmds.append(f'ip link set {if_host} master {if_bridge_host}')
        cmds.append(f'ip tuntap add {if_tap_host} mode tap')
        cmds.append(f'ip link set {if_tap_host} master {if_bridge_host}')
        cmds.append(f'ip link set {if_tap_host} up')
        cmds.append(f'ip link set {if_bridge_host} up')
        cmds.append(f'sysctl -w net.ipv4.conf.{if_tap_host}.proxy_arp=1')
        cmds.append(f'ip addr add {ip_host}/30 dev {if_bridge_host}')

        # Execute all commands
        for cmd in cmds:
            logger.info(f'Running: {cmd}')
            p = subprocess.run([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            rc = p.returncode
            if rc == 0:
                logger.info(f'Succeeded: {cmd}')
            else:
                error = p.stdout
                logger.error(f'Failed: {cmd}: {error}')


    def _copy_image(self):
        """ Create a copy of the filesystem image to work on """
        logger.info(f'Creating filesystem image copy to avoid modifying production images.')
        image = self.config['image']
        image_copy_tmp = self.config['image_copy_tmp']

        # Create copy of filesystem image
        try:
            shutil.copyfile(image, image_copy_tmp)
        except IOError as e:
            logger.error(f'Could not copy file: {e}')


    def _modify_image(self):
        """ Modify filesystem image to fit all needs for running platform tests """
        self._mount_image()
        self._adjust_image()
        self._unmount_image()


    def _mount_image(self):
        """ Mount filesystem image to a defined path from config """
        # Remap vars from config file
        image_copy_tmp = self.config['image_copy_tmp']
        mnt_dir = self.config['image_mount']

        # Create mount path if not already present
        try:
            os.mkdir(mnt_dir)
        except FileExistsError:
            pass

        # Mount filesystem image to defined mount path
        cmd = f'mount -o loop {image_copy_tmp} {mnt_dir}'
        p = subprocess.run([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        rc = p.returncode
        if rc == 0:
            logger.info(f'Succeeded: {cmd}')
        else:
            error = p.stdout
            logger.error(f'Failed: {cmd}: {error}')


    def _adjust_image(self):
        """ Adjust filesystem image to include authorized_keys, sshd- & nft configs """
        # Remap vars from config file
        mnt_dir = self.config['image_mount']
        ssh_key_path = self.config['ssh']['ssh_key_filepath']

        # Define additional vars
        authorized_keys_file = f'{ssh_key_path}.pub'
        systemd_dir = '/etc/systemd/system'
        sshd_config_file = 'platformSetup/misc/sshd_config_platform_tests'
        sshd_systemd_file = 'platformSetup/misc/sshd-platform.test.service'
        nft_ssh_platform_test_config = 'platformSetup/misc/nft_ssh_platform_test_ports.conf'
        nft_config_name = 'nft_ssh_platform_test_ports.conf'
        authorized_keys_dir = '/root/.ssh'
        sshd_config_dir = '/etc/ssh'
        systemd_dir = '/etc/systemd/system'
        nft_dropin_config_dir = '/etc/nft.d'

        # Reset umask to a known default value to avoid
        # unexpected permissions
        os.umask(0)

        ## Create needed directories including desired permissions
        # Dictionary: Including all directories and permissions to create
        dir_perm_dict = {
            f'{mnt_dir}/root/.ssh/': 0o700,
            f'{mnt_dir}{nft_dropin_config_dir}': 0o700
        }

        # Create all directories from dict
        for k,v in dir_perm_dict.items():
            try:
                os.makedirs(k, v)
            except FileExistsError:
                pass


        ## Copy all needed files to destination
        # Dictionary: Including all source files and their destinations
        file_copy_dict = {
            authorized_keys_file: f'{mnt_dir}{authorized_keys_dir}/test_authorized_keys',
            sshd_config_file: f'{mnt_dir}{sshd_config_dir}/sshd_config_platform_tests',
            nft_ssh_platform_test_config: f'{mnt_dir}{nft_dropin_config_dir}/{nft_config_name}',
            sshd_systemd_file: f'{mnt_dir}{systemd_dir}/sshd-platform.test.service'
        }

        # Copy all files to their destination
        try:
            for k,v in file_copy_dict.items():
                shutil.copyfile(k, v)
        except IOError as e:
            logger.error(f'Could not copy file: {e}')

        # Adjust permissions of files
        os.chmod(f'{mnt_dir}/root/.ssh/test_authorized_keys', 0o600)

        ## Run additional commands
        # List: Including all commands that needs to be executed
        cmds = []
        cmds.append(f'echo "ALL: ALL" >> {mnt_dir}/etc/hosts.allow')
        cmds.append(f'ln -s {systemd_dir}/sshd-platform.test.service \
            {mnt_dir}{systemd_dir}/multi-user.target.wants/sshd-platform.test.service')

        # Execute all commands
        for cmd in cmds:
            p = subprocess.run([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            rc = p.returncode
            if rc == 0:
                logger.info(f'Succeeded: {cmd}')
            else:
                error = p.stdout
                logger.error(f'Failed: {cmd}: {error}')


    def _unmount_image(self):
        """ Unmount filesystem image from mount path """
        # Remap var(s) from config file
        mnt_dir = self.config['image_mount']

        cmd = f'umount {mnt_dir}'
        p = subprocess.run([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        rc = p.returncode
        if rc == 0:
            logger.info(f'Succeeded: {cmd}')
        else:
            error = p.stdout
            logger.error(f'Failed: {cmd}: {error}')


    def _start_microvm(self, firecracker_config):
        """ Start Firecracker image as microvm """
        logger.info(f'Firecracker microvm starting...')
        binary = 'firecracker --no-api --config-file'
        cmd = f'{binary} {firecracker_config}'

        # We need to execute this cmd in background.
        # Therefore, we use Popen instead of run
        logger.info(f'Running {cmd}')
        p = subprocess.Popen([cmd], shell=True)
