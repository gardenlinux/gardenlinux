import pytest
import logging
import json
import time
import yaml
import sys
import os
import sys
import re


from typing import Iterator
from helper.sshclient import RemoteClient
from helper.utils import disabled_by

from os import path
from dataclasses import dataclass
from _pytest.config.argparsing import Parser

from integration.aws import AWS
from integration.azure import AZURE
from integration.gcp import GCP
from integration.ali import ALI
from integration.openstackccee import OpenStackCCEE
from integration.chroot import CHROOT
from integration.firecracker import FireCracker
from integration.kvm import KVM
from integration.manual import Manual

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def pytest_addoption(parser: Parser):
    parser.addoption(
        "--iaas",
        action="store",
        help="Infrastructure the tests should run on",
    )
    parser.addoption(
        "--configfile",
        action="store",
        default="test_config.yaml",
        help="Test configuration file"
    )
    parser.addoption(
        "--pipeline",
        action='store_true',
        help="tests are run from a pipeline context and thus, certain pieces of information are retrieved differently"
    )
    parser.addoption(
        "--image",
        nargs="?",
        help="URI for the image to be tested (overwrites value in config.yaml)"
    )


@pytest.fixture(scope="session")
def pipeline(pytestconfig):
    if pytestconfig.getoption('pipeline'):
        return True
    return False


@pytest.fixture(scope="session")
def iaas(pytestconfig):
    if pytestconfig.getoption('iaas'):
        return pytestconfig.getoption('iaas')
    pytest.exit("Need to specify which IaaS to test on.", 1)


@pytest.fixture(scope="session")
def image_suffix(iaas):
    image_suffixes = {
        "aws": "rootf.raw",
        "azure": "rootfs.vhd",
        "gcp": "rootfs-gcpimage.tar.gz",
        "ali": "rootfs.qcow2",
        "openstack-ccee": "rootfs.vmdk"
    }
    return image_suffixes[iaas]



@pytest.fixture(scope="session")
def imageurl(pipeline, testconfig, pytestconfig, request):
    if pipeline:
        s3_image_location = request.getfixturevalue('s3_image_location')
        return f's3://{s3_image_location.bucket_name}/{s3_image_location.raw_image_key}'
    elif pytestconfig.getoption('image'):
        return pytestconfig.getoption('image')
    else:
        if 'image' in testconfig:
            return testconfig['image']


@pytest.fixture(scope="session")
def testconfig(pipeline, iaas, pytestconfig):
    if not pipeline:
        configfile = pytestconfig.getoption("configfile")
        try:
            with open(configfile) as f:
                configoptions = yaml.load(f, Loader=yaml.FullLoader)
        except OSError as err:
            pytest.exit(err, 1)
        if iaas in configoptions:
            return configoptions[iaas]
        else:
            pytest.exit(f"Configuration section for {iaas} not found in {configfile}.", 1)
    else:
        if iaas == 'aws':
            ssh_config = {
                'user': 'admin'
            }
            config = {
                'region': 'eu-central-1',
                'instance_type': 'm5.large',
                'keep_running': 'false',
                'ssh': ssh_config
            }
        elif iaas == 'azure':
            ssh_config = {
                'user': 'azureuser'
            }
            config = {
                'location': 'westeurope',
                'keep_running': 'false',
                'ssh': ssh_config
            }
        elif iaas == 'gcp':
            ssh_config = {
                'user': 'gardenlinux'
            }
            config = {
                'region': 'europe-west1',
                'zone': 'europe-west1-d',
                'machine_type': 'n1-standard-2',
                'keep_running': 'false',
                'ssh': ssh_config
            }
        elif iaas == 'ali':
            pass
        elif iaas == 'openstack-ccee':
            pass
        elif iaas == 'chroot':
            pass
        elif iaas == 'firecracker':
            pass
        elif iaas == 'kvm':
            pass
        elif iaas == 'manual':
            pass
        elif iaas == 'local':
            pass
        return config


@pytest.fixture(scope="session")
def aws_session(testconfig, pipeline, request):
    import boto3
    
    if "region" in testconfig:
        return boto3.Session(region_name=testconfig["region"])
    else:
        return boto3.Session()


