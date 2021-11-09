import json
import os
import sys

import dacite
import glci.model
import glci.util
import glci.s3


def upload_test_results(
    architecture: str,
    cicd_cfg_name: str,
    committish: str,
    gardenlinux_epoch: str,
    modifiers: str,
    platform: str,
    build_targets: str,
    repo_dir: str,
    version: str,
):
    build_target_set = glci.model.BuildTarget.set_from_str(build_targets)

    if not glci.model.BuildTarget.TESTS in build_target_set:
        print('build target "tests" not specified - nothing to upload')
        sys.exit(0)

    if not glci.model.BuildTarget.MANIFEST in build_target_set:
        print('build target "manifest" not specified - skipping uploads')
        sys.exit(0)

    if os.path.exists('/workspace/skip_tests'):
        print('Tests already uploaded in previous run, skipping upload step')
        sys.exit(0)

    manifest = glci.model.ReleaseManifest(
      build_committish=committish,
      version=version,
      build_timestamp=None,
      gardenlinux_epoch=gardenlinux_epoch,
      architecture=glci.model.Architecture(architecture).value,
      platform=platform,
      modifiers=modifiers,
      paths=None,
      published_image_metadata=None,
    )

    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    s3_client = glci.s3.s3_client(cicd_cfg)
    aws_cfg_name = cicd_cfg.build.aws_cfg_name
    s3_bucket_name = cicd_cfg.build.s3_bucket_name
    modifiers = tuple(modifiers.split(','))

    test_result_file_name = os.path.join(repo_dir, 'test_results.json')
    if not os.path.exists(test_result_file_name):
        print("No file found with test results, tests did not run, won't upload.")
        print("Exiting with failure, see logs from previous steps")
        sys.exit(1)

    print(f'Loading test-results from previous steps from: {test_result_file_name}')
    with open(test_result_file_name, 'r') as f:
        test_result = json.load(f)

    print(f'Load local test-results, found: {test_result=}')
    if not test_result:
        print(f'Failed to load test results from {test_result_file_name}')
        sys.exit(1)

    # convert dict to dataclass:
    test_result =  dacite.from_dict(
            data_class=glci.model.ReleaseTestResult,
            data=test_result,
            config=dacite.Config(cast=[glci.model.TestResultCode]),
        )

    print(f'downloading release manifest from s3 {aws_cfg_name=} {s3_bucket_name=}')
    find_release = glci.util.preconfigured(
        func=glci.util.find_release,
        cicd_cfg=glci.util.cicd_cfg(cicd_cfg_name)
    )
    manifest = find_release(
        release_identifier=glci.model.ReleaseIdentifier(
            build_committish=committish,
            version=version,
            gardenlinux_epoch=int(gardenlinux_epoch),
            architecture=glci.model.Architecture(architecture),
            platform=platform,
            modifiers=modifiers,
        ),
        s3_client=s3_client,
        bucket_name=s3_bucket_name,
    )

    if not manifest:
        print('Could not find release-manifest, uploading test results failed.')
        sys.exit(1)

    print(f'downloaded manifest: {type(manifest)=}')

    # copy manifest and attach test_results
    new_manifest = manifest.with_test_result(glci.util._json_serialisable_manifest(test_result))
    # upload manifest
    manifest_path_suffix = manifest.canonical_release_manifest_key_suffix()
    manifest_path = f'{glci.model.ReleaseManifest.manifest_key_prefix}/{manifest_path_suffix}'
    glci.util.upload_release_manifest(
      s3_client=s3_client,
      bucket_name=s3_bucket_name,
      key=manifest_path,
      manifest=new_manifest,
    )
    print(f'uploaded updated manifest: {new_manifest.test_result=}')

    if test_result.test_result != glci.model.TestResultCode.OK:
        print('Upload successful')
        print('Step is failing due to previous test errors, see logs from previous steps')
        sys.exit(1)
