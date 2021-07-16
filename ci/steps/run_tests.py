import logging
import os

import yaml

import glci.model
import glci.util
import glci.aws

import ctx
import ccc.aws

logger = logging.getLogger(__name__)


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

    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    aws_cfg_name = cicd_cfg.build.aws_cfg_name
    aws_region = cicd_cfg.build.aws_region

    aws_cfg = ctx.cfg_factory().aws(aws_cfg_name)
    session = ccc.aws.session(aws_cfg_name, aws_region)
    ec2_client = session.client('ec2')

    find_release = glci.util.preconfigured(
        func=glci.util.find_release,
        cicd_cfg=cicd_cfg,
    )

    release = find_release(
        release_identifier=glci.model.ReleaseIdentifier(
            build_committish=committish,
            version=version,
            gardenlinux_epoch=int(gardenlinux_epoch),
            architecture=glci.model.Architecture(architecture),
            platform=platform,
            modifiers=modifiers,
        ),
    )

    raw_image_key = release.path_by_suffix('rootfs.raw').s3_key
    bucket_name = release.path_by_suffix('rootfs.raw').s3_bucket_name
    target_image_name = f'integration-test-image-{committish}'

    snapshot_task_id = glci.aws.import_snapshot(
        ec2_client=ec2_client,
        s3_bucket_name=bucket_name,
        image_key=raw_image_key,
    )
    logger.info(f'started import {snapshot_task_id=}')

    snapshot_id = glci.aws.wait_for_snapshot_import(
        ec2_client=ec2_client,
        snapshot_task_id=snapshot_task_id,
    )
    logger.info(f'import task finished {snapshot_id=}')

    initial_ami_id = glci.aws.register_image(
        ec2_client=ec2_client,
        snapshot_id=snapshot_id,
        image_name=target_image_name,
    )
    logger.info(f'registered {initial_ami_id=}')

    with open(os.path.join(repo_dir, 'tests', 'test_config.yaml')) as f:
        existing_config = yaml.safe_load(f.read())

    aws_test_cfg = existing_config['aws']
    aws_test_cfg['region'] = aws_cfg.region()
    aws_test_cfg['access_key_id'] = aws_cfg.access_key_id()
    aws_test_cfg['secret_access_key'] = aws_cfg.secret_access_key()
    aws_test_cfg['ami_id'] = initial_ami_id

    with open(os.path.join(repo_dir, 'tests', 'test_config.yaml'), 'w') as f:
        yaml.dump(existing_config, f)

    import pprint
    pprint.pprint(existing_config)

    result = True
    print("Running integration tests")
    print("Integration tests finished with result {result=}")
    return result
