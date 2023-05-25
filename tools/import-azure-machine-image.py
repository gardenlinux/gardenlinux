#!/usr/bin/env python3

import argparse
import os
import json
import time
import logging
import dataclasses

from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient, SubscriptionClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.storage.blob import BlobClient

import azure.mgmt.compute.models as azcm

logger = logging.Logger(name=__name__, level=logging.INFO)


@dataclasses.dataclass
class AZCredentials:
    credential: object
    subscription_id: str


def with_tags(p: dict, tags: dict = None):
    if tags != None:
        p["tags"] = tags
    return p


def with_generated_default(
    value,
    prefix,
    with_uuid: bool = False,
    with_timestamp: bool = False,
    suffix: str = None,
    maxlen: int = 64,
):
    if value != None and len(value) > 0:
        return value

    if suffix != None:
        suffix = f"-{suffix}"
    else:
        suffix = ""

    full_prefix = f"{prefix}-gardenlinux-test-image"

    if with_uuid is True:
        import uuid

        uuidstr = str(uuid.uuid4())
        uuidlen = maxlen - len(f"{full_prefix}-{suffix}")
        return f"{full_prefix}-{uuidstr[0:uuidlen]}{suffix}"

    if with_timestamp is True:
        import time

        timestamp = time.strftime("%Y%m%d%H%M%S")
        suffixlen = maxlen - len(f"{full_prefix}-{timestamp}")
        return f"{full_prefix}-{timestamp}{suffix[0:suffixlen]}"

    rv = f"{full_prefix}{suffix}"
    if len(rv) > maxlen:
        rv = f"{full_prefix[0:maxlen-len(suffix)]}{suffix}"
    return rv


def azure_credentials(
    subscription_id: str = None, subscription_name: str = None
) -> AZCredentials:
    logger.debug(f"Searching for subscription ID for name {subscription_name}...")
    from azure.identity import (
        AzureCliCredential,
    )

    def find_subscription_id(credential, subscription_name: str) -> str:
        subscription_client = SubscriptionClient(credential)
        for sub in subscription_client.subscriptions.list():
            if sub.display_name == subscription_name:
                return sub.subscription_id
        raise RuntimeError(
            f"Cannot find a subscription with display name {subscription_name}"
        )

    if subscription_id == None and subscription_name == None:
        raise RuntimeError(
            "Need to provide either a subscription ID or a subscription name."
        )

    credential = AzureCliCredential()
    if subscription_id == None:
        if subscription_name == None:
            raise RuntimeError(
                "Must provide either subscription_id or subcription_name."
            )
        subscription_id = find_subscription_id(credential, subscription_name)

    logger.debug(f"Subscription ID for {subscription_name} is {subscription_id}")
    return AZCredentials(credential=credential, subscription_id=subscription_id)


def check_location_available(credentials: AZCredentials, location):
    logger.debug(
        f"Checking if location {location} is available to subscription {credentials.subscription_id}..."
    )
    sc = SubscriptionClient(credentials.credential)
    locations = [
        l.name for l in sc.subscriptions.list_locations(credentials.subscription_id)
    ]

    if location in locations:
        logger.debug(f"location {location} is available")
        return location
    else:
        raise RuntimeError(f"{location} is not available to your subsription")


