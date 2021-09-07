from dataclasses import dataclass
import ccc.aws
import glci.model
import glci.util
import glci.aws
import pytest

'''
This class contains the fixtures needed by most of the integration tests:
- test_params is an instance of TestRunParameters in ci/steps/run_tests.px
  conaining the information about the current pipeline run context

- S3Info see below
- AWSCfg general information how to access AWS account (mostly internal used)
'''

@dataclass
class AWSCfg:
    aws_cfg_name: str
    aws_region: str

@dataclass
class S3Info:
    bucket_name: str
    raw_image_key: str
    target_image_name: str

@pytest.fixture(scope="session")
def aws_cfg(test_params):
    cicd_cfg = glci.util.cicd_cfg(cfg_name=test_params.cicd_cfg_name)
    return AWSCfg(
        aws_cfg_name=cicd_cfg.build.aws_cfg_name,
        aws_region=cicd_cfg.build.aws_region
    )

@pytest.fixture(scope="session")
def s3_bucket(test_params) -> S3Info:
    ''' 
    returns a S3Info object and gives access to the S3 bucket containing the build artifacts
    from the current pipeline run. Typically use to be uploaded to hyperscalers for testing.
    '''
    cicd_cfg = glci.util.cicd_cfg(cfg_name=test_params.cicd_cfg_name)
    find_release = glci.util.preconfigured(
        func=glci.util.find_release,
        cicd_cfg=cicd_cfg,
    )

    release = find_release(
        release_identifier=glci.model.ReleaseIdentifier(
            build_committish=test_params.committish,
            version=test_params.version,
            gardenlinux_epoch=int(test_params.gardenlinux_epoch),
            architecture=glci.model.Architecture(test_params.architecture),
            platform=test_params.platform,
            modifiers=test_params.modifiers,
        ),
    )

    return S3Info(
        raw_image_key=release.path_by_suffix('rootfs.raw').s3_key,
        bucket_name=release.path_by_suffix('rootfs.raw').s3_bucket_name,
        target_image_name=f'integration-test-image-{test_params.committish}',
    )


def pytest_addoption(parser):
    parser.addoption(
        '--local',
        action='store_true',
        help=(
            "run test using local authentication (requires successful authentication prior to "
            " execution, e.g.: 'gcloud auth application-default login' or 'az login')"
        ),
    )
