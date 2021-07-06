import enum
import os
import typing

import tkn.model

DEFAULT_IMAGE = 'eu.gcr.io/gardener-project/cc/job-image:1.1363.0'

own_dir = os.path.abspath(os.path.dirname(__file__))
scripts_dir = os.path.join(own_dir)
steps_dir = os.path.join(own_dir, 'steps')


def extend_python_path_snippet(param_name: str):
    sd_name = os.path.basename(scripts_dir)
    return f'sys.path.insert(1,os.path.abspath(os.path.join("$(params.{param_name})","{sd_name}")))'


class ScriptType(enum.Enum):
    BOURNE_SHELL = 'sh'
    PYTHON3 = 'python3'


def task_step_script(
    script_type: ScriptType,
    callable: str,
    params: typing.List[tkn.model.NamedParam],
    repo_path_param: typing.Optional[tkn.model.NamedParam]=None,
    path: str = None,
    inline_script: str = None,
):
    '''
    renders an inline-step-script, prepending a shebang, and appending an invocation
    of the specified callable (passing the given params). Either use path to inline
    script from a file or use inline inline_script to pass script directly

    '''

    if path and inline_script:
        raise ValueError("Either use path or inline_script but not both.")

    if path:
        with open(path) as f:
            script = f.read()
    elif inline_script:
        script = inline_script

    if script_type is ScriptType.PYTHON3:
        shebang = '#!/usr/bin/env python3'
        if repo_path_param:
            preamble = 'import sys,os;' + extend_python_path_snippet(repo_path_param.name)
        else:
            preamble = ''

        args = ','.join((
            f"{param.name.replace('-', '_')}='$(params.{param.name})'" for param in params
        ))
        callable_str = f'{callable}({args})'
    elif script_type is ScriptType.BOURNE_SHELL:
        shebang = '#!/usr/bin/env bash'
        preamble = ''
        args = ' '.join([f'"$(params.{param.name})"' for param in params])
        callable_str = f'{callable} {args}'

    if callable:
        return '\n'.join((
            shebang,
            preamble,
            script,
            callable_str,
        ))
    else:
        return '\n'.join((
            shebang,
            preamble,
            script,
        ))


def clone_step(
    committish: tkn.model.NamedParam,
    git_url: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    step = tkn.model.TaskStep(
        name='clone-repo-step',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'clone_repo_step.py'),
            script_type=ScriptType.PYTHON3,
            callable='clone_and_copy',
            params=[
                committish,
                git_url,
                repo_dir,
            ],
            repo_path_param=repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )

    return step


