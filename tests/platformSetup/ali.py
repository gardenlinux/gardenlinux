import logging
import json
import time
import os
import subprocess
import tempfile
import requests
import base64

from urllib.request import urlopen
from urllib.parse import urlparse

from helper.sshclient import RemoteClient
from . import util

from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526 import DeleteImageRequest
from aliyunsdkecs.request.v20140526 import DescribeImagesRequest
from aliyunsdkecs.request.v20140526 import ImportImageRequest
from aliyunsdkecs.request.v20140526.CreateInstanceRequest import CreateInstanceRequest
from aliyunsdkecs.request.v20140526.StartInstanceRequest import StartInstanceRequest
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526.AllocatePublicIpAddressRequest import AllocatePublicIpAddressRequest
from aliyunsdkecs.request.v20140526.DeleteInstanceRequest import DeleteInstanceRequest
from aliyunsdkecs.request.v20140526.DescribeImagesRequest import DescribeImagesRequest
from aliyunsdkecs.request.v20140526.ImportImageRequest import ImportImageRequest
from aliyunsdkecs.request.v20140526.DeleteImageRequest import DeleteImageRequest
from aliyunsdkecs.request.v20140526.ImportKeyPairRequest import ImportKeyPairRequest
from aliyunsdkecs.request.v20140526.DeleteKeyPairsRequest import DeleteKeyPairsRequest
from aliyunsdkecs.request.v20140526.DescribeKeyPairsRequest import DescribeKeyPairsRequest
import oss2

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BIN_DIR=os.path.join(os.path.dirname(__file__), "..", "..", "bin")