@pytest.fixture(scope="session")
def azure_credentials(testconfig, pipeline, request):
    from azure.identity import (
        AzureCliCredential,
        ClientSecretCredential
    )

    @dataclass
    class AZCredentials:
        credential: object
        subscription_id: str

    credential = AzureCliCredential()
    if 'subscription_id' in testconfig:
        subscription_id = testconfig['subscription_id']
    elif 'subscription' in testconfig:
        try:
            subscription_id = AZURE.find_subscription_id(credential, testconfig['subscription'])
        except RuntimeError as err:
            pytest.exit(err, 1)
    return AZCredentials(
        credential = credential,
        subscription_id = subscription_id
    )


@pytest.fixture(scope='session')
def gcp_credentials(testconfig, pipeline, request):
    import google.oauth2.service_account

    if "service_account_json_path" in testconfig:
        service_account_json_path = path.expanduser(testconfig["service_account_json_path"])
        with open(service_account_json_path, "r") as f:
            service_account_json = f.read()
        return google.oauth2.service_account.Credentials.from_service_account_info(
            json.loads(service_account_json)
        )
    else:
        return None


@pytest.fixture(scope="session")
def local(iaas):
    logger.info(f"Testconfig for {iaas=} is {testconfig}")
    test_name = testconfig.get('test_name', f"gl-test-{time.strftime('%Y%m%d%H%M%S')}")


@pytest.fixture(scope="session")
def client(testconfig, iaas, imageurl, request) -> Iterator[RemoteClient]:
    logger.info(f"Testconfig for {iaas=} is {testconfig}")
    test_name = testconfig.get('test_name', f"gl-test-{time.strftime('%Y%m%d%H%M%S')}")
    if iaas == "aws":
        session = request.getfixturevalue('aws_session')
        yield from AWS.fixture(session, testconfig, imageurl, test_name)
    elif iaas == "gcp":
        credentials = request.getfixturevalue('gcp_credentials')
        logger.info("Requesting GCP fixture")
        yield from GCP.fixture(credentials, testconfig, imageurl, test_name)
    elif iaas == "azure":
        credentials = request.getfixturevalue('azure_credentials')
        yield from AZURE.fixture(credentials, testconfig, imageurl, test_name)
    elif iaas == "openstack-ccee":
        yield from OpenStackCCEE.fixture(testconfig)
    elif iaas == "chroot":
        yield from CHROOT.fixture(testconfig)
    elif iaas == "firecracker":
        yield from FireCracker.fixture(testconfig)
    elif iaas == "kvm":
        yield from KVM.fixture(testconfig)
    elif iaas == "ali":
        yield from ALI.fixture(testconfig, test_name)
    elif iaas == "manual":
        yield from Manual.fixture(testconfig)
    elif iaas == "local":
        yield testconfig
    else:
        raise ValueError(f"invalid {iaas=}")


def pytest_collection_modifyitems(config, items):
    """Skip tests that belong to a feature that is not enabled in the test config"""
    skip = pytest.mark.skip(reason="test is not part of the enabled features")
    iaas = config.getoption("--iaas")
    config_file = config.getoption("--configfile")
    try:
        with open(config_file) as f:
            config_options = yaml.load(f, Loader=yaml.FullLoader)
    except OSError as err:
        logger.error(f"can not open config file {config_file}")
        pytest.exit(err, 1)
    if not iaas == 'local':
        features = config_options[iaas].get("features", [])
    else:
        features = []
    for item in items:
        item_path = str(item.fspath)
        if "features" in item_path:
            feature = item_path.split('/')[3]
            if not feature in features:
                item.add_marker(skip)
        plain_item_name = re.match(r"test_([\w_]+)\[?.*", item.name).group(1)
        disabled = disabled_by(features, plain_item_name)
        if len(disabled) != 0:
            item.add_marker(pytest.mark.skip(reason=f"test is disabled by feature " +
                                                    f"{', '.join(disabled)}"))


@pytest.fixture
def features(client):
    (exit_code, output, error) = client.execute_command("cat /etc/os-release", quiet=True)
    if exit_code != 0:
        logger.error(error)
        sys.exit(exit_code)
    for line in output.split('\n'):
        if line.startswith('GARDENLINUX_FEATURES'):
            features = line.split('=')[1]
    current = (os.getenv('PYTEST_CURRENT_TEST')).split('/')
    yield features.split(','), current[0]


@pytest.fixture
def non_ali(iaas):
    if iaas == 'ali':
        pytest.skip('test not supported on ali')

@pytest.fixture
def ali(iaas):
    if iaas != 'ali':
        pytest.skip('test only supported on ali')

@pytest.fixture
def non_azure(iaas):
    if iaas == 'azure':
        pytest.skip('test not supported on azure')