def cfssl_clone_step(
    name: str,
    committish: tkn.model.NamedParam,
    git_url: tkn.model.NamedParam,
    working_dir: tkn.model.NamedParam,
    gardenlinux_repo_path_param: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    step = tkn.model.TaskStep(
        name=name,
        image=DEFAULT_IMAGE,
        script=task_step_script(
            script_type=ScriptType.PYTHON3,
            path=os.path.join(steps_dir, 'clone_simple_step.py'),
            callable="git_clone('$(params.cfssl_git_url)', '$(params.cfssl_committish)', "
                     "'$(params.cfssl_dir)'); dummy",
            params=[],
            repo_path_param=gardenlinux_repo_path_param,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )

    return step


def upload_results_step(
    architecture: tkn.model.NamedParam,
    cicd_cfg_name: tkn.model.NamedParam,
    committish: tkn.model.NamedParam,
    gardenlinux_epoch: tkn.model.NamedParam,
    modifiers: tkn.model.NamedParam,
    outfile: tkn.model.NamedParam,
    platform: tkn.model.NamedParam,
    publishing_actions: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    version: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='upload-results',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'upload_results_step.py'),
            script_type=ScriptType.PYTHON3,
            callable='upload_results_step',
            params=[
                architecture,
                cicd_cfg_name,
                committish,
                gardenlinux_epoch,
                modifiers,
                outfile,
                platform,
                publishing_actions,
                version,
            ],
            repo_path_param=repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def promote_single_step(
    architecture: tkn.model.NamedParam,
    cicd_cfg_name: tkn.model.NamedParam,
    committish: tkn.model.NamedParam,
    gardenlinux_epoch: tkn.model.NamedParam,
    modifiers: tkn.model.NamedParam,
    platform: tkn.model.NamedParam,
    publishing_actions: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    version: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='promote-step',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'promote_step.py'),
            script_type=ScriptType.PYTHON3,
            callable='promote_single_step',
            params=[
                architecture,
                cicd_cfg_name,
                committish,
                gardenlinux_epoch,
                modifiers,
                platform,
                publishing_actions,
                version,
            ],
            repo_path_param=repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def promote_step(
    cicd_cfg_name: tkn.model.NamedParam,
    committish: tkn.model.NamedParam,
    flavourset: tkn.model.NamedParam,
    gardenlinux_epoch: tkn.model.NamedParam,
    publishing_actions: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    version: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='finalise-promotion-step',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'promote_step.py'),
            script_type=ScriptType.PYTHON3,
            callable='promote_step',
            params=[
                cicd_cfg_name,
                committish,
                flavourset,
                gardenlinux_epoch,
                publishing_actions,
                version,
            ],
            repo_path_param=repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def pre_build_step(
    architecture: tkn.model.NamedParam,
    cicd_cfg_name: tkn.model.NamedParam,
    committish: tkn.model.NamedParam,
    gardenlinux_epoch: tkn.model.NamedParam,
    modifiers: tkn.model.NamedParam,
    platform: tkn.model.NamedParam,
    publishing_actions: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    version: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='prebuild-step',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'pre_build_step.py'),
            script_type=ScriptType.PYTHON3,
            callable='pre_build_step',
            params=[
                architecture,
                cicd_cfg_name,
                committish,
                gardenlinux_epoch,
                modifiers,
                platform,
                publishing_actions,
                version,
            ],
            repo_path_param=repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def release_step(
    committish: tkn.model.NamedParam,
    gardenlinux_epoch: tkn.model.NamedParam,
    giturl: tkn.model.NamedParam,
    publishing_actions: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='release-step',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'release_step.py'),
            script_type=ScriptType.PYTHON3,
            callable='release_step',
            params=[
                committish,
                gardenlinux_epoch,
                giturl,
                publishing_actions,
            ],
            repo_path_param=repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_cfssl_step(
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='build-cfssl-step',
        image='golang:latest',
        script=task_step_script(
            inline_script='''
set -e
set -x

mkdir -p $(params.repo_dir)/cert/cfssl
if [ "$(params.cfssl_fastpath)" != "true" ]; then
  # slow-path build CFSSL from github:
  pushd $(params.cfssl_dir)
  make
  mv bin/* $(params.repo_dir)/cert/cfssl
else
  mkdir -p $(params.repo_dir)/bin
  pushd $(params.repo_dir)/bin
  # fast-path copy binaries from CFSSL github release:
  cfssl_files=( cfssl-bundle_1.5.0_linux_amd64 \\
    cfssl-certinfo_1.5.0_linux_amd64 \\
    cfssl-newkey_1.5.0_linux_amd64 \\
    cfssl-scan_1.5.0_linux_amd64 \\
    cfssljson_1.5.0_linux_amd64 \\
    cfssl_1.5.0_linux_amd64 \\
    mkbundle_1.5.0_linux_amd64 \\
    multirootca_1.5.0_linux_amd64 \\
  )

  len2=`expr length _1.5.0_linux_amd64`
  for file in "${cfssl_files[@]}"; do
    len=`expr length $file`
    outname=${file:0:`expr $len - $len2`}
    wget --no-verbose -O $outname https://github.com/cloudflare/cfssl/releases/download/v1.5.0/${file}
    chmod +x $outname
  done
  mv * $(params.repo_dir)/cert/cfssl
fi
# cleanup workspace to safe some valuable space
popd
rm -rf $(params.cfssl_dir)
''',
            script_type=ScriptType.BOURNE_SHELL,
            callable='',
            params=[],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_make_cert_step(
    repo_dir: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='make-cert',
        image='$(params.gardenlinux_build_deb_image)',
        script=task_step_script(
            inline_script='''
set -e
set -x
cd $(params.repo_dir)/cert
# Note: that make will also build cfssl which was here done in the previous step
# it will skip this step as it already present, this is a bit fragile
make
''',
            script_type=ScriptType.BOURNE_SHELL,
            callable='',
            params=[
                repo_dir,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_package_step(
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='build-package',
        image='$(params.gardenlinux_build_deb_image)',
        script=task_step_script(
            inline_script='''
set -e
set -x

repodir='$(params.repo_dir)'
pkg_name="$(params.pkg_name)"

if [ -z "$SOURCE_PATH" ]; then
  SOURCE_PATH="$(readlink -f ${repodir})"
fi

if [ -z "${pkg_name}" ]; then
  echo "ERROR: no package name given"
  exit 1
fi

echo $(pwd)

MANUALDIR=$(realpath $repodir/packages/manual)
KERNELDIR=$(realpath $repodir/packages/kernel)
CERTDIR=$(realpath $repodir/cert)

export DEBFULLNAME="Garden Linux Maintainers"
export DEBEMAIL="contact@gardenlinux.io"
export BUILDIMAGE="gardenlinux/build-deb"
export BUILDKERNEL="gardenlinux/build-kernel"
echo "MANUALDIR: ${MANUALDIR}"
echo "KERNELDIR: ${KERNELDIR}"
echo "CERTDIR: ${CERTDIR}"

# original makefile uses mounts, replace this by linking required dirs
# to the expexted locations:
# original: mount <gardenlinuxdir>/.packages but this does not exist so just create
ls -l ${CERTDIR}
ln -s ${MANUALDIR} /workspace/manual
ln -s /../Makefile.inside /workspace/Makefile
echo "$(gpgconf --list-dir agent-socket)"
mkdir -p /workspace/.gnupg
ln -s $(gpgconf --list-dir agent-socket) /workspace/.gnupg/S.gpg-agent
ln -s ${CERTDIR}/sign.pub /sign.pub
ln -s ${CERTDIR}/Kernel.sign.full /kernel.full
ln -s ${CERTDIR}/Kernel.sign.crt /kernel.crt
ln -s ${CERTDIR}/Kernel.sign.key /kernel.key

pkg_build_script_path="manual/${pkg_name}"
echo "pkg_build_script_path: ${pkg_build_script_path}"

if [ ! -f "${pkg_build_script_path}" ]; then
  echo "ERROR: Don't know how to build ${pkg_name}"
  exit 1
fi

export BUILDTARGET="${OUT_PATH:-/workspace/pool}"
if [ ! -f "$BUILDTARGET" ]; then
  mkdir "$BUILDTARGET"
fi

echo "Calling package-build script ${pkg_build_script_path}"
${pkg_build_script_path}
''',
            script_type=ScriptType.BOURNE_SHELL,
            callable='',
            params=[],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_kernel_package_step(
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='build-package',
        image='$(params.gardenlinux_build_deb_image)',
        script=task_step_script(
            inline_script='''
set -ex

# split string into an array
echo "Input: $(params.pkg_names)"
IFS=', ' read -r -a packages <<< "$(params.pkg_names)"
echo "Building kernel dependent packages: ${packages[@]}"

repodir='$(params.repo_dir)'

if [ -z "$SOURCE_PATH" ]; then
  SOURCE_PATH="$(readlink -f ${repodir})"
fi

if [ -z "${packages}" ]; then
  echo "ERROR: no package name given"
  exit 1
fi

echo $(pwd)

MANUALDIR=$(realpath $repodir/packages/manual)
KERNELDIR=$(realpath $repodir/packages/kernel)
CERTDIR=$(realpath $repodir/cert)

export DEBFULLNAME="Garden Linux Maintainers"
export DEBEMAIL="contact@gardenlinux.io"
export BUILDIMAGE="gardenlinux/build-deb"
export BUILDKERNEL="gardenlinux/build-kernel"
export WORKDIR="/workspace"
echo "MANUALDIR: ${MANUALDIR}"
echo "KERNELDIR: ${KERNELDIR}"
echo "CERTDIR: ${CERTDIR}"
echo "WORKDIR: ${WORKDIR}"
ls -l ${CERTDIR}

# original makefile uses mounts, replace this by linking required dirs
# to the expexted locations:
# original: mount <gardenlinuxdir>/.packages but this does not exist so just create
ln -s ${MANUALDIR} /workspace/manual
ln -s /../Makefile.inside /workspace/Makefile
echo "$(gpgconf --list-dir agent-socket)"
mkdir -p /workspace/.gnupg
ln -s $(gpgconf --list-dir agent-socket) /workspace/.gnupg/S.gpg-agent
ln -s ${CERTDIR}/sign.pub /sign.pub
ln -s ${CERTDIR}/Kernel.sign.full /kernel.full
ln -s ${CERTDIR}/Kernel.sign.crt /kernel.crt
ln -s ${CERTDIR}/Kernel.sign.key /kernel.key

echo "Checking disk begin end of kernel-packages build:"
df -h
sudo apt-get install --no-install-recommends -y wget quilt vim less

export BUILDTARGET="${OUT_PATH:-/workspace/pool}"
if [ ! -f "$BUILDTARGET" ]; then
mkdir "$BUILDTARGET"
fi

for package in "${packages[@]}"
do
  echo "Building now ${package}"
  pkg_build_script_path="manual/${package}"
  echo "pkg_build_script_path: ${pkg_build_script_path}"

  if [ ! -f "${pkg_build_script_path}" ]; then
    echo "ERROR: Don't know how to build ${package}"
    exit 1
  fi

  pushd "/workspace"
  ${pkg_build_script_path}
  popd
done
echo "Checking disk usage end of kernel-packages build:"
df -h
''',
            script_type=ScriptType.BOURNE_SHELL,
            callable='',
            params=[],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_upload_packages_step(
    repo_dir: tkn.model.NamedParam,
    cicd_cfg_name: tkn.model.NamedParam,
    s3_package_path: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='upload-packages-s3',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'upload_packages.py'),
            script_type=ScriptType.PYTHON3,
            callable='upload_packages',
            repo_path_param=repo_dir,
            params=[
                cicd_cfg_name,
                s3_package_path,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_publish_packages_repository_step(
    cicd_cfg_name: tkn.model.NamedParam,
    s3_package_path: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='publish-package-repository-s3',
        image='$(params.gardenlinux_build_deb_image)',
        script=task_step_script(
            path=os.path.join(steps_dir, 'publish_package_repository.py'),
            script_type=ScriptType.PYTHON3,
            callable='main',
            repo_path_param=repo_dir,
            params=[
                cicd_cfg_name,
                s3_package_path,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_image_step(
    repo_dir: tkn.model.NamedParam,
    suite: tkn.model.NamedParam,
    gardenlinux_epoch: tkn.model.NamedParam,
    timestamp: tkn.model.NamedParam,
    platform: tkn.model.NamedParam,
    modifiers: tkn.model.NamedParam,
    arch: tkn.model.NamedParam,
    committish: tkn.model.NamedParam,
    gardenversion: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    build_image_step_volume_mounts = [vm for vm in volume_mounts]
    build_image_step_volume_mounts.extend([{
        'mountPath': '/dev',
        'name': 'dev',
    }, {
        'mountPath': '/build',
        'name': 'build',
    }])

    build_image_step_resource_config = {
        'requests': {
            'memory': '1Gi',
        },
        'limits': {
            'memory': '1.5Gi',
        },
    }
    build_image_step_security_context = {
        'privileged': True,
        'allowPrivilegeEscalation': True,
        'capabilities': {
          'add': ['SYS_ADMIN'],
        },
    }
    return tkn.model.TaskStep(
        name='build-image',
        image='$(params.build_image)',
        script=task_step_script(
            path=os.path.join(steps_dir, 'build_image.sh'),
            script_type=ScriptType.BOURNE_SHELL,
            callable='build_image',
            repo_path_param=repo_dir,
            params=[
                # !DO NOT CHANGE ORDER!
                suite,
                gardenlinux_epoch,
                timestamp,
                platform,
                modifiers,
                arch,
                committish,
                gardenversion
            ],
        ),
        volumeMounts=build_image_step_volume_mounts,
        env=env_vars,
        resources=build_image_step_resource_config,
        securityContext=build_image_step_security_context,
    )


def build_base_image_step(
    repo_dir: tkn.model.NamedParam,
    oci_path: tkn.model.NamedParam,
    version_label: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='basebuild',
        image='eu.gcr.io/gardener-project/cc/job-image-kaniko:1.1363.0',
        script=task_step_script(
            path=os.path.join(steps_dir, 'build_base_image.py'),
            script_type=ScriptType.PYTHON3,
            callable='build_base_image',
            repo_path_param=repo_dir,
            params=[
                oci_path,
                repo_dir,
                version_label,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def notify_step(
    cicd_cfg_name: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    git_url: tkn.model.NamedParam,
    status_dict_str: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='notify-status',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'notify.py'),
            script_type=ScriptType.PYTHON3,
            callable='send_notification',
            repo_path_param=repo_dir,
            params=[
                cicd_cfg_name,
                git_url,
                status_dict_str,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def get_logs_step(
    repo_dir: tkn.model.NamedParam,
    pipeline_run: tkn.model.NamedParam,
    namespace: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='get-logs',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'get_logs.py'),
            script_type=ScriptType.PYTHON3,
            callable='getlogs',
            repo_path_param=repo_dir,
            params=[
                repo_dir,
                pipeline_run,
                namespace,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )
