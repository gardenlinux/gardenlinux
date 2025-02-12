"""
In this we keep the platforms specify test configuration.
"""

import pytest

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
def chroot(platform):
    if platform != 'chroot':
        pytest.skip('test only supported on chroot platform')

@pytest.fixture
def container(platform):
    """
    This fixture is an alias of "chroot" but does not use the "chroot" env.  However, it only needs
    the underlying container for its tests.
    """
    if platform != 'container' or platform != 'chroot':
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
def local(platform):
    if platform != 'local':
        pytest.skip('test only supported on local platform')

@pytest.fixture
def metal(platform):
    if platform != 'metal':
        pytest.skip('test only supported on metal platform')

@pytest.fixture
def openstack(platform):
    if platform != 'openstack-ccee':
        pytest.skip('test only supported on openstack')
