#!/usr/bin/env python3

import argparse
import dataclasses
import enum
import os
import sys
import yaml

own_dir = os.path.abspath(os.path.dirname(__file__))
repo_root = os.path.abspath(os.path.join(own_dir, os.pardir))
ci_dir = os.path.join(repo_root, 'ci')

sys.path.insert(1, ci_dir)

import clean
import glci.util
import glci.model
import paths


def clean_build_result_repository():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cicd-cfg', default='default')
    parser.add_argument('--snapshot-max-age-days', default=14, type=int)

    parsed = parser.parse_args()

    cicd_cfg = glci.util.cicd_cfg(parsed.cicd_cfg)

    print('purging outdated build snapshot manifests')
    clean.clean_single_release_manifests(
        max_age_days=parsed.snapshot_max_age_days,
        cicd_cfg=cicd_cfg,
    )

    print('purging outdated build result snapshot sets (release-candidates)')
    clean.clean_release_manifest_sets(
        max_age_days=parsed.snapshot_max_age_days,
        cicd_cfg=cicd_cfg,
    )

    print('purging loose objects')
    clean.clean_orphaned_objects(cicd_cfg=cicd_cfg)


def gardenlinux_epoch():
    print(glci.model.gardenlinux_epoch_from_workingtree())


def gardenlinux_timestamp():
    epoch = glci.model.gardenlinux_epoch_from_workingtree()

    print(glci.model.snapshot_date(gardenlinux_epoch=epoch))


def _gitrepo():
    import git
    repo = git.Repo(paths.repo_root)
    return repo


def _head_sha():
    repo = _gitrepo()
    return repo.head.commit.hexsha


def _retrieve_argparse(parser):
    repo = _gitrepo()
    parser.add_argument(
        '--committish', '-c',
        default=_head_sha(),
        type=lambda c: repo.git.rev_parse(c),
    )
    parser.add_argument('--cicd-cfg', default='default')
    parser.add_argument(
        '--version',
        default=glci.model._parse_version_from_workingtree(),
    )
    parser.add_argument(
        '--gardenlinux-epoch',
        default=glci.model.gardenlinux_epoch_from_workingtree(),
        type=int,
    )
    parser.add_argument(
        '--build-type',
        type=glci.model.BuildType,
        default=glci.model.BuildType.SNAPSHOT,
    )
    parser.add_argument(
        '--outfile', '-o',
        type=lambda f: open(f, 'w'),
        default=sys.stdout,
    )

    return parser


def retrieve_single_manifest():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--architecture',
        default=glci.model.Architecture.AMD64,
        type=glci.model.Architecture,
    )
    parser.add_argument(
        '--platform',
        choices=[p.name for p in glci.model.platforms()],
    )

    class AddModifierAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string):
            choices = [c.name for c in glci.model.modifiers()]

            raw_modifiers = []
            for v in values.split(','):
                if not (v := v.strip()) in choices:
                    raise ValueError(f'{v} not in {choices}')
                raw_modifiers.append(v)

            normalised_modifiers = glci.model.normalised_modifiers(
                platform=namespace.platform,
                modifiers=raw_modifiers,
            )

            setattr(namespace, self.dest, normalised_modifiers)

    parser.add_argument(
        '--modifier',
        action=AddModifierAction,
        dest='modifiers',
        default=[],
    )
    _retrieve_argparse(parser=parser)

    parsed = parser.parse_args()

    find_release = glci.util.preconfigured(
        func=glci.util.find_release,
        cicd_cfg=glci.util.cicd_cfg(parsed.cicd_cfg)
    )

    release = find_release(
        release_identifier=glci.model.ReleaseIdentifier(
            build_committish=parsed.committish,
            version=parsed.version,
            gardenlinux_epoch=parsed.gardenlinux_epoch,
            architecture=parsed.architecture,
            platform=parsed.platform,
            modifiers=parsed.modifiers,
        )
    )

    if not release:
        print('ERROR: no such release found')
        sys.exit(1)

    with parsed.outfile as f:
        yaml.dump(
            data=dataclasses.asdict(release),
            stream=f,
            Dumper=glci.util.EnumValueYamlDumper,
        )

def retrieve_release_set():
    parser = argparse.ArgumentParser()
    _retrieve_argparse(parser=parser)
    parser.add_argument('--flavourset-name', default='all')

    parsed = parser.parse_args()

    find_release_set = glci.util.preconfigured(
        func=glci.util.find_release_set,
        cicd_cfg=glci.util.cicd_cfg(parsed.cicd_cfg),
    )

    release_set = find_release_set(
        flavourset_name=parsed.flavourset_name,
        build_committish=parsed.committish,
        version=parsed.version,
        gardenlinux_epoch=parsed.gardenlinux_epoch,
        build_type=parsed.build_type,
        absent_ok=True,
    )

    if release_set is None:
        print('Did not find specified release-set')
        sys.exit(1)

    with parsed.outfile as f:
        yaml.dump(
            data=dataclasses.asdict(release_set),
            stream=f,
            Dumper=glci.util.EnumValueYamlDumper,
        )


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
