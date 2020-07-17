import oss2
import os
import datetime
import tempfile
import json
import time
import enum
import logging
import dataclasses
import glci.model
from aliyunsdkecs.request.v20140526 import ImportImageRequest
from aliyunsdkecs.request.v20140526 import DescribeImagesRequest
from aliyunsdkecs.request.v20140526 import DeleteImageRequest
from aliyunsdkecs.request.v20140526 import DescribeRegionsRequest
from aliyunsdkecs.request.v20140526 import CopyImageRequest
from aliyunsdkecs.request.v20140526 import ModifyImageSharePermissionRequest
from aliyunsdkcore.client import AcsClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
TIME_OUT = 30 * 60  # in seconds, 30 Minutes


class AlicloudImageStatus(enum.Enum):
    CREATING = "Creating"
    WAITING = "Waiting"
    AVAILABLE = "Available"
    UNAVAILABLE = "UnAvailable"
    CREATEFAILED = "CreateFailed"

    def __str__(self):
        return self.value

    @staticmethod
    def to_availbel_str_array() -> []:
        return [v.value for v in AlicloudImageStatus]

class ImageShareOption(enum.Enum):
    SHARE = "HIDDEN"
    UNSHARE = "PRIVATE"
    def __str__(self):
        return self.value

class AlicloudImageMaker:
    def __init__(
        self,
        oss2_auth: oss2.Auth,
        acs_client: AcsClient,
        release: glci.model.OnlineReleaseManifest,
        build_cfg: glci.model.BuildCfg,
    ):
        self.oss2_auth = oss2_auth
        self.acs_client = acs_client
        self.release = release
        self.build_cfg = build_cfg
        self.image_oss_key = f"gardenlinux-{self.release.version}.qcow2"
        self.region = build_cfg.alicloud_region
        self.bucket_name = build_cfg.oss_bucket_name
        self.image_name = f"gardenlinux-{self.release.canonical_release_manifest_key_suffix()}"

    # copy image from S3 to OSS
    def cp_image_from_s3(self, s3_client):
        s3_bucket_key = self.release.path_by_suffix("rootfs.qcow2").s3_key
        s3_bucket_name = self.release.path_by_suffix(
            "rootfs.qcow2").s3_bucket_name
        try:
            tmp_file = tempfile.mktemp()
            logger.info(
                f"downloading image from s3 {s3_bucket_name}/{s3_bucket_key} to temp file {tmp_file}"
            )
            s3_client.download_file(
                Bucket=s3_bucket_name,
                Key=s3_bucket_key,
                Filename=tmp_file,
            )
            logger.info(
                f"downloaded image from s3 {s3_bucket_name}/{s3_bucket_key}")

            logger.info(
                f"uploading image to oss {self.bucket_name} {self.image_oss_key} in region {self.region}"
            )
            bucket = oss2.Bucket(
                self.oss2_auth,
                f"http://oss-{self.region}.aliyuncs.com",
                self.bucket_name,
            )
            bucket.put_object_from_file(self.image_oss_key, tmp_file)
            logger.info(
                f"uploaded image to oss {self.bucket_name} {self.image_oss_key=}"
            )
        finally:
            os.unlink(tmp_file)
            logger.info(f"temp file {tmp_file} is removed")

    # Import image from OSS and then copy it to other regions
    def make_image(self) -> glci.model.OnlineReleaseManifest:
        image_id = self.import_image()
        other_regions = self._list_regions()
        logger.info(f"begin to copy image to regsions {other_regions}")
        region_image_map = {}
        for region in other_regions:
            region_image_map[region] = self.copy_image(image_id, region)

        for k, v in region_image_map.items():
            self._wait_for_image(k, v)
            logger.info(f"finished copying image {v} to region {k}")

        region_image_map[self.region] = image_id

        self._share_images(region_image_map)

        # make release manifest
        published_images = tuple((glci.model.AlicloudPublishedImage(
            image_id=image_id,
            region_id=region,
            image_name=self.image_name,
        ) for region, image_id in region_image_map.items()))
        published_image_set = glci.model.AlicloudPublishedImageSet(
            published_alicloud_images=published_images)

        return dataclasses.replace(
            self.release, published_image_metadata=published_image_set)

    # Share image in a hidden way. The account should apply for whitelist
    def _share_images(self, region_image_map: dict):
        for region, image_id in region_image_map.items():
            self.acs_client.set_region_id(region)
            logger.info(
                f"share image ({region}/{image_id}) as a hidden image"
            )
            req = ModifyImageSharePermissionRequest.ModifyImageSharePermissionRequest()
            req.set_ImageId(image_id)
            req.set_LaunchPermission(str(ImageShareOption.SHARE))
            self.acs_client.do_action_with_exception(req)

        self.acs_client.set_region_id(self.region)

    # delete images
    def delete_images(self, region_image_map: dict):
        for region, image_id in region_image_map.items():
            self.acs_client.set_region_id(region)
            logger.info(
                f"delete image ({region}/{image_id})"
            )
            req = ModifyImageSharePermissionRequest.ModifyImageSharePermissionRequest()
            req.set_ImageId(image_id)
            req.set_LaunchPermission(str(ImageShareOption.UNSHARE))
            self.acs_client.do_action_with_exception(req)

            req = DeleteImageRequest.DeleteImageRequest()
            req.set_ImageId(image_id)
            self.acs_client.do_action_with_exception(req)

        self.acs_client.set_region_id(self.region)

    # Import image from oss. Returns image id
    def import_image(self) -> str:
        exist, image_id = self._check_image_existance(self.region,
                                                      self.image_name)
        if exist:
            logger.warn(
                f"found image {self.image_name} already exists in region {self.region}, the id is {image_id}, skip importing"
            )
            self._wait_for_image(self.region, image_id)
        else:
            logger.info(
                f"importing image {self.image_name} in region {self.region}")
            req = ImportImageRequest.ImportImageRequest()
            req.set_Description(self.image_name)
            req.set_Platform("Others Linux")
            req.set_ImageName(self.image_name)
            devMap = [{
                "OSSBucket": self.bucket_name,
                "DiskImageSize": "20",
                "Format": "qcow2",
                "OSSObject": self.image_oss_key,
            }]
            req.set_DiskDeviceMappings(devMap)
            logger.info(f"dev: {devMap}")
            response = parse_response(
                self.acs_client.do_action_with_exception(req))
            image_id = response.get("ImageId")
            logger.info(
                f"importing job {self.image_name}[{self.region}/{image_id}] is submitted. Waiting for processed"
            )
            self._wait_for_image(self.region, image_id)
            logger.info(
                f"finished importing image {self.image_name} in region {self.region}"
            )

        return image_id

    # tries to find all images with specified region and name.
    # If found, return the first found image_id
    def _check_image_existance(self, region, image_name) -> (bool, str):
        req = DescribeImagesRequest.DescribeImagesRequest()
        req.set_ImageName(image_name)
        req.set_Status(",".join(AlicloudImageStatus.to_availbel_str_array()))

        self.acs_client.set_region_id(region)
        response = parse_response(
            self.acs_client.do_action_with_exception(req))
        count = response.get("TotalCount")
        self.acs_client.set_region_id(self.region)

        if count == 0:
            return False, ""

        return True, response.get("Images").get("Image")[0].get("ImageId")

    ####
    def _wait_for_image(self, region, image_id):
        start_time = datetime.datetime.now()
        req = DescribeImagesRequest.DescribeImagesRequest()
        req.set_ImageId(image_id)
        req.set_Status(",".join(AlicloudImageStatus.to_availbel_str_array()))
        self.acs_client.set_region_id(region)
        while True:
            elapse = datetime.datetime.now() - start_time
            if elapse.seconds > TIME_OUT:
                raise Exception(f"Time out to wait image {image_id} be ready")
            response = parse_response(
                self.acs_client.do_action_with_exception(req))

            if response.get("Images").get("Image")[0].get("Status") == str(
                    AlicloudImageStatus.AVAILABLE):
                break

            logger.info(
                f"Image {image_id} ({region}) is not ready, will check it 10 senconds later"
            )
            time.sleep(10)

        self.acs_client.set_region_id(self.region)

    #####
    def _list_regions(self) -> []:
        req = DescribeRegionsRequest.DescribeRegionsRequest()
        response = parse_response(
            self.acs_client.do_action_with_exception(req))
        region_ids = []

        for region in response.get("Regions").get("Region"):
            region_id = region.get("RegionId")
            if region_id != self.region:
                region_ids.append(region_id)

        return region_ids

    ####
    def copy_image(self, src_image_id: str, dest_region: str) -> str:
        exist, image_id = self._check_image_existance(dest_region,
                                                      self.image_name)
        if exist:
            logger.warn(
                f"found image {self.image_name} already exists in region {dest_region}, id is {image_id} skip copying"
            )
        else:
            req = CopyImageRequest.CopyImageRequest()
            req.set_DestinationDescription(self.image_name)
            req.set_DestinationImageName(self.image_name)
            req.set_ImageId(src_image_id)
            req.set_DestinationRegionId(dest_region)
            logger.info(
                f"start to copy image {src_image_id} to region {dest_region}")
            response = parse_response(
                self.acs_client.do_action_with_exception(req))
            image_id = response.get("ImageId")
            logger.info(
                f"copying image {self.image_name} in region {dest_region} is in process, waiting for success"
            )
        return image_id


def parse_response(response):
    return json.loads(response)
