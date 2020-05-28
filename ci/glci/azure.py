import json
import requests

import botocore.client

import glci.model

from datetime import (
    datetime,
    timedelta,
)

from msal import ConfidentialClientApplication

from azure.storage.blob import (
    BlobClient,
    BlobType,
    ContainerSasPermissions,
    generate_container_sas,
)

import ci.util


class AzureImageStore:
    """Azure Image Store backed by an container in an Azure Storage Account."""

    def __init__(
        self,
        storage_account_name: str,
        storage_account_key: str,
        container_name: str
    ):
        self.sa_name = storage_account_name
        self.sa_key = storage_account_key
        self.container_name = container_name

    def copy_from_s3(
        self,
        s3_client,
        s3_bucket_name: str,
        s3_object_key: str,
        target_blob_name: str
    ):
        """Copy an object from Amazon S3 to an Azure Storage Account

        This will overwrite the contents of the target file if it already exists.
        """
        connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={self.sa_name};"
            f"AccountKey={self.sa_key};"
            "EndpointSuffix=core.windows.net"
        )
        image_blob = BlobClient.from_connection_string(
            conn_str=connection_string,
            container_name=self.container_name,
            blob_name=target_blob_name,
            blob_type=BlobType.PageBlob,
        )

        file_size = _get_s3_object_file_size(s3_client, s3_bucket_name, s3_object_key)
        url = _get_public_s3_url(s3_client, s3_bucket_name, s3_object_key)

        image_blob.create_page_blob(file_size)
        # max size we can copy in one go is 4 mebibytes. Split the upload in steps with max size of
        # 4 MiB
        copy_step_length = 4 * 1024 * 1024
        offset = 0
        while offset < file_size:
            remaining = file_size - offset
            image_blob.upload_pages_from_url(
                source_url=url,
                offset=offset,
                length=min(copy_step_length, remaining),
                source_offset=offset,
            )
            offset += copy_step_length

    def get_image_url(self, image_name: str):
        """Generate an url including sas token to access image in the store."""
        container_sas = generate_container_sas(
            account_name=self.sa_name,
            account_key=self.sa_key,
            container_name=self.container_name,
            permission=ContainerSasPermissions(read=True, list=True),
            start=datetime.utcnow() - timedelta(days=1),
            expiry=datetime.utcnow() + timedelta(days=30)
        )
        return f"https://{self.sa_name}.blob.core.windows.net/{self.container_name}/{image_name}?{container_sas}"


class AzureMarketplaceClient:
    """Azure Marketplace Client is a client to interact with the Azure Marketplace."""

    def __init__(self, spn_tenant_id: str, spn_client_id: str, spn_client_secret: str):
        app_client = ConfidentialClientApplication(
            spn_client_id,
            authority=f"https://login.microsoftonline.com/{spn_tenant_id}",
            client_credential=spn_client_secret
        )
        token = app_client.acquire_token_for_client(scopes="https://cloudpartner.azure.com/.default")
        self.req_headers = {
            "Authorization": f"Bearer {token['access_token']}",
            "Content-Type": "application/json",
        }
        self.req_params = {
            "api-version": "2017-10-31"
        }

    def fetch_offer(self, publisher_id: str, offer_id: str):
        """Fetch an offer from Azure marketplace."""
        response = requests.get(
            f"https://cloudpartner.azure.com/api/publishers/{publisher_id}/offers/{offer_id}",
            headers=self.req_headers,
            params=self.req_params
        )
        if not response.ok:
            raise RuntimeError(
                "Fetching of Azure marketplace offer for gardenlinux failed. "
                f"statuscode={response.status_code}"
            )
        offer_spec = response.json()
        response.close()
        return offer_spec

    def update_offer(self, publisher_id: str, offer_id: str, spec: dict):
        """Update an offer with a give spec."""
        headers = self.req_headers.copy()
        headers.update({
            "If-Match": "*",
        })
        response = requests.put(
            f"https://cloudpartner.azure.com/api/publishers/{publisher_id}/offers/{offer_id}",
            headers=headers,
            params=self.req_params,
            json=spec,
        )
        if not response.ok:
            raise RuntimeError(
                "Update of Azure marketplace offer for gardenlinux failed. "
                f"statuscode={response.status_code}"
            )
        response.close()

    def publish_offer(self, publisher_id: str, offer_id: str, notification_mails):
        """Trigger (re-)publishing of an offer."""
        data = {
            "metadata": {
                "notification-emails": ",".join(notification_mails)
            }
        }
        response = requests.post(
            f"https://cloudpartner.azure.com/api/publishers/{publisher_id}/offers/{offer_id}/publish",
            headers=self.req_headers,
            params=self.req_params,
            json=data,
        )
        if not response.ok:
            raise RuntimeError(
                "Can't publish updated Azure marketplace offer for "
                f"gardenlinux. statuscode={response.status_code}"
            )
        response.close()


