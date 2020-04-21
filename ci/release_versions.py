#!/usr/bin/env python3

import dacite
import itertools
import os
import yaml

import glci.model


def enumerate_build_flavours(build_yaml: str='build.yaml'):
    with open(build_yaml) as f:
        parsed = yaml.safe_load(f)

    GardenlinuxFlavour = glci.model.GardenlinuxFlavour
    GardenlinuxFlavourCombination = glci.model.GardenlinuxFlavourCombination
    Architecture = glci.model.Architecture
    Platform = glci.model.Platform
    Extension = glci.model.Extension
    Modifier = glci.model.Modifier

    flavour_combinations = [
        dacite.from_dict(
            data_class=GardenlinuxFlavourCombination,
            data=flavour_def,
            config=dacite.Config(
                cast=[Architecture, Platform, Extension, Modifier],
            )
        ) for flavour_def in parsed['flavours']
    ]
    for comb in flavour_combinations:
        for arch, platf, exts, mods in itertools.product(
            comb.architectures,
            comb.platforms,
            comb.extensions,
            comb.modifiers,
        ):
            yield GardenlinuxFlavour(
                architecture=arch,
                platform=platf,
                extensions=exts,
                modifiers=mods,
                fails=comb.fails, # not part of variant
            )


def print_build_flavours(version:str, build_yaml:str='../build.yaml'):
    for flavour in enumerate_build_flavours(build_yaml=build_yaml):
        for fn in flavour.release_files(version=version):
            print(fn)


def version_path(version: str):
    return f'version/{version}'


def main():
    version = '18-deadbeef'

    print_build_flavours(version=version)


if __name__ == '__main__':
    main()
