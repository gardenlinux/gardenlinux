import os

import ctx


def write_key_to_file(
    target_file_path: str,
    key_config_name: str,
):
    cfg_factory = ctx.cfg_factory()
    key_config = cfg_factory._cfg_element(cfg_type_name='gpg_key', cfg_name=key_config_name)
    with open(target_file_path, 'w') as f:
        f.write(key_config.raw['private'])


def write_key(repo_dir, key_config_name):
    write_key_to_file(
        os.path.join(repo_dir, 'cert', 'private.key'),
        key_config_name,
    )