def add_image_version_to_plan(spec: dict, plan_id: str, image_version: str, image_url: str):
    """Add a new image version to a given plan and return a modified offer spec."""

    plan_spec = {}
    for plan in spec["definition"]["plans"]:
        if plan["planId"] == plan_id:
            plan_spec = plan

    if not plan_spec:
        raise RuntimeError(f"Plan {plan_id} not found in offer {spec['id']}.")

    plan_spec["microsoft-azure-virtualmachines.vmImages"][image_version] = {
        "osVhdUrl": image_url,
        "lunVhdDetails": []
    }
    return spec


def remove_image_version_from_plan(spec: dict, plan_id: str, image_version: str, image_url: str):
    """remove an image version from a given plan and return a modified offer spec."""

    plan_spec = {}
    for plan in spec["definition"]["plans"]:
        if plan["planId"] == plan_id:
            plan_spec = plan

    if not plan_spec:
        raise RuntimeError(f"Plan {plan_id} not found in offer {spec['id']}.")

    del plan_spec["microsoft-azure-virtualmachines.vmImages"][image_version]

    return spec


def _get_public_s3_url(s3_client, bucket_name, key):
    return s3_client.generate_presigned_url(
        'get_object',
        ExpiresIn=0,
        Params={'Bucket': bucket_name, 'Key': key},
    )


def _get_s3_object_file_size(s3_client, bucket_name, key):
    response = s3_client.head_object(Bucket=bucket_name, Key=key)
    return response['ContentLength']


def copy_image(
    storage_account_config,
    bucket_name,
    object_key,
    target_blob_name,
    s3_client,
):
    ''' copy object from s3 to storage account and return the generated access url including SAS token
    for the blob
    '''
    if not target_blob_name.endswith('.vhd'):
        print(
            f"Destination image name '{target_blob_name}' does not end with '.vhd'! Resulting blob will "
            "not be suitable to create a marketplace offer from it!"
        )

    store = AzureImageStore(
        storage_account_config.storage_account_name(),
        storage_account_config.access_key(),
        storage_account_config.container_name(),
    )

    store.copy_from_s3(
        s3_client=s3_client,
        s3_bucket_name=bucket_name,
        s3_object_key=object_key,
        target_blob_name=target_blob_name,
    )

    return store.get_image_url(target_blob_name)


def update_offer(
    service_principal_config,
    plan_config,
    image_version,
    image_url,
    notification_recipients,
):

    marketplace_client = AzureMarketplaceClient(
        service_principal_config.tenant_id(),
        service_principal_config.client_id(),
        service_principal_config.client_secret(),
    )

    publisher_id = plan_config.publisher_id()
    offer_id = plan_config.offer_id()
    plan_id = plan_config.plan_id()

    offer_spec = marketplace_client.fetch_offer(publisher_id, offer_id)

    # Add new image version to plan in the offer spec.
    modified_offer_spec = add_image_version_to_plan(offer_spec, plan_id, image_version, image_url)

    # Update the marketplace offer.
    marketplace_client.update_offer(publisher_id, offer_id, modified_offer_spec)

    marketplace_client.publish_offer(
        plan_config.publisher_id(),
        plan_config.offer_id(),
        notification_recipients,
    )


def copy_image_and_publish_offer(
    mk_session: callable,
    build_cfg: glci.model.BuildCfg,
    release: glci.model.OnlineReleaseManifest,
):
    '''Copies an object from S3 to an Azure Storage Account and adds it as machine image to the
    given Plan.
    '''
    cfg_factory = ci.util.ctx().cfg_factory()
    service_principal_config = cfg_factory.service_principal(
        build_cfg.service_principal_name
    )
    storage_account_config = cfg_factory.azure_storage_account(
        build_cfg.storage_account_config_name
    )
    plan_config = cfg_factory.azure_plan(build_cfg.plan_config_name)

    session = mk_session(region_name=build_cfg.aws_region)
    config = botocore.client.Config(signature_version=botocore.UNSIGNED)
    s3_client = session.client('s3', config=config)

    target_blob_name = f"gardenlinux-az-{release.version}.vhd"

    image_url = copy_image(
        storage_account_config=storage_account_config,
        s3_client=s3_client,
        bucket_name=release.s3_bucket,
        object_key=release.path_by_suffix('rootfs.raw').rel_path,
        target_blob_name=target_blob_name,
    )

    update_offer(
        service_principal_config=service_principal_config,
        plan_config=plan_config,
        image_version=release.version,
        image_url=image_url,
        notification_recipients=build_cfg.notification_recipients,
    )
