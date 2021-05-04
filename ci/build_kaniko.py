import dataclasses
from genericpath import exists
import os
import subprocess
import sys

import ccc.oci
import oci
import oci.model as om
import oci.util as ou
import concourse.steps.build_oci_image as conf_writer

@dataclasses.dataclass
class _Kaniko_save_fs_state():
    certifi_certs_path: str = None
    certifi_bak: str = None
    ca_certs_path: str = None
    ca_certs_bak: str = None
    python_lib_dir: str = None
    python_bak_dir: str = None
    bin_dir: str = None
    bin_bak_dir: str = None

def _prepare_for_kaniko_purgefs() -> _Kaniko_save_fs_state:
    # XXX ugly hack: early-import so we survive kaniko's rampage (will purge container during build)
    import ccc.secrets_server
    import model.container_registry
    import model.elasticsearch
    import concurrent.futures
    import concurrent.futures.thread

    # XXX another hack: save truststores from being purged by kaniko's multistage-build
    import certifi
    certifi_bak = os.path.join('/', 'kaniko', 'cacert.pem')
    certifi_certs_path = certifi.where()
    if not os.path.exists(certifi_bak):
      os.link(certifi_certs_path, certifi_bak)
    
    ca_certs_bak = os.path.join('/', 'kaniko', 'ca-certificates.crt')
    ca_certs_path = os.path.join('/', 'etc', 'ssl', 'certs', 'ca-certificates.crt')
    if not os.path.exists(ca_certs_bak):
      os.link(ca_certs_path, ca_certs_bak)

    # XXX final hack (I hope): cp entire python-dir
    import sys
    import shutil
    if sys.version_info.minor >= 9 or sys.version_info.major > 3:
      lib_dir = os.path.join(sys.prefix, sys.platlibdir)
    else:
      lib_dir = os.path.join(sys.prefix, 'lib')

    python_lib_dir = os.path.join(lib_dir, f'python{sys.version_info.major}.{sys.version_info.minor}')
    python_bak_dir = os.path.join('/', 'kaniko', 'python.bak')
    if not os.path.exists(python_bak_dir) and os.path.isdir(python_lib_dir):
        shutil.copytree(python_lib_dir, python_bak_dir)

    bin_dir = '/bin'
    bin_bak_dir = os.path.join('/', 'kaniko', 'bin.bak')
    if not os.path.exists(bin_bak_dir):
       shutil.copytree(bin_dir, bin_bak_dir)

    # HACK remove '/usr/lib' and '/cc/utils' to avoid pip from failing in the first stage of builds
    shutil.rmtree(path=os.path.join('/', 'usr', 'lib'), ignore_errors=True)
    shutil.rmtree(path=os.path.join('/', 'cc', 'utils'), ignore_errors=True)

    return _Kaniko_save_fs_state(
        certifi_certs_path = certifi_certs_path,
        certifi_bak = certifi_bak,
        ca_certs_path = ca_certs_path,
        ca_certs_bak = ca_certs_bak,
        python_lib_dir = python_lib_dir,
        python_bak_dir = python_bak_dir,
        bin_dir = bin_dir,
        bin_bak_dir = bin_bak_dir,
    ) 

def _restore_after_kaniko_purgefs(state: _Kaniko_save_fs_state):
    import shutil
    os.makedirs(os.path.dirname(state.certifi_certs_path), exist_ok=True)
    if not os.path.exists(state.certifi_certs_path):
      os.link(state.certifi_bak, state.certifi_certs_path)

    os.makedirs(os.path.dirname(state.ca_certs_path), exist_ok=True)
    if not os.path.exists(state.ca_certs_path):
      os.link(state.ca_certs_bak, state.ca_certs_path)

    if not os.path.exists(state.python_lib_dir):
      os.symlink(state.python_bak_dir, state.python_lib_dir)

    shutil.copytree(state.bin_bak_dir, state.bin_dir, dirs_exist_ok=True)

def build_and_push_kaniko(
    dockerfile_path: str,
    context_dir: str,
    image_push_path: str,
    image_tag: str,
    additional_tags = None,
    build_args = None,
    home_dir = os.getenv('HOME', default=os.getcwd()),
):

    print("--- Writing kaniko config files ---")
    docker_cfg_dir = os.path.join(home_dir, '.docker')
    os.makedirs(docker_cfg_dir, exist_ok=True)
    docker_cfg_path = os.path.join(docker_cfg_dir, 'config.json')

    conf_writer.write_docker_cfg(
      dockerfile_path=dockerfile_path,
      docker_cfg_path=docker_cfg_path,
    )
    
    purge_state = _prepare_for_kaniko_purgefs()

    print("--- Doing kaniko build ---")
    subproc_env = os.environ.copy()
    subproc_env['HOME'] = home_dir
    subproc_env['GOOGLE_APPLICATION_CREDENTIALS'] = docker_cfg_path
    subproc_env['PATH'] = os.path.join('/', 'kaniko', 'bin')

    oci_client = ccc.oci.oci_client()

    image_outfile = os.path.basename(image_push_path) + '.tar'
    image_ref = f'{image_push_path}:{image_tag}'

    if os.path.exists('/kaniko/executor'):
        kaniko_executor = '/kaniko/executor'
    else:
        kaniko_executor = '/bin/kaniko'

    kaniko_argv = [
        kaniko_executor,
        '--no-push',
        '--dockerfile', 'Dockerfile',
        '--context', f'{context_dir}',
        '--tarPath', image_outfile,
        '--destination', image_ref,
   ]
    for arg in build_args:
        kaniko_argv.append('--build-arg')
        kaniko_argv.append(arg)

    print(f'running kaniko-build {kaniko_argv=}')
    # avoid that kaniko logs appear before our prints
    sys.stdout.flush()
    res = subprocess.run(
        kaniko_argv,
        env=subproc_env,
        check=True,
    )
    print(f'wrote image to {image_outfile=} attempting to push, exit-code: {res.returncode}')

    _restore_after_kaniko_purgefs(purge_state)

    print(f'publishing to {image_ref=}, {additional_tags=}')
    manifest_mimetype = om.DOCKER_MANIFEST_SCHEMA_V2_MIME
    oci.publish_container_image_from_kaniko_tarfile(
        image_tarfile_path=image_outfile,
        oci_client=oci_client,
        image_reference=image_ref,
        additional_tags=additional_tags,
        manifest_mimetype=manifest_mimetype,
    )
