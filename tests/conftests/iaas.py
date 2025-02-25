"""We define the fixtures here, that we can use to run the tests.

Do not confuse it with the platform, since we're talking here more about
Container Runtime Environment like podman/docker or Virtualization Environment
we want to conduct our tests on.

The parameter will be not be define by the feauter, but by a execution flag
that we run during pytest

pytest --iaas
"""

import pytest

@pytest.fixture
def chroot(iaas):
    """This is the target infrastructure process we consume"""
    if iaas != 'chroot':
        pytest.skip('test only supported on chroot')

@pytest.fixture
def local(iaas):
    if iaas != 'local':
        pytest.skip('test only supported on local')

@pytest.fixture
def manual(iaas):
    if iaas != 'local':
        pytest.skip('test only supported on local')

@pytest.fixture
def qemu(iaas):
    """This is the target infrastructure process we consume"""
    if iaas != 'qemu':
        pytest.skip('test only supported on qemu')

@pytest.fixture
def non_chroot(iaas):
    if iaas == 'chroot':
        pytest.skip('test not supported on chroot')

@pytest.fixture
def non_local(iaas):
    if iaas == 'local':
        pytest.skip('test not supported on local')

@pytest.fixture
def non_manual(iaas):
    if iaas == 'manual':
        pytest.skip('test not supported on manual')

@pytest.fixture
def non_qemu(iaas):
    if iaas == 'qemu':
        pytest.skip('test not supported on qemu')
