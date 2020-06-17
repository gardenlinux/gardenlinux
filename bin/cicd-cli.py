#!/usr/bin/env python3

import os
import sys

own_dir = os.path.abspath(os.path.dirname(__file__))
repo_root = os.path.abspath(os.path.join(own_dir, os.pardir))
ci_dir = os.path.join(repo_root, 'ci')

sys.path.insert(1, ci_dir)


def gardenlinux_epoch():
    import glci.model
    print(glci.model.gardenlinux_epoch_from_workingtree())


def gardenlinux_timestamp():
    import glci.model
    epoch = glci.model.gardenlinux_epoch_from_workingtree()

    print(glci.model.snapshot_date(gardenlinux_epoch=epoch))


def main():
    cmd_name = os.path.basename(sys.argv[0]).replace('-', '_')

    module_symbols = sys.modules[__name__]

    func = getattr(module_symbols, cmd_name, None)

    if not func:
        print(f'ERROR: {cmd_name} is not defined')
        sys.exit(1)

    func()


if __name__ == '__main__':
    main()