@pytest.fixture
def azure(iaas):
    if iaas != 'azure':
        pytest.skip('test only supported on azure')

@pytest.fixture
def non_aws(iaas):
    if iaas == 'aws':
        pytest.skip('test not supported on aws')

@pytest.fixture
def aws(iaas):
    if iaas != 'aws':
        pytest.skip('test only supported on aws')

@pytest.fixture
def non_gcp(iaas):
    if iaas != 'gcp':
        pytest.skip('test only supported on gcp')

@pytest.fixture
def gcp(iaas):
    if iaas != 'gcp':
        pytest.skip('test only supported on gcp')

@pytest.fixture
def non_firecracker(iaas):
    if iaas == 'firecracker':
        pytest.skip('test not supported on firecracker')

@pytest.fixture
def firecracker(iaas):
    if iaas != 'firecracker':
        pytest.skip('test only supported on firecracker')

@pytest.fixture
def non_kvm(iaas):
    if iaas == 'kvm':
        pytest.skip('test not supported on kvm')

@pytest.fixture
def kvm(iaas):
    if iaas != 'kvm':
        pytest.skip('test only supported on kvm')

@pytest.fixture
def non_chroot(iaas):
    if iaas == 'chroot':
        pytest.skip('test not supported on chroot')

@pytest.fixture
def chroot(iaas):
    if iaas != 'chroot':
        pytest.skip('test only supported on chroot')

@pytest.fixture
def non_local(iaas):
    if iaas == 'local':
        pytest.skip('test not supported on local')

@pytest.fixture
def local(iaas):
    if iaas != 'local':
        pytest.skip('test only supported on local')

@pytest.fixture
def non_openstack(iaas):
    if iaas == 'openstack-ccee':
        pytest.skip('test not supported on openstack')

@pytest.fixture
def openstack(iaas):
    if iaas != 'openstack-ccee':
        pytest.skip('test only supported on openstack')

@pytest.fixture
def non_hyperscalers(iaas):
    if iaas == 'aws' or iaas == 'gcp' or iaas == 'azure' or iaas == 'ali':
        pytest.skip(f"test not supported on hyperscaler {iaas}")

# This fixture is an alias of "chroot" but does not use the "chroot" env.
# However, it only needs the underlying container for its tests.
@pytest.fixture
def container(iaas):
    if iaas != 'chroot':
        pytest.skip('test only supported on containers')

@pytest.fixture
def openstack_flavor():
    return OpenStackCCEE.instance().flavor

@pytest.fixture
def non_amd64(client):
    (exit_code, output, error) = client.execute_command("dpkg --print-architecture", quiet=True)
    if exit_code != 0:
        logger.error(error)
        sys.exit(exit_code)
    if "amd64" in output:
        pytest.skip('test not supported on amd64 architecture')

@pytest.fixture
def non_arm64(client):
    (exit_code, output, error) = client.execute_command("dpkg --print-architecture", quiet=True)
    if exit_code != 0:
        logger.error(error)
        sys.exit(exit_code)
    if "arm64" in output:
        pytest.skip('test not supported on arm64 architecture')

@pytest.fixture
def non_metal(testconfig):
    features = testconfig.get("features", [])
    if "metal" in features:
        pytest.skip('test not supported on metal')

@pytest.fixture
def non_feature_gardener(testconfig):
    features = testconfig.get("features", [])
    if "gardener" in features:
        pytest.skip('test is not supported on gardener')

@pytest.fixture
def non_feature_githubActionRunner(testconfig):
    features = testconfig.get("features", [])
    if "githubActionRunner" in features:
        pytest.skip('test is not supported on githubActionRunner')

@pytest.fixture
def non_dev(testconfig):
    features = testconfig.get("features", [])
    if "_dev" in features:
        pytest.skip('test not supported on dev')

@pytest.fixture
def non_vhost(testconfig):
    features = testconfig.get("features", [])
    if "vhost" in features:
        pytest.skip('test not supported with vhost feature enabled')

@pytest.fixture
# After solving #1240 define "firecracker" as IAAS
def firecracker(testconfig):
    features = testconfig.get("features", [])
    if "firecracker" in features:
        skip_msg = "Currently unsupported. Please see: https://github.com/gardenlinux/gardenlinux/issues/1240"
        pytest.skip(skip_msg)

@pytest.fixture
def non_container(testconfig):
    features = testconfig.get("features", [])
    if "container" in features:
        pytest.skip('test is not supported on container')
