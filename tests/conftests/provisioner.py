""" We define the fixtures here, that we can use to run the tests on.

Do not confuse the iaas keyword with the platform keyword. Both words are used
often interchangeably. However, in our context we're talking here about
environments in which our images/rootfs will be executed on for testing.

This can be any Container Runtime Environment like podman/docker or a
Virtualization Environment like KVM/VMWare or a simple wrapper program like
chroot. Since this file defines the environment we want to conduct our tests
on. We're using in the future the word: provisioner

pytest --provisioner=chroot 
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
