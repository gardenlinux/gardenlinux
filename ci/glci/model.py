import dataclasses
import datetime
import dateutil.parser
import enum
import typing


class Architecture(enum.Enum):
    '''
    gardenlinux' target architectures, following Debian's naming
    '''
    AMD64 = 'amd64'


class Platform(enum.Enum):
    '''
    gardenlinux' target platforms
    '''
    ALI = 'ali'
    AWS = 'aws'
    AZURE = 'azure'
    BASE = 'base'
    GCP = 'gcp'
    KVM = 'kvm'
    METAL = 'metal'
    OPEN_STACK = 'openstack'
    VMWARE = 'vmware'


class Extension(enum.Enum):
    '''
    extensions that can be added to gardenlinux images (more than one may be chosen)
    '''
    CHOST = 'chost'
    GHOST = 'ghost'
    VHOST = 'vhost'
    _BUILD = '_build'


class Modifier(enum.Enum):
    '''
    modifiers that can be applied to gardenlinux images (more than one may be chosen)
    '''
    PROD = 'prod'


@dataclasses.dataclass
class GardenlinuxFlavour:
    architecture: Architecture
    extensions: typing.Sequence[Extension]
    platform: Platform
    modifiers: typing.Sequence[Modifier]
    fails: typing.Sequence[str]

    def release_files(self, version: str):
        suffices = (
            'InRelease',
            'Release',
            'rootf.tar.xz',
            'rootfs.raw',
            'manifest',
        )

        a = self.architecture.value
        e = '_'.join([e.value for e in sorted(self.extensions)])
        p = self.platform.value
        m = '_'.join([m.value for m in sorted(self.modifiers)])

        for s in suffices:
            yield f'{a}/{p}-{e}-{m}-{version}-{s}'


@dataclasses.dataclass
class GardenlinuxFlavourCombination:
    architectures: typing.List[Architecture]
    platforms: typing.List[Platform]
    extensions: typing.List[typing.List[Extension]]
    modifiers: typing.List[typing.List[Modifier]]
    fails: typing.List[str]


def gardenlinux_epoch(date:typing.Union[str, datetime.datetime]=None):
    '''
    calculate the gardenlinux epoch for the given date (the amount of days since 2020-04-01)
    @param date: date (defaults to today); if str, must be compliant to iso-8601
    '''
    if date is None:
        date = datetime.datetime.today()
    elif isinstance(date, str):
        date = dateutil.parser.isoparse(date)

    if not isinstance(date, datetime.datetime):
        raise ValueError(date)

    epoch_date = datetime.datetime.fromisoformat('2020-04-01')

    gardenlinux_epoch = (date - epoch_date).days

    if gardenlinux_epoch < 0:
        raise ValueError() # must not be older than gardenlinux' inception
    return gardenlinux_epoch
