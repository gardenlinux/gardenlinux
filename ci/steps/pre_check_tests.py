import glci.model
import glci.util
import glci.s3


def pre_check_tests(
    cicd_cfg_name: str,
    modifiers: str,
    committish: str,
    version: str,
    gardenlinux_epoch: str,
    architecture: str,
    platform: str,
    build_targets: str,
):
    build_target_set = glci.model.BuildTarget.set_from_str(build_targets)

    if not glci.model.BuildTarget.TESTS in build_target_set:
        print('build target "tests" not specified - skipping tests')
        return True

    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    s3_client = glci.s3.s3_client(cicd_cfg)
    s3_bucket_name = cicd_cfg.build.s3_bucket_name

    modifiers = tuple([m for m in modifiers.split(',') if m])

    release_identifier = glci.model.ReleaseIdentifier(
      build_committish=committish,
      version=version,
      gardenlinux_epoch=int(gardenlinux_epoch),
      architecture=glci.model.Architecture(architecture),
      platform=platform,
      modifiers=modifiers,
    )

    release = glci.util.find_release(
      s3_client=s3_client,
      bucket_name=s3_bucket_name,
      release_identifier=release_identifier,
      prefix=glci.model.ReleaseManifest.manifest_key_prefix,
    )
    if release:
      # check if tests have been run and create a marker file
      test_result = release.test_result
      if test_result and test_result.test_result == glci.model.TestResultCode.OK:
          print('Tests have been run successfully previously, will be skipped')
          with open('/workspace/skip_tests', 'w') as f:
              f.write('skip tests (already done)')
      else:
          print('Tests have not been run or failed - running tests')
    else:
      print('no release manifest found - running tests')
