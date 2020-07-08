import dataclasses
from datetime import (
    datetime,
    timedelta,
)
from enum import Enum

import requests
from msal import ConfidentialClientApplication
from azure.storage.blob import (
    BlobClient,
    BlobType,
    ContainerSasPermissions,
    generate_container_sas,
)
from msal import ConfidentialClientApplication

import glci.model


'''
The publishing process for an image to the Azure Marketplace consist of
two sequences of steps.

1. publishing steps - this include the upload of the image to an Azure StorageAccount,
the update of the gardenlinux Marketplace spec, the trigger of the publish operation
which will trigger the validation of the image on the Microsoft side and upload
the image into their staging enviroment.
Those steps are covered by the "upload_and_publish_image" function.

2. check and approve steps – first the progress of the triggered publish operation
will be checked. If the publish operation has been completed the go live operation
will be triggered automatically. After that it will check for the progress of the
go live operation and if this also has been completed it will return the urn of the image.
Those steps are covered by the "check_offer_transport_state" function.
It need to be called multiple times until the entire process has been completed.
'''


class AzureImageStore:
    '''Azure Image Store backed by an container in an Azure Storage Account.'''

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
        '''Copy an object from Amazon S3 to an Azure Storage Account

        This will overwrite the contents of the target file if it already exists.
        '''
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
        '''Generate an url including sas token to access image in the store.'''
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
    '''Azure Marketplace Client is a client to interact with the Azure Marketplace.'''

    marketplace_baseurl = "https://cloudpartner.azure.com/api/publishers"

    def __init__(self, spn_tenant_id: str, spn_client_id: str, spn_client_secret: str):
        app_client = ConfidentialClientApplication(
            client_id=spn_client_id,
            authority=f"https://login.microsoftonline.com/{spn_tenant_id}",
            client_credential=spn_client_secret
        )
        token = app_client.acquire_token_for_client(scopes="https://cloudpartner.azure.com/.default")
        if 'error' in token:
            raise RuntimeError("Could not fetch token for Azure Marketplace client", token['error_description'])
        self.token = token['access_token']

    def _request(self, url: str, method='GET', headers={}, params={}, **kwargs):
        if 'Authorization' not in headers:
            headers['Authorization'] = f"Bearer {self.token}"
        if 'Content-Type' not in headers:
            headers['Content-Type'] = "application/json"

        if 'api-version' not in params:
            params['api-version'] = '2017-10-31'

        return requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            **kwargs
        )

    def _api_url(self, *parts):
        return '/'.join(p for p in (self.marketplace_baseurl, *parts))

    def _raise_for_status(self, response, message=""):
        if response.ok:
            return
        if message:
            raise RuntimeError(f"{message}. statuscode={response.status_code}")
        raise RuntimeError(f"HTTP call to {response.url} failed. statuscode={response.status_code}")

    def fetch_offer(self, publisher_id: str, offer_id: str):
        '''Fetch an offer from Azure marketplace.'''

        response = self._request(url=self._api_url(publisher_id, "offers", offer_id))
        self._raise_for_status(
            response=response,
            message='Fetching of Azure marketplace offer for gardenlinux failed',
        )
        offer_spec = response.json()
        return offer_spec

    def update_offer(self, publisher_id: str, offer_id: str, spec: dict):
        '''Update an offer with a give spec.'''

        response = self._request(
            url=self._api_url(publisher_id, "offers", offer_id),
            method='PUT',
            headers={"If-Match": "*"},
            json=spec,
        )
        self._raise_for_status(
            response=response,
            message='Update of Azure marketplace offer for gardenlinux failed',
        )

    def publish_offer(self, publisher_id: str, offer_id: str, notification_mails=()):
        '''Trigger (re-)publishing of an offer.'''

        data = {
            "metadata": {
                "notification-emails": ",".join(notification_mails)
            }
        }
        response = self._request(
            method='POST',
            url=self._api_url(publisher_id, "offers", offer_id, "publish"),
            json=data,
        )
        self._raise_for_status(
            response=response,
            message="Can't publish updated Azure marketplace offer for gardenlinux",
        )

    def fetch_ongoing_operation_id(self, publisher_id: str, offer_id: str, transport_dest: AzmpTransportDest):
        '''Fetches the id of an ongoing Azure Marketplace transport operation to a certain transport destination.'''

        response = self._request(url=self._api_url(publisher_id, "offers", offer_id, "submissions"))
        self._raise_for_status(
            response=response,
            message="Could not fetch Azure Marketplace transport operations for gardenlinux offer",
        )
        operations = response.json()
        for operation in operations:
            if AzmpTransportDest(operation["slot"]) == transport_dest and AzmpOperationState(operation["submissionState"]) == AzmpOperationState.RUNNING:
                return operation["id"]
        raise RuntimeError(f"Did not find an ongoing transport operation to ship gardenliunx offer on the Azure Marketplace.")

    def fetch_operation_state(self, publisher_id: str, offer_id: str, operation_id: str):
        '''Fetches the state of a given Azure Marketplace transport operation.'''

        response = self._request(url=self._api_url(publisher_id, "offers", offer_id, "operations", operation_id))
        self._raise_for_status(
            response=response,
            message=f"Can't fetch state for transport operation {operation_id}",
        )
        operation = response.json()
        return AzmpOperationState(operation['status'])

    def go_live(self, publisher_id: str, offer_id: str):
        '''Trigger a go live operation to transport an Azure Marketplace offer to production.'''

        response = self._request(
            method='POST',
            url=self._api_url(publisher_id, "offers", offer_id, "golive"),
        )
        self._raise_for_status(
            response=response,
            message="Go live of updated gardenlinux Azure Marketplace offer failed",
        )


