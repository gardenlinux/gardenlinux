from dataclasses import dataclass
import logging
import os

import yaml

import glci.model
import glci.util
import glci.aws

import ctx
import ccc.aws
import pytest

logger = logging.getLogger(__name__)

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
        self.params=params

    @pytest.fixture(scope="session")
    def test_params(self, request) -> TestRunParameters:
        return self.params


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
    pytest_args: str = None,
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
        architecture = architecture,
        cicd_cfg_name = cicd_cfg_name,
        gardenlinux_epoch = gardenlinux_epoch,
        modifiers = modifiers,
        platform = platform,
        publishing_actions = publishing_actions,
        repo_dir = repo_dir,
        suite = suite,
        snapshot_timestamp = snapshot_timestamp,
        version = version,
        committish = committish
    )

    params_plugin = PyTestParamsPlugin(params)
    if not pytest_args:
        test_dir = os.path.join(repo_dir, "integration_tests")
        if not os.path.exists(test_dir):
            print(f'Path for running tests: {test_dir} does not exist. Stopping')
            return 1
        pytest_arg_list = [test_dir]
    else:
        pytest_arg_list = pytest_args
    print("Running integration tests")
    result = pytest.main(pytest_arg_list, plugins=[params_plugin])
    print(f'Integration tests finished with result {result=}')
    return result