class AzureImageBuild:
    def __init__(self, args):
        self.args = args
        self.logger = logger

        credentials = azure_credentials(
            subscription_id=args.subscription_id,
            subscription_name=args.subscription_name,
        )
        self.subscription = credentials.subscription_id
        self.location = check_location_available(credentials, args.location)

        if args.debug is True:
            self.logger.setLevel(logging.DEBUG)

        self.resource_group_name = with_generated_default(
            args.resource_group, "rg", with_timestamp=True
        )
        self.storage_account_name = f"sagl{time.strftime('%Y%m%d%H%M%S')}"
        self.gallery_name = with_generated_default(
            args.gallery_name, "gallery", with_timestamp=True, maxlen=80
        )
        self.hyper_v_generation = args.hyper_v_generation

        self.tags = []
        if args.tags != None:
            for i in args.tags:
                tag_split = i.split(":")
                if len(tag_split) != 2:
                    raise ValueError(
                        f"{i} is not a valid tag, must be in 'key:value' format"
                    )
                self.tags.append({tag_split[0]: tag_split[1]})

        self.cclient = ComputeManagementClient(
            credentials.credential, credentials.subscription_id
        )
        self.rclient = ResourceManagementClient(
            credentials.credential, credentials.subscription_id
        )
        self.sclient = StorageManagementClient(
            credentials.credential, credentials.subscription_id
        )

    def az_get_resource_group(self, name: str):
        self.logger.debug(f"Checking if resource group {name} already exists...")
        try:
            rg = self.rclient.resource_groups.get(resource_group_name=name)
            self.logger.debug(f"Resource group {name} already exists.")
            return rg
        except ResourceNotFoundError:
            return None

    def az_create_resource_group(self, name: str, location: str):
        self.logger.debug(f"Creating resource group {name}...")

        rg = self.rclient.resource_groups.create_or_update(
            resource_group_name=name,
            parameters=with_tags(
                {
                    "location": location,
                },
                self.tags,
            ),
        )

        return rg

    def az_get_storage_account(self, name: str):
        name = name.replace("-", "")
        self.logger.debug(
            f"Checking if storage account {name} in resource group {self._resourcegroup.name} already exists..."
        )
        try:
            stoacc = self.sclient.storage_accounts.get_properties(
                resource_group_name=self._resourcegroup.name,
                account_name=name,
            )
            self.logger.debug(
                f"Storage account {name} in resource group {self._resourcegroup.name} already exists."
            )
            return stoacc
        except ResourceNotFoundError:
            return None

    def az_create_storage_account(self, name: str):
        name = name.replace("-", "")
        self.logger.debug(
            f"Creating storage account {name} in resourcegroup {self._resourcegroup.name}..."
        )

        storage_account = self.sclient.storage_accounts.begin_create(
            resource_group_name=self._resourcegroup.name,
            account_name=name,
            parameters=with_tags(
                {
                    "sku": {
                        "name": "Standard_RAGRS",
                        "tier": "Standard",
                    },
                    "kind": "StorageV2",
                    "location": self._resourcegroup.location,
                    "allow_blob_public_access": False,
                    "enable_https_traffic_only": True,
                    "minimum_tls_version": "TLS1_2",
                },
                self.tags,
            ),
        )

        return storage_account.result()

    def upload_image_file(
        self, name: str, image_file_path: str, show_progress: bool = False
    ):
        def progress_function(total, uploaded):
            print(
                f"Uploaded {uploaded} of {total} bytes ({uploaded/total*100:.2f}%)",
                end="\r",
                flush=True,
            )

        self.logger.debug("Creating blob container in storage account...")
        try:
            self.sclient.blob_containers.create(
                resource_group_name=self._resourcegroup.name,
                account_name=self.storage_account_name,
                container_name="vhds",
                blob_container={"public_access": "None"},
            )
        except ResourceExistsError:
            pass

        storage_keys = self.sclient.storage_accounts.list_keys(
            resource_group_name=self._resourcegroup.name,
            account_name=self.storage_account_name,
        )
        keys = {v.key_name: v.value for v in storage_keys.keys}

        connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.storage_account_name};AccountKey={keys['key1']};EndpointSuffix=core.windows.net"
        blob_client = BlobClient.from_connection_string(
            conn_str=connection_string,
            container_name="vhds",
            blob_name=f"{name}.vhd",
        )

        chunksize = 4 * 1024 * 1024
        offset = 0

        file_size = os.path.getsize(image_file_path)
        blob_client.create_page_blob(file_size)
        self.logger.debug(
            f"Uploading {image_file_path} ({file_size} bytes) - this may take a while..."
        )

        with open(image_file_path, "rb") as f:
            while offset < file_size:
                # refer to https://docs.microsoft.com/en-us/azure/storage/blobs/storage-blob-pageblob-overview?tabs=dotnet#writing-pages-to-a-page-blob
                # for sparse file upload logic and requirements for offset alignments
                offset = (f.seek(offset, os.SEEK_DATA) // chunksize) * chunksize
                f.seek(offset, os.SEEK_SET)

                data = f.read(chunksize)
                remaining = file_size - offset
                actual_cp_bytes = min(chunksize, remaining)

                blob_client.upload_page(
                    page=data,
                    offset=offset,
                    length=actual_cp_bytes,
                )
                offset += actual_cp_bytes
                if show_progress:
                    progress_function(total=file_size, uploaded=offset)

        image_uri = (
            f"https://{self.storage_account_name}.blob.core.windows.net/vhds/{name}.vhd"
        )

        image = self.cclient.images.begin_create_or_update(
            resource_group_name=self._resourcegroup.name,
            image_name=name,
            parameters=with_tags(
                {
                    "location": self._resourcegroup.location,
                    "hyper_v_generation": self.hyper_v_generation,
                    "storage_profile": {
                        "os_disk": {
                            "os_type": azcm.OperatingSystemType.LINUX,
                            "os_state": azcm.OperatingSystemStateTypes.GENERALIZED,
                            "blob_uri": image_uri,
                            "caching": azcm.CachingTypes.READ_WRITE,
                            "storage_account_type": azcm.StorageAccountTypes.STANDARD_SSD_LRS,
                        }
                    },
                },
                self.tags,
            ),
        )

        return image.result()

    def az_get_image_gallery(self, name: str):
        self.logger.debug(
            f"Checking if image gallery {name} in resource group {self._resourcegroup.name} already exists..."
        )
        try:
            gallery = self.cclient.galleries.get(
                resource_group_name=self._resourcegroup.name, gallery_name=name
            )
            self.logger.debug(
                f"Image gallery {name} in resource group {self._resourcegroup.name} already exists."
            )
            return gallery
        except ResourceNotFoundError:
            return None

    def az_create_image_gallery(self, name: str, community_gallery: bool = False):
        name = name.replace("-", "_")
        self.logger.debug(
            f"Creating image gallery {name} in resource group {self._resourcegroup.name} with {community_gallery=}"
        )

        gallery = azcm.Gallery(
            location=self._resourcegroup.location,
            description="image gallery for publishing Garden Linux test images",
        )

        if community_gallery is True:
            gallery.sharing_profile = azcm.SharingProfile(
                permissions=azcm.GallerySharingPermissionTypes.COMMUNITY,
                community_gallery_info=azcm.CommunityGalleryInfo(
                    publisher_uri="www.gardenlinux.io",
                    publisher_contact="info@gardenlinux.io",
                    eula="MIT License",
                    public_name_prefix="gardenlinux-test",
                ),
            )

        gallery = self.cclient.galleries.begin_create_or_update(
            resource_group_name=self._resourcegroup.name,
            gallery_name=name,
            gallery=gallery,
        ).result()

        if community_gallery is True:
            self.logger.debug(f"Enabling community sharing on image gallery {name}...")
            self.cclient.gallery_sharing_profile.begin_update(
                resource_group_name=self._resourcegroup.name,
                gallery_name=name,
                sharing_update=azcm.SharingUpdate(
                    operation_type=azcm.SharingUpdateOperationTypes.ENABLE_COMMUNITY,
                ),
            )

        return gallery

    def az_get_gallery_image_definition(self, name: str):
        self.logger.debug(
            f"Checking if gallery image definition {name} in gallery {self._image_gallery.name} already exists..."
        )
        try:
            gallery_image_definition = self.cclient.gallery_images.get(
                resource_group_name=self._resourcegroup.name,
                gallery_name=self._image_gallery.name,
                gallery_image_name=name,
            )
            self.logger.debug(
                f"Image gallery definition {name} in gallery {self._image_gallery.name} already exists."
            )
            return gallery_image_definition
        except ResourceNotFoundError:
            return None

    def az_create_gallery_image_definition(self, name: str):
        self.logger.debug(
            f"Creating gallery image definition {name} in image gallery {self._image_gallery.name}..."
        )

        image_definition = self.cclient.gallery_images.begin_create_or_update(
            resource_group_name=self._resourcegroup.name,
            gallery_name=self._image_gallery.name,
            gallery_image_name=name,
            gallery_image=azcm.GalleryImage(
                location=self._resourcegroup.location,
                os_type=azcm.OperatingSystemType.LINUX,
                os_state=azcm.OperatingSystemStateTypes.GENERALIZED,
                hyper_v_generation=self.hyper_v_generation,
                architecture=self.args.architecture,
                identifier=azcm.GalleryImageIdentifier(
                    publisher="GardenLinux", offer="gardenlinux", sku="gardenlinux"
                ),
            ),
        )

        return image_definition.result()

    def az_get_gallery_image_version(self, version: str):
        self.logger.debug(
            f"Checking if gallery image version {version} for gallery definition {self._image_definition.name} already exists..."
        )
        try:
            gallery_image_definition = self.cclient.gallery_image_versions.get(
                resource_group_name=self._resourcegroup.name,
                gallery_name=self._image_gallery.name,
                gallery_image_name=self._image_definition.name,
                gallery_image_version_name=version,
            )
            self.logger.debug(
                f"Image gallery version {version} with gallery image definition {self._image_definition.name} in gallery {self._image_gallery.name} and resource group {self._resourcegroup.name} already exists."
            )
            return gallery_image_definition
        except ResourceNotFoundError:
            return None

    def az_create_gallery_image_version(self, version: str, image_id: str):
        self.logger.debug(
            f"Creating image version {version} for image {image_id} and gallery definition {self._image_definition.name}..."
        )
        image_version = self.cclient.gallery_image_versions.begin_create_or_update(
            resource_group_name=self._resourcegroup.name,
            gallery_name=self._image_gallery.name,
            gallery_image_name=self._image_definition.name,
            gallery_image_version_name=version,
            gallery_image_version=azcm.GalleryImageVersion(
                location=self._resourcegroup.location,
                tags=self.tags,
                publishing_profile=azcm.GalleryImageVersionPublishingProfile(
                    replica_count=1,
                    exclude_from_latest=False,
                    storage_account_type=azcm.StorageAccountType.STANDARD_LRS,
                    replication_mode=azcm.ReplicationMode.SHALLOW,
                ),
                storage_profile=azcm.GalleryImageVersionStorageProfile(
                    source=azcm.GalleryArtifactVersionFullSource(id=image_id)
                ),
                safety_profile=azcm.GalleryImageVersionSafetyProfile(),
            ),
        )

        return image_version.result()

    def run(self):
        image_path = self.args.image_path
        if not os.path.exists(image_path) or not os.path.isfile(image_path):
            raise RuntimeError(f"{image_path} does not exist or is not a file")
        if not image_path.lower().endswith(".vhd"):
            raise RuntimeError(
                f"{image_path} must be a .vhd file (and thus must end with .vhd)"
            )

        # check and/or create resource group
        self._resourcegroup = self.az_get_resource_group(name=self.resource_group_name)
        if self._resourcegroup == None:
            self._resourcegroup = self.az_create_resource_group(
                name=self.resource_group_name, location=self.location
            )

        self._storageaccount = self.az_get_storage_account(
            name=self.storage_account_name
        )
        if self._storageaccount == None:
            self._storageaccount = self.az_create_storage_account(
                name=self.storage_account_name
            )

        image = self.upload_image_file(
            name=self.args.image_name,
            image_file_path=image_path,
            show_progress=not self.args.no_show_progress,
        )

        self._image_gallery = self.az_get_image_gallery(name=self.gallery_name)
        if self._image_gallery == None:
            self._image_gallery = self.az_create_image_gallery(
                name=self.gallery_name, community_gallery=self.args.community_gallery
            )

        self._image_definition = self.az_get_gallery_image_definition(
            name=self.args.image_name
        )
        if self._image_definition == None:
            self._image_definition = self.az_create_gallery_image_definition(
                name=self.args.image_name
            )

        self._image_version = self.az_get_gallery_image_version(version=self.args.image_version)
        if self._image_version == None:
            self._image_version = self.az_create_gallery_image_version(
                version=self.args.image_version, image_id=image.id
            )

        result_info = {
            "subscription": self.subscription,
            "resource_group": self._resourcegroup.as_dict(),
            "storage_account": self._storageaccount.as_dict(),
            "image": image.as_dict(),
            "image_gallery": self._image_gallery.as_dict(),
            "image_definition": self._image_definition.as_dict(),
            "image_version": self._image_version.as_dict(),
        }

        print(json.dumps(result_info, indent=4))

    @classmethod
    def _argparse_register(cls, parser):
        parser.add_argument(
            "--location",
            type=str,
            dest="location",
            help="the Azure location all resources should be created in",
            required=True,
        )
        parser.add_argument(
            "--resource-group",
            type=str,
            dest="resource_group",
            help="Name of the resource group to use - leave empty to use a generated name",
        )
        parser.add_argument(
            "--storage-account-name",
            type=str,
            dest="storage_account_name",
            help="Name of the storage accont to use - leave empty to use a generated name",
        )
        parser.add_argument(
            "--image-name",
            type=str,
            dest="image_name",
            help="Name of the image that gets uploaded",
            required=True,
        )
        parser.add_argument(
            "--image-version",
            type=str,
            dest="image_version",
            help="Version of the image that gets uploaded",
            required=True,
        )
        parser.add_argument(
            "--gallery-name",
            type=str,
            dest="gallery_name",
            help="Name of the image gallery to which the image gets published - leave empty to use a generated name",
        )
        parser.add_argument(
            "--community-gallery",
            type=bool,
            dest="community_gallery",
            help="Make the image available through a community image gallery",
        )
        parser.add_argument(
            "--subscription-id",
            type=str,
            dest="subscription_id",
            help="Azure subscription ID",
        )
        parser.add_argument(
            "--architecture",
            type=str,
            choices=["x64", "Arm64"],
            default="x64",
            dest="architecture",
            help="CPU architecture",
        )
        parser.add_argument(
            "--hyper-v-generation",
            type=str,
            choices=["V1", "V2"],
            default="V1",
            dest="hyper_v_generation",
            help="HyperV Generation",
        )
        parser.add_argument(
            "--subscription-name",
            type=str,
            dest="subscription_name",
            help="Azure subscription name",
        )
        parser.add_argument(
            "--no-show-progress",
            default=False,
            action="store_true",
            dest="no_show_progress",
            help="Show upload progress",
        )
        parser.add_argument(
            "--debug",
            default=False,
            dest="debug",
            action="store_true",
            help="Verbose debug output",
        )
        parser.add_argument(
            "--tag",
            nargs="+",
            action="append",
            dest="tags",
            help="tag to add to all resources (multiple tags can be added)",
        )
        parser.add_argument(
            "image_path",
            type=str,
            help="The image file to be uploaded to Azure.",
        )

    @classmethod
    def _main(cls):
        parser = argparse.ArgumentParser()
        cls._argparse_register(parser)
        args = parser.parse_args()
        print(args)

        azure_img_build = AzureImageBuild(args)
        azure_img_build.run()


if __name__ == "__main__":
    AzureImageBuild._main()
