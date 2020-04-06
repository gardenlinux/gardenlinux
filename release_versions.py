#!/usr/bin/env python3

import enum
import itertools
import os


class IaasType(enum.Enum):
    AWS = 'aws'
    AZURE = 'azure'
    GCP = 'gcp'
    KVM = 'kvm'
    OPEN_STACK = 'openstack'
    VMWARE = 'vmware'


class Arch(enum.Enum):
    X86_64 = 'x86_64'
    ARM_64 = 'arm64'


def effective_version():
    return '0.9.0-SAP'


def image_name(
    arch: Arch,
    iaas: IaasType,
    flavour: str,
    ext: str,
    prefix='gardenlinux'
):
    return f'{prefix}-{arch.value}-{iaas.value}-{flavour}{ext}'


def enumerate_image_names():
    for arch, iaas_type, flavour, ext in itertools.product(
        Arch,
        IaasType,
        ('prod', 'dev'),
        ('.raw', '.tar.gz'),
    ):
        yield image_name(arch=arch, iaas=iaas_type, flavour=flavour, ext=ext)


def version_path(version: str):
    return f'version/{version}'


def main():
    image_names = enumerate_image_names()

    version = '12.3'
    ver_path = version_path(version)

    for image_name in image_names:
        print(os.path.join(ver_path, image_name))

if __name__ == '__main__':
    main()
