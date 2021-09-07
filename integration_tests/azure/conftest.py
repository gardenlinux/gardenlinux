from dataclasses import dataclass
import pytest

from azure.identity import (
    AzureCliCredential,
    ClientSecretCredential,
)
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient

import glci.az
import glci.model
from util import ctx
import glci.util


@dataclass
class AzureCfg:
    client_id: str
    client_secret: str
    tenant_id: str
    subscription_id: str
    marketplace_cfg: glci.model.AzureMarketplaceCfg


@pytest.fixture(scope="session")
def azure_cfg():
    cicd_cfg = glci.util.cicd_cfg()
    service_principal_cfg_tmp = ctx().cfg_factory().azure_service_principal(
        cicd_cfg.publish.azure.service_principal_cfg_name, #'shoot-operator-dev'
    )
    service_principal_cfg = glci.model.AzureServicePrincipalCfg(
        **service_principal_cfg_tmp.raw
    )

    azure_marketplace_cfg = glci.model.AzureMarketplaceCfg(
        publisher_id=cicd_cfg.publish.azure.publisher_id,
        offer_id=cicd_cfg.publish.azure.offer_id,
        plan_id=cicd_cfg.publish.azure.plan_id,
    )

    return AzureCfg(
        client_id=service_principal_cfg.client_id,
        client_secret=service_principal_cfg.client_secret,
        tenant_id=service_principal_cfg.tenant_id,
        marketplace_cfg=azure_marketplace_cfg,
        subscription_id=service_principal_cfg.subscription_id,
    )


@pytest.fixture(scope='session')
def azure_credentials(azure_cfg: AzureCfg, pytestconfig):
    if pytestconfig.getoption('local'):
        return AzureCliCredential()
    else:
        return ClientSecretCredential(
            client_id=azure_cfg.client_id,
            client_secret=azure_cfg.client_secret,
            tenant_id=azure_cfg.tenant_id
        )


@pytest.fixture(scope="session")
def marketplace_client(azure_cfg) -> glci.az.AzureMarketplaceClient:
    '''
    get an Azure marketplace client instance to further interact with marketplace
    '''
    return glci.az.AzureMarketplaceClient(
        spn_tenant_id=azure_cfg.tenant_id,
        spn_client_id=azure_cfg.client_id,
        spn_client_secret=azure_cfg.client_secret,
    )


@pytest.fixture(scope="session")
def compute_client(azure_credentials, azure_cfg):
    '''
    get a Azure client instance to further interact with Azure compute instances
    '''
    return ComputeManagementClient(azure_credentials, azure_cfg.subscription_id)


@pytest.fixture(scope="session")
def storage_client(azure_credentials, azure_cfg):
    '''
    get a Azure client instance to further interact with Azure storage instances
    '''
    return StorageManagementClient(azure_credentials, azure_cfg.subscription_id)
