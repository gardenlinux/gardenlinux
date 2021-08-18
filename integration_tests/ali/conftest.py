from dataclasses import dataclass

import ccc.alicloud
import pytest


@pytest.fixture(scope="session")
def ali_client():
    '''
    get an Ali client instance to further interact with ALi cloud objects
    '''
    return  ccc.alicloud.acs_client(alicloud_cfg='gardenlinux')
