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
    build_image = NamedParam(
        name='build_image',
        description='the container image for gardenlinux build (dynamically created)',
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
    skip_cfssl_build = NamedParam(
        name='skip_cfssl_build',
        default='False',
        description='bypass cfssl build, use binaries from base-image',
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
    flavourset = NamedParam(
        name='flavourset',
        default='all',
        description='the flavourset name this task is a part of',
    )
    gardenlinux_build_deb_image = NamedParam(
        name='gardenlinux_build_deb_image',
        description='image to use for package build',
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
    pkg_names = NamedParam(
        name='pkg_names',
        description='list of kernel-package to build (comma separated string)',
    )
    pkg_name = NamedParam(
        name='pkg_name',
        description='name of package to build',
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
    s3_package_path = NamedParam(
        name='package_path_s3_prefix',
        default='packages/pool',
        description='path relative to the root of the s3 bucket to upload the built packages to',
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
    suite = NamedParam(
        name='suite',
        default='bookworm',
        description='Debian release (buster, bullseye, ..)',
    )
    version = NamedParam(
        name='version',
        description='the target version to build / release',
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
