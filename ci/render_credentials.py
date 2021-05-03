#!/usr/bin/env python3

import argparse
import json
import os
import yaml

import paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--outfile', default='config.json')

    parsed = parser.parse_args()

    types_path = os.path.join(paths.own_dir, 'cfg', 'cfg_types.yaml')
    with open(types_path) as f:
        types_config = yaml.safe_load(f.read())

    rendered_credentials = {
        'cfg_types': types_config,
    }

    for cfg_type in types_config:
        src_files = types_config[cfg_type]['src']
        cfgs = {}
        for src_file in [f for f in src_files if 'file' in f]:
            file_name = src_file['file']
            src_file_path = os.path.join(paths.own_dir, 'cfg', file_name)
            with open(src_file_path) as f:
                cfgs.update(yaml.safe_load(f.read()))
        rendered_credentials[cfg_type] = cfgs

    with open(parsed.outfile, 'w') as outfile:
        json.dump(rendered_credentials, outfile)


if __name__ == '__main__':
    main()
