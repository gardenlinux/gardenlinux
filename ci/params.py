import dataclasses
import tkn.model


NamedParam = tkn.model.NamedParam


@dataclasses.dataclass(frozen=True)
class AllParams:
    additional_recipients = NamedParam(
        name='additional_recipients',
    )
    architecture = NamedParam(
        name='architecture',
        default='amd64',
        description='the build architecture (currently, only amd64 is supported)',
    )
    branch = NamedParam(
        name='branch',
        description='branch of git repository',
    )
    build_tasks = tkn.model.NamedParam(
        name='build_tasks',
        default='null',
        description='comma separated list of all tasks building gardenlinux',
    )
    cicd_cfg_name = NamedParam(
        name='cicd_cfg_name',
        default='default',
    )
    cfssl_dir = NamedParam(
        name='cfssl_dir',
        default='/workspace/cfssl',
        description='git wokring dir to clone and build cfssl',
    )
    cfssl_committish = NamedParam(
        name='cfssl_committish',
        description='cfssl branch to clone',
        default='master'
    )
    cfssl_git_url = NamedParam(
        name='cfssl_git_url',
        description='cfssl git url to clone',
        default='https://github.com/cloudflare/cfssl.git'
    )
    ctx_repository_config_name = NamedParam(
        name='ctx_repository_config_name',
        default='gardener-dev',
        description='Name of the component-descriptor repository-context config to use',
    )
    committish = NamedParam(
        name='committish',
        default='main',
        description='commit to build',
    )
    disable_notifications = NamedParam(
        name='disable_notifications',
        default='false',
        description='if true no notification emails are sent',
    )
    flavour_set_name = NamedParam(
        name='flavour_set_name',
        default='all',
        description='the name of the flavour set this task is a part of',
    )
    giturl = NamedParam(
        name='giturl',
        default='ssh://git@github.com/gardenlinux/gardenlinux'
    )
    gardenlinux_epoch = NamedParam(
        name='gardenlinux_epoch',
        description='the gardenlinux epoch to use for as snapshot repo timestamp'
    )
    key_config_name = NamedParam(
        name='key_config_name',
        description='config name of the key to use for signing the packages',
        default='gardenlinux',
    )
    modifiers = NamedParam(
        name='modifiers',
        description='the build modifiers',
    )
    namespace = NamedParam(
            name='namespace',
            description='Namespace of current pipeline run',
        )
    oci_path = NamedParam(
        name='oci_path',
        description='path in OCI-registry where to store output',
        default='eu.gcr.io/gardener-project/test/gardenlinux-test',
    )
    only_recipients = NamedParam(
        name='only_recipients',
    )
    outfile = NamedParam(
        name='outfile',
        default='/workspace/gardenlinux.out',
        description='build result file (parameter is used to pass between steps)'
    )
    pipeline_name = NamedParam(
            name='pipeline_name',
            description='Namespace of current pipeline',
        )
    pipeline_run_name = NamedParam(
            name='pipeline_run_name',
            description='Name of current pipeline run',
        )
    platform = NamedParam(
        name='platform',
        description='the target platform (aws, gcp, metal, kvm, ..)',
    )
    platform_set = NamedParam(
        name='platform_set',
        description='set of platforms built in this pipeline (aws, gcp, metal, kvm, ..)',
    )
    build_targets = NamedParam(
        name='build_targets',
        default='manifests',
        description='how artifacts should be published (glci.model.BuildTarget)',
    )
    pytest_cfg = NamedParam(
        name='pytest_cfg',
        description='configuration name of testsuite in file test_cfg.yaml',
        default='default',
    )
    promote_target = NamedParam(
        name='promote_target',
        default='snapshots',
        description='the promotion target (snapshots|daily|release)',
    )
    repo_dir = NamedParam(
        name='repo_dir',
        default='/workspace/gardenlinux_git',
        description='Gardenlinux working dir',
    )
    snapshot_ctx_repository_config_name = NamedParam(
        name='snapshot_ctx_repository_config_name',
        default='gardener-public',
        description='Name of the snapshot component-descriptor repository-context config to use',
    )
    snapshot_timestamp = NamedParam(
        name='snapshot_timestamp',
        description='the snapshot timestamp (calculated from gardenlinux_epoch)'
    )
    status_dict_str = tkn.model.NamedParam(
        name='status_dict_str',
        default='~',
        description='JSON string with status for all tasks',
    )
    step_image = NamedParam(
        name='step_image',
        description='the container image for CI/CD steps (dynamically created)',
    )
    suite = NamedParam(
        name='suite',
        default='bookworm',
        description='Debian release (buster, bullseye, ..)',
    )
    version = NamedParam(
        name='version',
        description='the target version to build / release',
    )
    garden_build_version = NamedParam(
        name='gardenbuild_version',
        description='the version string passed to garden-build',
    )
    version_label = NamedParam(
        name='version_label',
        description='version label uses as tag for upload',
    )
    status_dict_str = tkn.model.NamedParam(
        name='status_dict_str',
        default='~',
        description='JSON string with status for all tasks',
    )
    pr_id = NamedParam(
        name='pr_id',
        description='The PR-id for PR-builds',
    )
