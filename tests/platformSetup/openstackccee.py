import logging
import json
import time
import os
import subprocess
import tempfile
import time
import paramiko

from novaclient import client
from helper.sshclient import RemoteClient
from . import util

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BIN_DIR=os.path.join(os.path.dirname(__file__), "..", "..", "bin")

class OpenStackCCEE:
    """Handle OpenStack CCEE flavor"""

    @classmethod
    def fixture(cls, config):

        test_name = "gl-test-" + str(int(time.time()))

        if not("image_name" in config and config["image_name"] != None):
            config["image_name"] = test_name
        if not ("vm_name" in config and config["vm_name"] != None):
            config["vm_name"] = test_name + "_vm"
        logger.info("Image name %s" % config["image_name"])

        openstack = OpenStackCCEE(config)
        cls.openstack = openstack

        if openstack.floating_ip != None:
            ip = openstack.floating_ip
        else:
            ip = openstack.ip

        logger.info(f"Using ip {ip} to connect to VM.")
        try:
            ssh = None
            ssh = RemoteClient(
                host=ip,
                sshconfig=config["ssh"],
            )
            yield ssh
        finally:
            if ssh is not None:
                ssh.disconnect()
            if openstack is not None:
                openstack.__del__()

    @classmethod
    def instance(cls):
        return cls.openstack

    def __init__(self, config):

        self.floating_ip_attached = False
        self.config = config
        if "credentials" in self.config and self.config["credentials"] != None:
            logger.info("Credentials: %s" % config["credentials"])
            self.env = self._load_credentials(self.config["credentials"])
        else:
            self.env = None

        if self.env == None:
            self.env = os.environ
        self._nova_connect()

        if "image_id" in config and config["image_id"] != None:
            result = self._image_exists(image_id=self.config["image_id"])
            if result is None:
                raise Exception("Image id %s does not exist." % config["image_id"])
            logger.info("Image %s exists. Using it" % config["image_id"])
        else:
            logger.info("Uploading new image %s" % self.config["image"])
            self.image = self._upload_image(
                self.config["image"],
                self.config["image_name"]
            )
            config["image_id"] = self.image["id"]
            logger.info("Uploaded image %s" % config["image_id"])

        if not self._ssh_key_exists(self.config["ssh"]["key_name"]):
            self._upload_ssh_key(
                keyfile=self.config["ssh"]["ssh_key_filepath"],
                keyname=self.config["ssh"]["key_name"]
            )

        self.flavor = self._get_flavor(config["flavor"])
        self.network = self._get_network(config["network_name"])

        self._boot_image(
                flavor_id=self.flavor["id"], 
                image_id=config["image_id"], 
                security_group=config["security_group"],
                network_id=self.network["id"],
                key_name=config["ssh"]["key_name"], 
                vm_name=config["image_id"]
        )
        logger.info(f"VM with id {self.vm_id} booted.")

        fip = util.get_config_value(config, "floating_ip")
        if fip != None:
            fip_json = self._get_floating_ip(fip)
            if fip_json["fixed_ip_address"] != None:
                raise Exception(f"Floating IP address {fip} is in use.")
            logger.info(f"Attaching floating ip addess {fip_json['floating_ip_address']} to vm {self.vm_id}")
            self._attach_floating_ip(self.vm_id, fip_json['floating_ip_address'])
            self.floating_ip_attached = True
            self.floating_ip = fip_json["fixed_ip_address"]

    def __del__(self):
        """Cleanup resources held by this object"""
        if "keep_running" in self.config and self.config["keep_running"] == True:
            logger.info("Keeping all resources")
        else:
            if self.floating_ip_attached:
                self._detach_floating_ip(self.vm_id, self.config["floating_ip"])
            if self.server:
                self._delete_vm(self.vm_id)
            if self.image:
                self._delete_image(self.image["id"])

    def _nova_connect(self):
        self.nova = client.Client(
            version=self.env["OS_COMPUTE_API_VERSION"],
            username=self.env["OS_USERNAME"],
            user_domain_name=self.env["OS_USER_DOMAIN_NAME"],
            password=self.env["OS_PASSWORD"],
            project_domain_name=self.env["OS_PROJECT_DOMAIN_NAME"],
            project_name=self.env["OS_PROJECT_NAME"],
            auth_url=self.env["OS_AUTH_URL"],
            http_log_debug=True
        )   


    def _load_credentials(self, filename):
        """Load Openstack credentials as exported by the OpenStack UI"""
        env = {}
        with open(filename) as f:
            while True:
                line = f.readline()
                if not line:
                    break
                elems = line.split(" ")
                if len(elems) > 0 and elems[0] == "export":
                    nv = elems[1].split("=")
                    value = nv[1].rstrip()
                    if value[0] == value[-1] == '"':
                        value = value[1:-2]
                    env[nv[0]] = value
        return env

    def _get_flavor(self, flavor):
        cmd = [
            "openstack",
            "flavor",
            "show",
            "-f",
            "json",
            flavor
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, env=self.env, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to get flavor %s" % result.stderr.decode('utf-8'))
        return json.loads(result.stdout)

    def _get_network(self, network_name):
        cmd = [
            "openstack",
            "network",
            "show",
            "-f",
            "json",
            network_name
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, env=self.env, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to get network %s" % result.stderr.decode('utf-8'))
        return json.loads(result.stdout)

    def _ssh_key_exists(self, ssh_key_name):
        cmd = [
            "openstack",
            "keypair",
            "list",
            "-f",
            "json"
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, env=self.env, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to list keypairs %s" % result.stderr.decode('utf-8'))
        doc = json.loads(result.stdout)
        for item in doc:
            if item["Name"] == ssh_key_name:
                return True
        return False

    def _upload_ssh_key(self, keyfile, keyname):
        k = paramiko.RSAKey.from_private_key_file(os.path.abspath(keyfile))
        pub = k.get_name() + " " + k.get_base64()
        tmpfile = tempfile.NamedTemporaryFile()
        fn = tmpfile.name
        tmpfile.write(bytes(pub,'ascii'))
        tmpfile.flush()
        cmd = [
            "openstack",
            "keypair",
            "create",
            "--public-key",
            fn,
            "-f",
            "json",
            keyname
        ]
        # cmd = [ "cat", fn]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, env=self.env, capture_output=True)
        tmpfile.close()
        if result.returncode != 0:
            raise Exception("Unable to upload keypair %s" % result.stderr.decode('utf-8'))
        return json.loads(result.stdout)

    def _image_exists(self, image_name=None, image_id=None):
        cmd = [
            "openstack",
            "image",
            "list",
            "-f",
            "json"
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, env=self.env, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to list images %s" % result.stderr.decode('utf-8'))
        doc = json.loads(result.stdout)
        if image_name != None:
            for item in doc:
                if item["Name"] == image_name:
                    return item["ID"]
        if image_id != None:
            for item in doc:
                if item["ID"] == image_id:
                    return item["ID"]
        return None

    def _upload_image(self, image, image_name):
        cmd = [
            os.path.join(BIN_DIR, "upload-openstack"),
            image,
            image_name
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, env=self.env, capture_output=True)
        if result.returncode != 0:
            raise Exception("Image %s could not be uploaded as %s: %s" %( image, image_name, result.stderr.decode('utf-8')))
        doc = json.loads(result.stdout)
        id = doc['id']

        cmd = [
            "openstack",
            "image",
            "set",
            "--tag",
            "purpose=platform-test",
            id
        ]
        logger.debug(json.dumps(doc, indent=4))
        result = subprocess.run(cmd, env=self.env, capture_output=True)
        if result.returncode != 0:
            logger.error("ignored: image %s could not be tagged: %s" % (id, result.stderr.decode('utf-8')))
        return doc

    def _delete_image(self, image_id):
        cmd = [
            "openstack",
            "image",
            "delete",
            image_id
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, env=self.env, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to delete image %s" % result.stderr.decode('utf-8'))

    def _boot_image(self, flavor_id, image_id, security_group, network_id, key_name, vm_name):

        self.server = self.nova.servers.create(
            name=vm_name, 
            image=image_id, 
            flavor=flavor_id,
            security_groups=[security_group],
            key_name=key_name,
            nics=[{"net-id": network_id}]
        )
        values = self.server.to_dict()
        logging.info("Waiting for VM %s to become active" % values["id"])
        time.sleep(30)
        while True:
            time.sleep(5)
            self.server.get()
            values = self.server.to_dict()
            status = values["OS-EXT-STS:vm_state"]
            logger.info("VM status: %s" % status)
            if status == "active":
                break
        # allow the operating system to boot
        logger.info("Waiting 30 seconds to allow os boot to complete.")
        time.sleep(30)
        self.server.get()
        values = self.server.to_dict()
        addresses = values["addresses"]
        addr = list(addresses.values())[0]
        self.ip = addr[0]["addr"]
        self.vm_id = values["id"]
        logger.info("VM IP address %s" % self.ip)
        return self.vm_id

    def _delete_vm(self, id):
        self._nova_connect()
        server = self.nova.servers.get(server=id)
        server.delete()

    def _get_floating_ip(self, fip):
        cmd = [
            "openstack",
            "floating",
            "ip",
            "show",
            "-f",
            "json",
            fip
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, env=self.env, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to get floating ip %s: %s" % (fip, result.stderr.decode('utf-8')))
        return json.loads(result.stdout)

    def _attach_floating_ip(self, vm_id, fip):
        cmd = [
            "openstack",
            "server",
            "add",
            "floating",
            "ip",
            vm_id,
            fip
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, env=self.env, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to attach floating ip %s to server %s: %s" % (fip, vm_id, result.stderr.decode('utf-8')))

    def _detach_floating_ip(self, vm_id, fip):
        cmd = [
            "openstack",
            "server",
            "remove",
            "floating",
            "ip",
            vm_id,
            fip
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, env=self.env, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to remove floating ip %s from server %s: %s" % (fip, vm_id, result.stderr.decode('utf-8')))
