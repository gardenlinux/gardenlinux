from dataclasses import dataclass
import tempfile
import json
import os
from typing import Any

import ccc.gcp
import model.gcp
from util import ctx
import pytest


# Documentation:
# https://cloud.google.com/compute/docs/tutorials/python-guide
# https://github.com/GoogleCloudPlatform/python-docs-samples
# reference: https://cloud.google.com/compute/docs/reference/rest/v1

@dataclass
class GCP_Cfg:
    svc_account: model.gcp.GcpServiceAccount
    project_id: str


@pytest.fixture(scope="session")
def gcp_cfg():
    gcp_cfg = ctx().cfg_factory().gcp("gardenlinux")
    return GCP_Cfg(svc_account=gcp_cfg, project_id=gcp_cfg.project())


@pytest.fixture(scope="session")
def compute_client(gcp_cfg):
    '''
    get a Google client instance to further interact with GCP compute instances 
    '''
    return ccc.gcp.authenticated_build_func(gcp_cfg.svc_account)('compute', 'v1')
