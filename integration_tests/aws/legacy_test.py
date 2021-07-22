import logging 
import os
import sys
import yaml

import glci.aws

logger = logging.getLogger(__name__)

def test_legacy(aws_cfg, ec2_client, s3_bucket, test_params):
    snapshot_task_id = glci.aws.import_snapshot(
        ec2_client=ec2_client,
        s3_bucket_name=s3_bucket.bucket_name,
        image_key=s3_bucket.raw_image_key,
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
        image_name=s3_bucket.target_image_name,
    )
    print.info(f'registered {initial_ami_id=}')

    test_config_path = os.path.join(test_params.repo_dir, 'tests', 'test_config.yaml')
    with open(test_config_path) as f:
        existing_config = yaml.safe_load(f.read())

    aws_test_cfg = existing_config['aws']
    aws_test_cfg['region'] = aws_cfg.region()
    aws_test_cfg['access_key_id'] = aws_cfg.access_key_id()
    aws_test_cfg['secret_access_key'] = aws_cfg.secret_access_key()
    aws_test_cfg['ami_id'] = initial_ami_id

    with open(test_config_path, 'w') as f:
        yaml.dump(existing_config, f)

    import pprint
    pprint.pprint(existing_config)

    sys.path.insert(1, os.path.abspath(os.path.join(test_params.repo_dir, 'tests', 'full')))
    import run_full_test

    run_full_test.run_test(
        path=None,
        config=test_config_path,
        debug=True)