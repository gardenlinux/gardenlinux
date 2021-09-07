import dataclasses

import google.oauth2.service_account
import googleapiclient.discovery

import model.gcp
import pytest

from util import ctx


# Documentation:
# https://cloud.google.com/compute/docs/tutorials/python-guide
# https://github.com/GoogleCloudPlatform/python-docs-samples
# reference: https://cloud.google.com/compute/docs/reference/rest/v1

@dataclasses.dataclass
class GCP_Cfg:
    svc_account: model.gcp.GcpServiceAccount
    project_id: str


@pytest.fixture(scope="session")
def gcp_cfg():
    gcp_cfg = ctx().cfg_factory().gcp("gardenlinux")
    return gcp_cfg


@pytest.fixture(scope='session')
def gcp_credentials(gcp_cfg, pytestconfig) -> 'google.auth.credentials.Credentials':
    if pytestconfig.getoption('local'):
        # passing 'None' as credential to gcp clients will implicitly look for other, local methods
        # (e.g. existing gcloud auth)
        return None
    else:
        return google.oauth2.service_account.Credentials.from_service_account_info(
            gcp_cfg.service_account_key(),
        )


@pytest.fixture(scope="session")
def compute_client(gcp_credentials):
    '''
    get a Google client instance to further interact with GCP compute instances
    '''
    return googleapiclient.discovery.build(
        'compute', 'v1',
        credentials=gcp_credentials,
    )
