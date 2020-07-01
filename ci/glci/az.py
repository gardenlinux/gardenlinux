import requests
import dataclasses

from enum import Enum
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

import glci.model


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

        file_size_response = s3_client.head_object(Bucket=s3_bucket_name, Key=s3_object_key)
        file_size = file_size_response['ContentLength']

        url = s3_client.generate_presigned_url(
            'get_object',
            ExpiresIn=0,
            Params={'Bucket': s3_bucket_name, 'Key': s3_object_key},
        )

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


class AzmpOperationState(Enum):
    NOTSTARETD = "notStarted"
    RUNNING = "running"
    COMPLETED = "completed"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

class AzmpTransportDest(Enum):
    STAGING = "staging"
    PROD = "production"

class AzureMarketplaceClient:
    """Azure Marketplace Client is a client to interact with the Azure Marketplace."""

    marketplace_baseurl = "https://cloudpartner.azure.com/api/publishers"

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

    def _api_url(self, *parts):
        url_parts = "/".join(p for p in parts)
        return f"{self.marketplace_baseurl}/{url_parts}"

    def fetch_offer(self, publisher_id: str, offer_id: str):
        """Fetch an offer from Azure marketplace."""

        response = requests.get(
            self._api_url(publisher_id, "offers", offer_id),
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
            self._api_url(publisher_id, "offers", offer_id),
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
            self._api_url(publisher_id, "offers", offer_id, "publish"),
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

    def fetch_ongoing_operation_id(self, publisher_id: str, offer_id: str, transport_dest: AzmpTransportDest):
        '''Fetches the id of an ongoing Azure Marketplace transport operation to a certain transport destination.'''

        response = requests.get(
            self._api_url(publisher_id, "offers", offer_id, "submissions"),
            headers=self.req_headers,
            params=self.req_params,
        )
        if not response.ok:
            raise RuntimeError("Could not fetch Azure Marketplace transport operations for gardenlinux offer.")
        operations = response.json()
        response.close()
        for operation in operations:
            if AzmpTransportDest(operation["slot"]) == transport_dest and AzmpOperationState(operation["submissionState"]) == AzmpOperationState.RUNNING:
                return operation["id"]
        raise RuntimeError(f"Did not find an ongoing transport operation to ship gardenliunx offer on the Azure Marketplace.")

    def fetch_operation_state(self, publisher_id: str, offer_id: str, operation_id: str):
        """Fetches the state of a given Azure Marketplace transport operation."""

        response = requests.get(
            self._api_url(publisher_id, "offers", offer_id, "operations", operation_id),
            headers=self.req_headers,
            params=self.req_params,
        )
        if not response.ok:
            raise RuntimeError(f"Can't fetch state for transport operation {operation_id}. statuscode={response.status_code}")
        operation = response.json()
        response.close()
        return AzmpOperationState(operation['status'])

    def go_live(self, publisher_id: str, offer_id: str):
        """Trigger a go live operation to transport an Azure Marketplace offer to production."""

        response = requests.post(
            self._api_url(publisher_id, "offers", offer_id, "golive"),
            headers=self.req_headers,
            params=self.req_params,
        )
        if not response.ok:
            raise RuntimeError(
                    "Go live of updated gardenlinux Azure Marketplace offer failed."
                    f"statuscode={response.status_code}"
                )


def add_image_version_to_plan(
    spec: dict,
    plan_id: str,
    image_version: str,
    image_url: str
):
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


def generate_urn(marketplace_cfg: glci.model.AzureMarketplaceCfg, image_version: str):
    return f"{marketplace_cfg.publisher_id}:{marketplace_cfg.offer_id}:{marketplace_cfg.plan_id}:{image_version}"


def copy_image_from_s3_to_az_storage_account(
    storage_account_cfg: glci.model.AzureStorageAccountCfg,
    s3_bucket_name: str,
    s3_object_key,
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
        storage_account_cfg.name,
        storage_account_cfg.access_key,
        storage_account_cfg.container_name,
    )

    store.copy_from_s3(
        s3_client=s3_client,
        s3_bucket_name=s3_bucket_name,
        s3_object_key=s3_object_key,
        target_blob_name=target_blob_name,
    )

    return store.get_image_url(target_blob_name)


def update_and_publish_marketplace_offer(
    service_principal_cfg: glci.model.AzureServicePrincipalCfg,
    marketplace_cfg: glci.model.AzureMarketplaceCfg,
    image_version,
    image_url,
    notification_recipients,
):

    marketplace_client = AzureMarketplaceClient(
        service_principal_cfg.tenant_id,
        service_principal_cfg.client_id,
        service_principal_cfg.client_secret,
    )

    publisher_id = marketplace_cfg.publisher_id
    offer_id = marketplace_cfg.offer_id
    plan_id = marketplace_cfg.plan_id

    offer_spec = marketplace_client.fetch_offer(
        publisher_id=publisher_id,
        offer_id=offer_id,
    )

    # Add new image version to plan in the offer spec.
    modified_offer_spec = add_image_version_to_plan(
        spec=offer_spec,
        plan_id=plan_id,
        image_version=image_version,
        image_url=image_url,
    )

    # Update the marketplace offer.
    marketplace_client.update_offer(
        publisher_id=publisher_id,
        offer_id=offer_id,
        spec=modified_offer_spec,
    )

    marketplace_client.publish_offer(
        publisher_id=publisher_id,
        offer_id=offer_id,
        notification_mails=notification_recipients,
    )

    publish_operation_id = marketplace_client.fetch_ongoing_operation_id(
        publisher_id,
        offer_id,
        AzmpTransportDest.STAGING,
    )
    return publish_operation_id


def check_offer_transport_state(
    cicd_cfg: glci.model.CicdCfg,
    release: glci.model.OnlineReleaseManifest,
) -> glci.model.OnlineReleaseManifest:
    """Checks the state of the gardenlinux Azure Marketplace offer transport

    In case the transport to staging enviroment has been succeeded then the transport
    to production (go live) will be automatically triggered.
    """

    transport_state = release.published_image_metadata.transport_state
    if transport_state == "released":
        return release

    marketplace_client = AzureMarketplaceClient(
        spn_tenant_id=cicd_cfg.publish.azure.service_principal.tenant_id,
        spn_client_id=cicd_cfg.publish.azure.service_principal.client_id,
        spn_client_secret=cicd_cfg.publish.azure.service_principal.client_secret,
    )

    publisher_id = cicd_cfg.publish.azure.marketplace.publisher_id
    offer_id = cicd_cfg.publish.azure.marketplace.offer_id

    operation_status = marketplace_client.fetch_operation_state(
        publisher_id=publisher_id,
        offer_id=offer_id,
        operation_id=release.published_image_metadata.publish_operation_id,
    )

    # Check first if the process has been failed.
    if operation_status == AzmpOperationState.FAILED:
        published_image = glci.model.AzurePublishedImage(
            transport_state="failed",
            publish_operation_id=release.published_image_metadata.publish_operation_id,
        )
        if release.published_image_metadata.transport_state == "going_live":
            published_image.golive_operation_id = release.published_image_metadata.golive_operation_id
        return dataclasses.replace(release, published_image_metadata=published_image)

    # Publish completed. Trigger go live to transport the offer changes to production.
    if transport_state == "publishing" and operation_status == AzmpOperationState.SUCCEEDED:
        print("Publishing of gardenlinux offer to staging has been successfully completed. Trigger go live...")
        marketplace_client.go_live(publisher_id=publisher_id, offer_id=offer_id)
        golive_operation_id = marketplace_client.fetch_ongoing_operation_id(
            publisher_id,
            offer_id,
            AzmpTransportDest.PROD,
        )
        published_image = glci.model.AzurePublishedImage(
            transport_state="going_live",
            publish_operation_id=release.published_image_metadata.publish_operation_id,
            golive_operation_id=golive_operation_id,
        )
        return dataclasses.replace(release, published_image_metadata=published_image)

    # Go Live completed. Done!
    if transport_state == "going_live" and operation_status == AzmpOperationState.SUCCEEDED:
        print("Tranport to production of gardenlinux offer succeeded.")
        published_image = glci.model.AzurePublishedImage(
            transport_state="released",
            publish_operation_id=release.published_image_metadata.publish_operation_id,
            golive_operation_id=release.published_image_metadata.golive_operation_id,
            urn=generate_urn(cicd_cfg.publish.azure.marketplace, release.version),
        )
        return dataclasses.replace(release, published_image_metadata=published_image)

    print(f"Gardenlinux Azure Marketplace release operation {transport_state} is still ongoing...")
    return release


def upload_and_publish_image(
    s3_client,
    cicd_cfg: glci.model.CicdCfg,
    release: glci.model.OnlineReleaseManifest,
) -> glci.model.OnlineReleaseManifest:
    """Copies an image from S3 to an Azure Storage Account, updates the corresponding
    Azure Marketplace offering and publish the offering.
    """

    # Copy image from s3 to Azure Storage Account
    target_blob_name = f"gardenlinux-az-{release.version}.vhd"
    image_url = copy_image_from_s3_to_az_storage_account(
        storage_account_cfg=cicd_cfg.publish.azure.storate_account,
        s3_client=s3_client,
        s3_bucket_name=release.path_by_suffix('rootfs.raw').s3_bucket_name,
        s3_object_key=release.path_by_suffix('rootfs.raw').s3_key,
        target_blob_name=target_blob_name,
    )

    # Update Marketplace offer and start publishing.
    publish_operation_id = update_and_publish_marketplace_offer(
        service_principal_cfg=cicd_cfg.publish.azure.service_principal,
        marketplace_cfg=cicd_cfg.publish.azure.marketplace,
        image_version=release.version,
        image_url=image_url,
        notification_recipients=(), # TODO: configure email recipients
    )

    published_image = glci.model.AzurePublishedImage(
        transport_state="publishing",
        publish_operation_id=publish_operation_id,
    )

    return dataclasses.replace(release, published_image_metadata=published_image)
