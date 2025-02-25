"""
In this we keep the platforms specify test configuration.
The file is structured as follows:
    - platform
    - non_platform
    - platform set
    - non_platform set
"""

import pytest

##########
# Platform
##########

@pytest.fixture
def ali(platform):
    if platform != 'ali':
        pytest.skip('test only supported on ali platform')

@pytest.fixture
def aws(platform):
    if platform != 'aws':
        pytest.skip('test only supported on aws platform')

@pytest.fixture
def azure(platform):
    if platform != 'azure':
        pytest.skip('test only supported on azure platform')

@pytest.fixture
def container(platform):
    """
    This fixture is for the container platform and require a Container Runtime Environment. 
    We do not sepcify what runtime environment this targets.
    """
    if platform != 'container': 
        pytest.skip('test only supported on container platform')

@pytest.fixture
def firecracker(platform):
    if platform != 'firecracker':
        pytest.skip('test only supported on firecracker platform')

@pytest.fixture
def gcp(platform):
    if platform != 'gcp':
        pytest.skip('test only supported on gcp platform')

@pytest.fixture
def kvm(platform):
    if platform != 'kvm':
        pytest.skip('test only supported on kvm platform')

@pytest.fixture
def metal(platform):
    if platform != 'metal':
        pytest.skip('test only supported on metal platform')

@pytest.fixture
def openstack(platform):
    if platform != 'openstack-ccee':
        pytest.skip('test only supported on openstack')

####################
# Platform blacklist
####################

@pytest.fixture
def non_ali(platform):
    if platform == 'ali':
        pytest.skip('test not supported on ali platform')

@pytest.fixture
def non_aws(platform):
    if platform == 'aws':
        pytest.skip('test not supported on aws platform')

@pytest.fixture
def non_azure(platform):
    if platform == 'azure':
        pytest.skip('test not supported on azure')

@pytest.fixture
def non_container(testconfig):
    features = testconfig.get("features", [])
    if "container" in features:
        pytest.skip('test is not supported on container')

@pytest.fixture
def non_firecracker(platform):
    if platform == 'firecracker':
        pytest.skip('test not supported on firecracker')

@pytest.fixture
def non_gcp(platform):
    if platform == 'gcp':
        pytest.skip('test not supported on gcp')

@pytest.fixture
def non_kvm(platform):
    if platform == 'kvm':
        pytest.skip('test not supported on kvm')

@pytest.fixture
def non_metal(testconfig):
    features = testconfig.get("features", [])
    if "metal" in features:
        pytest.skip('test not supported on metal')

@pytest.fixture
def non_openstack(platform):
    if platform == 'openstack-ccee':
        pytest.skip('test not supported on openstack')


##################
# Pooled Platforms
##################

@pytest.fixture
def ccee(platform):
    if 'openstack-ccee' not in platform and 'openstack-baremetal-ccee' not in platform:
        pytest.skip("test only supported on ccee platform")

@pytest.fixture
def hyperscalers(platform):
    list_of_platforms = {'aws', 'gcp', 'azure', 'ali'}
    if platform not in list_of_platforms:
        pytest.skip(f"test only supported on hyperscaler {platform} platform")

##############################
# Pooled Platforms blackedlist
##############################

@pytest.fixture
def non_hyperscalers(platform):
    list_of_platforms = {'aws', 'gcp', 'azure', 'ali'}
    if platform in  list_of_platforms:
        pytest.skip(f"test not supported on hyperscaler {platform} platform")

@pytest.fixture
def non_ccee(platform):
    ccee_platforms = {'openstack-ccee', 'openstack-baremetal-ccee'}
    if platform in ccee_platforms:
        pytest.skip("test not supported on ccee platform")