class ALI:
    """Handle Ali"""

    @classmethod
    def fixture(cls, config, test_name):
        config["test-name"] = test_name
        if not("image_name" in config and config["image_name"] != None):
            config["image_name"] = test_name
        if not ("vm_name" in config and config["vm_name"] != None):
            config["vm_name"] = test_name + "_vm"
        if not "image_region" in config:
            config["image_region"] = "eu-central-1"
        logger.info("Image name %s" % config["image_name"])

        ali = ALI(config)

        (instance, ip) = ali._boot_image(
                zone_id=config["zone_id"],
                image_id=config["image_id"],
                instance_type=config["instance_type"],
                vswitch_id=config["vswitch_id"],
                instance_name=config["vm_name"],
                ssh_keyname=config["ssh"]["key_name"],
                security_group_id=config["security_group_id"]
        )
        ali.instance = instance
        ali.ip = ip["IpAddress"]
        cls.ali = ali
        logger.info("VM booted, waiting for 30 seconds to make sure the boot process has finished")
        time.sleep(30)

        try:
            ssh = None
            ssh = RemoteClient(
                host=ali.ip,
                sshconfig=config["ssh"],
            )
            yield ssh
        finally:
            if ssh is not None:
                ssh.disconnect()
            if ali is not None:
                ali.__del__()

    @classmethod
    def instance(cls):
        return cls.ali

    def __init__(self, config):
        self.config = config
        self.image_created = False
        self.ssh_config = self.config["ssh"]
        self.ssh_key_uploaded = False
        credentials = config["credential_file"]
        (access_key_id, access_key_secret) = self._read_credentials(credentials)
        self.oss_auth = oss2.Auth(access_key_id, access_key_secret)
        self.acs_client = AcsClient(access_key_id, access_key_secret, config["region_id"])
        self.oss_endpoint = "https://oss-" + config["region_id"] + ".aliyuncs.com"

        if "image_id" in config and config["image_id"] != None:
            if not self._image_exists(image_id=self.config["image_id"]):
                raise Exception("Image id %s does not exist." % config["image_id"])
            logger.info("Image %s exists. Using it for test." % config["image_id"])            
        else:
            self.image_name_in_bucket = ""
            if "bucket_path" in config and config["bucket_path"] != "":
                self.image_name_in_bucket += config["bucket_path"] + "/"
            self.image_name_in_bucket += config["test-name"] + ".qcow2"
            logger.info("Uploading new image %s" % self.config["image"])
            config["image_id"] = self.image = self._upload_image(
                bucket_name=self.config["bucket"],
                image=self.config["image"],
                image_name_in_bucket=self.image_name_in_bucket
            )
            logger.info("Uploaded image %s" % config["image_id"])

        if self.ssh_config.get("key_name", None) == None:
            self.ssh_config["key_name"] = f"ssh-key-{self.config['test-name']}"

        if not self._ssh_key_exists(self.ssh_config["key_name"]):
            if self.ssh_config.get("ssh_key_filepath", None) == None:
                import tempfile
                keyfile = tempfile.NamedTemporaryFile(prefix=f"sshkey-{self.config['test_name']}-", suffix=".key", delete=False)
                keyfp = RemoteClient.generate_key_pair(
                    filename = keyfile.name,
                )
                self.ssh_config["ssh_key_filepath"] = keyfile.name
                logger.info(f"Generated SSH keypair with fingerprint {keyfp}.")

            self._upload_ssh_key(
                keyfile=self.ssh_config["ssh_key_filepath"],
                keyname=self.ssh_config["key_name"]
            )

    def __del__(self):
        """Cleanup resources held by this object"""
        if "keep_running" in self.config and self.config["keep_running"] == True:
            logger.info("Keeping all resources")
        else:
            if self.instance:
                self._delete_vm(self.instance_id)
            if self.image_created:
                self._delete_image(self.config["image_id"])
                bucket = oss2.Bucket(self.oss_auth, self.oss_endpoint, self.config["bucket"])
                bucket.delete_object(self.config["test-name"] + ".qcow2")
            if self.ssh_key_uploaded:
                self._delete_ssh_key(self.config["ssh"]["key_name"])


    def _read_credentials(self, file):
        with open(file, "r") as f:
            creds = json.load(f)
        current_profile = creds["current"]
        for p in creds["profiles"]:
            if p["name"] == current_profile:
                return (p["access_key_id"], p["access_key_secret"])
        return (None, None)

    def _ssh_key_exists(self, ssh_key_name):
        request = DescribeKeyPairsRequest()
        request.set_KeyPairName(ssh_key_name)
        response = self._send_request(request)
        if response["TotalCount"] > 0:
            logger.info(f"Key {ssh_key_name} exists.")
            return True
        else:
            logger.info(f"Key {ssh_key_name} does not exist.")
            return False

    def _upload_ssh_key(self, keyfile, keyname):
        request = ImportKeyPairRequest()
        request.set_KeyPairName(keyname)
        request.set_PublicKeyBody(util.get_public_key(keyfile))
        response = self._send_request(request)
        if not ("KeyPairName" in response and response["KeyPairName"] == keyname):
            logger.info(response)
            raise Exception(f"key pair {keyname} not uploaded")
        self.ssh_key_uploaded = True

    def _delete_ssh_key(self, keyname):
        request = DeleteKeyPairsRequest()
        request.set_KeyPairNames(keyname)
        response = self._send_request(request)
        logger.info("ssh key delete key pair response")
        logger.info(response)

    def _image_exists(self, image_id):
        request = DescribeImagesRequest()
        request.set_ImageId(image_id)
        response = self._send_request(request)
        if response != None and "TotalCount" in response and response["TotalCount"] == 1:
            return True
        else:
            return False

    def _upload_image(self, bucket_name, image, image_name_in_bucket):
        bucket = oss2.Bucket(self.oss_auth, self.oss_endpoint, bucket_name)

        o = urlparse(image)
        if o.scheme == "file":
            logger.info(f"Uploading image {image} - this may take a while...")
            with open(o.path, "rb") as fileobj:
                bucket.put_object(image_name_in_bucket, fileobj)

        elif o.scheme == "s3":
            s3_url = f"https://{o.hostname}.s3.{self.config['image_region']}.amazonaws.com/{o.path.lstrip('/')}"
            meta = urlopen(s3_url)
            file_size = int(meta.getheader('Content-Length'))
            chunk_size = 4 * 1024 * 1024

            logger.info(f"Downloading from {s3_url} ({file_size} bytes) to temporary file...")
            with tempfile.TemporaryFile() as tfh:
                with requests.get(s3_url, stream=True) as r:
                    for chunk in r.iter_content(chunk_size=chunk_size): 
                        tfh.write(chunk)

                tfh.seek(0)

                logger.info(f"Re-uploading image to Ali-Cloud bucket {bucket.bucket_name}/{image_name_in_bucket} ({file_size} bytes)...")
                bucket.put_object(image_name_in_bucket, tfh)

        logger.info(f"Image blob successfully uploaded to Ali-Cloud bucket {bucket.bucket_name}/{image_name_in_bucket}")

        request = ImportImageRequest()
        request.set_Description(self.config["test-name"])
        request.set_Platform('Others Linux')
        request.set_ImageName(self.config["test-name"])
        devMap = [{
            "OSSBucket": bucket_name,
            "DiskImageSize": "5",
            "Format": "qcow2",
            "OSSObject": image_name_in_bucket,
        }]
        request.set_DiskDeviceMappings(devMap)
        response = self._send_request(request)
        image_id = response["ImageId"]
        logger.info(response)

        self._wait_for_image(image_id)
        logger.info(
            f"finished importing image {image_id}"
        )
        self.image_created = True
        bucket.delete_object(image_name_in_bucket)
        return image_id

    def _delete_disk_image(bucket_name, image_name_in_bucket):
        bucket = oss2.Bucket(self.oss_auth, self.oss_endpoint, bucket_name)
        bucket.delete

    def _wait_for_image(self, image_id):
        logger.info(f"Image id is {image_id}. Waiting for 120s before checking whether image got created.")
        time.sleep(120)
        request = DescribeImagesRequest()
        request.set_ImageId(image_id)
        request.set_Status(",".join(["Creating", "Available", "UnAvailable", "CreateFailed", "Waiting"]))
        max_tries = 120
        while max_tries > 0:
            max_tries -= 1
            time.sleep(10)
            response = self._send_request(request)
            #logger.info(json.dumps(response, indent=4))
            if response.get("TotalCount") >= 1:
                status = response.get("Images").get("Image")[0].get("Status")
                if status == "Available":
                    return
                else:
                    logger.info(f"Image import status: {status}")
            else:
                logger.info("Unknown image import status.")
        raise Exception(f"Image {image_id} not available.")

    def _delete_image(self, image_id):
        logger.info(f"Deleting image {image_id}")
        request = DeleteImageRequest()
        request.set_ImageId(image_id)
        response = self._send_request(request)
        logger.info(response)

    def _boot_image(self, zone_id, image_id, instance_type, vswitch_id, instance_name, ssh_keyname, security_group_id):

        startup_script = """#!/bin/bash
        systemctl start ssh
        """

        startup_script_encoded = base64.b64encode(startup_script.encode('utf-8')).decode('utf-8')


        request = CreateInstanceRequest()
        request.set_UserData(startup_script_encoded)
        request.set_ImageId(image_id)
        request.set_SecurityGroupId(security_group_id)
        request.set_InstanceType(instance_type)
        request.set_VSwitchId(vswitch_id)
        request.set_ZoneId(zone_id)
        request.set_InstanceChargeType('PostPaid')
        request.set_KeyPairName(ssh_keyname)
        request.set_InternetMaxBandwidthOut(1)
        response = self._send_request(request)
        instance_id = response.get('InstanceId')
        if instance_id is None:
            logger.info(response)
            raise Exception("Instance could not be created.")
        self.instance_id = instance_id
        logger.info("Instance %s created" % instance_id)

        logger.info("Wait for the instance to appear as stopped so we can continue")
        max_tries = 10
        status = None
        while max_tries > 0 and status != 'Stopped':
            max_tries -= 1
            time.sleep(5)
            status = self._get_instance_status_by_id(instance_id)
        if status != 'Stopped':
            raise Exception("VM %s not in desired state" % instance_id)

        logger.info("Allocating public ip for instance %s" % instance_id)
        request = AllocatePublicIpAddressRequest()
        request.set_InstanceId(instance_id)
        ip_address = self._send_request(request)
        logger.info("Public IP address asssigned to instance: %s" % ip_address)
        logger.info(json.dumps(ip_address, indent=4))

        logger.info("Starting instance %s" % instance_id)
        request = StartInstanceRequest()
        request.set_InstanceId(instance_id)
        self._send_request(request)

        # wait for instance to be started
        max_tries = 60
        status = "initial"
        while max_tries > 0 and status != 'Running':
            max_tries -= 1
            time.sleep(10)
            status = self._get_instance_status_by_id(instance_id)
            logger.info("Status is %s" % status)

        if status != 'Running':
            raise Exception("Instance %s status is %s: failed to start." %(instance_id, status))

        return (instance_id, ip_address)

    def _send_request(self, request):
        request.set_accept_format('json')
        # try:
        response_str = self.acs_client.do_action(request)
        logger.debug(response_str)
        response_detail = json.loads(response_str)
        return response_detail
        # except Exception as e:
        #    logger.error(e)
        #    return None

    def _get_instance_status_by_id(self, instance_id):
        request = DescribeInstancesRequest()
        request.set_InstanceIds(json.dumps([instance_id]))
        response = self._send_request(request)
        instance_detail = None
        if response is not None:
            instance_list = response.get('Instances').get('Instance')
            for item in instance_list:
                return item.get('Status')
        else:
            return None

    def _boot_image_bak(self, region_id, zone_id, image_id, instance_type, vswitch_id, instance_name, ssh_keyname):

        cmd = [
            "aliyun",
            "ecs",
            "CreateInstance",
            "--RegionId",
            region_id,
            "--ZoneId",
            zone_id,
            "--ImageId",
            image_id,
            "--InstanceType",
            instance_type,
            "--VSwitchId",
            vswitch_id,
            "--InstanceName",
            instance_name,
            "--InstanceChargeType",
            "PostPaid",
            "--KeyPairName",
            ssh_keyname,
            "--InternetMaxBandwidthOut"
            "1"
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, env=self.env, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to create vm %s" % result.stderr.decode('utf-8'))
        instance = json.loads(result.stdout)

        cmd = [
            "aliyun",
            "ecs",
            "AllocatePublicIpAddress",
            "--InstanceId",
            instance["InstanceId"]
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, env=self.env, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to attach public ip to vm %s" % result.stderr.decode('utf-8'))
        ipinfo = json.loads(result.stdout)

        cmd = [
            "aliyun",
            "ecs",
            "StartInstance",
            "--InstanceId",
            instance["InstanceId"]
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, env=self.env, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to to start vm %s" % result.stderr.decode('utf-8'))
        return (instance, ipinfo)

    def _delete_vm(self, id):
        request = DeleteInstanceRequest()
        request.set_InstanceId(id)
        request.set_Force(True)
        response = self._send_request(request)
