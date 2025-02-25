import pytest
import logging
import json
import time
import yaml
import sys
import os
import re
from pathlib import Path

from typing import Iterator
from helper.sshclient import RemoteClient
from helper.utils import disabled_by

from os import path
from dataclasses import dataclass
from _pytest.config.argparsing import Parser

from platformSetup.chroot import CHROOT
from platformSetup.firecracker import FireCracker
from platformSetup.qemu import QEMU
from platformSetup.manual import Manual

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def pytest_addoption(parser: Parser):
    parser.addoption(
        "--iaas",
        action="store",
        help="What Infrastructure the tests should be provisioned on to run.",
    )
    parser.addoption(
        "--provisioner",
        action="store",
        help="What Infrastructure the tests should be provisioned on to run.",
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
    parser.addoption(
        "--create-only",
        action="store_true", 
        default=False,
        help="Only create and set up the test resources without running tests (default: False)"
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
def platform(pytestconfig, testconfig):
    if 'platform' in testconfig:
        return testconfig['platform']
    elif pytestconfig.getoption('iaas'):
        return pytestconfig.getoption('iaas')
    else:
        pytest.exit("Need to specify which platform (in configfile) or IaaS (via parameter) to test on.", 1)


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
        elif iaas == 'qemu':
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
            from platformSetup.azure import AZURE
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
def client(testconfig, iaas, imageurl, request) -> Iterator[RemoteClient]:
    """Create and manage the test client resources"""
    logger.info(f"Testconfig for {iaas=} is {testconfig}")
    test_name = testconfig.get('test_name', f"gl-test-{time.strftime('%Y%m%d')}-{os.urandom(2).hex()}")
    create_only = request.config.getoption("--create-only")
    
    try:
       if iaas == "openstack-ccee":
           from platformSetup.openstackccee import OpenStackCCEE
           yield from OpenStackCCEE.fixture(testconfig)
       elif iaas == "chroot":
           yield from CHROOT.fixture(testconfig)
       elif iaas == "firecracker":
           yield from FireCracker.fixture(testconfig)
       elif iaas == "qemu":
           yield from QEMU.fixture(testconfig)
       elif iaas == "manual":
           yield from Manual.fixture(testconfig)
       elif iaas == "local":
           yield testconfig
       else:
           raise ValueError(f"invalid {iaas=}")
    finally:
       if create_only:
           logger.info("Resource creation complete")
           pytest.exit("Resource creation complete", 0)

def create_resource_test(client):
    """Test that ensures the client fixture runs for resource creation"""
    pass

def create_resource_module(session):
    """Module and test for resource creation"""
    import _pytest.python
    
    module = _pytest.python.Module.from_parent(
        parent=session,
        path=Path("resource_creation_test.py")
    )
    
    return _pytest.python.Function.from_parent(
        name="test_resource_creation",
        parent=module,
        callobj=create_resource_test
    )

def pytest_collection_modifyitems(config, items):
    """Skip tests that belong to a feature that is not enabled in the test config"""
    if config.getoption("--create-only"):
        # Replace all items with our resource creation test
        session = items[0].session if items else config.pluginmanager.get_plugin("session")
        items[:] = [create_resource_module(session)]
        return

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
        for marker in item.iter_markers(name="security_id"):
            # For the mapping of the necessary testing for our compliance, we define our own mark.
            # We add this to the user_properties field. This way it shows up in any generated report.
            # https://docs.pytest.org/en/4.6.x/reference.html#item
            security_id = marker.args[0]
            item.user_properties.append(("security_id", security_id))

        item_path = str(item.fspath)
        # check if a feature is in the enabled feature, if not skip it.
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


# all configuration for our test has been split into smaller parts.  
pytest_plugins = [
     "conftests.architecture",
     "conftests.elements",
     "conftests.features",
     "conftests.miscellaneous",
     "conftests.platforms",
     "conftests.provisioner",
  ]

# THis is a helper function some tests invoke.
@pytest.fixture
def openstack_flavor():
    return OpenStackCCEE.instance().flavor
