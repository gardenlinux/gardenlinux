import os
from string import Template

import glci.util
import pytest
import sys
import yaml


# @dataclass -> do no use dataclass this silently breaks pytest
class TestRunParameters:
    def __init__(
        self,
        architecture: str,
        cicd_cfg_name: str,
        gardenlinux_epoch: str,
        modifiers: str,
        platform: str,
        publishing_actions: str,
        repo_dir: str,
        suite: str,
        snapshot_timestamp: str,
        version: str,
        committish: str,
    ):
        self.architecture = architecture
        self.cicd_cfg_name = cicd_cfg_name
        self.gardenlinux_epoch = gardenlinux_epoch
        self.modifiers = modifiers
        self.platform = platform
        self.publishing_actions = publishing_actions
        self.repo_dir = repo_dir
        self.suite = suite
        self.snapshot_timestamp = snapshot_timestamp
        self.version = version
        self.committish = committish


class PyTestParamsPlugin:
    def __init__(self, params: TestRunParameters):
        self.params = params

    @pytest.fixture(scope="session")
    def test_params(self, request) -> TestRunParameters:
        return self.params


def _get_test_suite_from_platform(
    architecture: str,
    platform: str,
):
    if architecture == 'amd64':
        if platform == 'ali':
            return 'ali'
        elif platform == 'aws':
            return 'aws'
        elif platform == 'azure':
            return 'azure'
        elif platform == 'gcp':
            return 'gcp'
        elif platform == 'openstack':
            return 'openstack'
        else:
            return None
    else:
        return None


def run_tests(
    architecture: str,
    cicd_cfg_name: str,
    gardenlinux_epoch: str,
    modifiers: str,
    platform: str,
    publishing_actions: str,
    repo_dir: str,
    suite: str,
    snapshot_timestamp: str,
    version: str,
    committish: str,
    pytest_cfg: str = None,
):
    print(f'run_test with: {architecture=}, {cicd_cfg_name=}, {gardenlinux_epoch=}')
    print(f'   : {modifiers=}, {platform=}, {publishing_actions=}, {repo_dir=}')
    print(f'   : {suite=}, {snapshot_timestamp=}, {version=}')
    publishing_actions = [
        glci.model.PublishingAction(action.strip()) for action in publishing_actions.split(',')
    ]

    if not glci.model.PublishingAction.RUN_TESTS in publishing_actions:
        print('publishing action "run_tests" not specified - skipping tests')
        return True

    modifiers = tuple(modifiers.split(','))

    params = TestRunParameters(
        architecture=architecture,
        cicd_cfg_name=cicd_cfg_name,
        gardenlinux_epoch=gardenlinux_epoch,
        modifiers=modifiers,
        platform=platform,
        publishing_actions=publishing_actions,
        repo_dir=repo_dir,
        suite=suite,
        snapshot_timestamp=snapshot_timestamp,
        version=version,
        committish=committish
    )

    params_plugin = PyTestParamsPlugin(params)
    cfg_name = pytest_cfg.strip()
    test_cfg_path = os.path.join(repo_dir, "ci", "test_cfg.yaml")
    if not os.path.exists(test_cfg_path):
        print(f'Configuration file for tests: {test_cfg_path} not found, exiting')
        sys.exit(1)
    if not pytest_cfg:
        print('No tests configured, nothing to do')
        sys.exit(0)
    else:
        final_arg = None
        with open(test_cfg_path) as file:
            test_cfgs = yaml.safe_load(file)

        if  not 'test_cfgs' in test_cfgs:
            print(f'Profile: {cfg_name} not found in file {test_cfg_path}. Stopping')
            sys.exit(1)
        if not cfg_name in test_cfgs['test_cfgs']:
            print(f'Profile: {cfg_name} not found in file {test_cfg_path}. Stopping')
            sys.exit(1)

        test_profile = test_cfgs['test_cfgs'][cfg_name]
        if architecture in test_profile['architecture']:
            sub_cfg = test_profile['architecture'][architecture]
            if platform in sub_cfg['platform']:
                final_arg = sub_cfg['platform'][platform]
        if not final_arg:
            print(f'No test configured for {architecture=}, {platform=} in {cfg_name}')
            return 0
        template = Template(final_arg)
        pytest_args = template.substitute(platform=platform, architecture=architecture)
        pytest_arg_list = pytest_args.split()
    print(f'Running integration tests with pytest args: {pytest_arg_list}')
    result = pytest.main(pytest_arg_list, plugins=[params_plugin])
    print(f'Integration tests finished with result {result=}')
    if result != pytest.ExitCode.OK:
        sys.exit(result)
    return result