def _find_plan_spec(offer_spec :dict, plan_id: str):
    plan_spec = {}
    for plan in offer_spec["definition"]["plans"]:
        if plan["planId"] == plan_id:
            plan_spec = plan
            break
    else:
        raise RuntimeError(f"Plan {plan_id} not found in offer {spec['id']}.")
    return plan_spec

def add_image_version_to_plan(
    spec: dict,
    plan_id: str,
    image_version: str,
    image_url: str
):
    '''
    Add a new image version to a given plan and return a modified offer spec.

    The offer spec needs to be fetched upfront from the Azure Marketplace.
    The modified offer spec needs to be pushed to the Azure Marketplace.
    '''

    plan_spec = _find_plan_spec(spec, plan_id)
    plan_spec["microsoft-azure-virtualmachines.vmImages"][image_version] = {
        "osVhdUrl": image_url,
        "lunVhdDetails": []
    }
    return spec


def remove_image_version_from_plan(spec: dict, plan_id: str, image_version: str, image_url: str):
    '''
    Remove an image version from a given plan and return a modified offer spec.

    The offer spec needs to be fetched upfront from the Azure Marketplace.
    The modified offer spec needs to be pushed to the Azure Marketplace.
    '''

    plan_spec = _find_plan_spec(spec, plan_id)
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
    image_version :str,
    image_url :str,
    notification_recipients=(),
):

    marketplace_client = AzureMarketplaceClient(
        spn_tenant_id=service_principal_cfg.tenant_id,
        spn_client_id=service_principal_cfg.client_id,
        spn_client_secret=service_principal_cfg.client_secret,
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
        publisher_id=publisher_id,
        offer_id=offer_id,
        transport_dest=AzmpTransportDest.STAGING,
    )
    return publish_operation_id


def check_offer_transport_state(
    cicd_cfg: glci.model.CicdCfg,
    release: glci.model.OnlineReleaseManifest,
) -> glci.model.OnlineReleaseManifest:
    '''Checks the state of the gardenlinux Azure Marketplace offer transport

    In case the transport to staging enviroment has been succeeded then the transport
    to production (go live) will be automatically triggered.
    '''

    transport_state = release.published_image_metadata.transport_state
    if transport_state == glci.model.AzureTransportState.RELEASED:
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
            transport_state=glci.model.AzureTransportState.FAILED,
            publish_operation_id=release.published_image_metadata.publish_operation_id,
            golive_operation_id='',
            urn='',
        )
        if release.published_image_metadata.transport_state == glci.model.AzureTransportState.GO_LIVE:
            published_image.golive_operation_id = release.published_image_metadata.golive_operation_id
        return dataclasses.replace(release, published_image_metadata=published_image)

    # Publish completed. Trigger go live to transport the offer changes to production.
    if transport_state == glci.model.AzureTransportState.PUBLISH and operation_status == AzmpOperationState.SUCCEEDED:
        print("Publishing of gardenlinux offer to staging has been successfully completed. Trigger go live...")
        marketplace_client.go_live(publisher_id=publisher_id, offer_id=offer_id)
        golive_operation_id = marketplace_client.fetch_ongoing_operation_id(
            publisher_id,
            offer_id,
            AzmpTransportDest.PROD,
        )
        published_image = glci.model.AzurePublishedImage(
            transport_state=glci.model.AzureTransportState.GO_LIVE,
            publish_operation_id=release.published_image_metadata.publish_operation_id,
            golive_operation_id=golive_operation_id,
            urn='',
        )
        return dataclasses.replace(release, published_image_metadata=published_image)

    # Go Live completed. Done!
    if transport_state == glci.model.AzureTransportState.GO_LIVE and operation_status == AzmpOperationState.SUCCEEDED:
        print("Tranport to production of gardenlinux offer succeeded.")
        published_image = glci.model.AzurePublishedImage(
            transport_state=glci.model.AzureTransportState.RELEASED,
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
    '''Copies an image from S3 to an Azure Storage Account, updates the corresponding
    Azure Marketplace offering and publish the offering.
    '''

    # Copy image from s3 to Azure Storage Account
    target_blob_name = f"gardenlinux-az-{release.version}.vhd"
    image_url = copy_image_from_s3_to_az_storage_account(
        storage_account_cfg=cicd_cfg.publish.azure.storage_account,
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
        notification_recipients=cicd_cfg.publish.azure.notification_recipients,
    )

    published_image = glci.model.AzurePublishedImage(
        transport_state=glci.model.AzureTransportState.PUBLISH,
        publish_operation_id=publish_operation_id,
        golive_operation_id='',
        urn='',
    )

    return dataclasses.replace(release, published_image_metadata=published_image)
