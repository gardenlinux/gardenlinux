import dataclasses
import datetime
import dateutil.parser
import enum
import typing


class FeatureType(enum.Enum):
    PLATFORM = 'platform'


@dataclasses.dataclass(frozen=True)
class FeaturesCfg:
    include: typing.Tuple[str]


@dataclasses.dataclass(frozen=True)
class PlatformDescriptor:
    '''
    A gardenlinux feature descriptor (parsed from $repo_root/features/*/info.yaml)
    '''
    description: str
    type: FeatureType
    features: FeaturesCfg


class Architecture(enum.Enum):
    '''
    gardenlinux' target architectures, following Debian's naming
    '''
    AMD64 = 'amd64'


class Platform(enum.Enum):
    '''
    gardenlinux' target platforms (exactly one must be chosen)
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


class Modifier(enum.Enum):
    '''
    modifiers that can be applied to gardenlinux images (more than one may be chosen)
    '''
    PROD = '_prod'
    BUILD = '_build'


@dataclasses.dataclass(frozen=True)
class GardenlinuxFlavour:
    architecture: Architecture
    extensions: typing.Tuple[Extension]
    platform: Platform
    modifiers: typing.Tuple[Modifier]

    def canonical_name_prefix(self):
        a = self.architecture.value
        fname_prefix = self.filename_prefix()

        return f'{a}/{fname_prefix}'

    def filename_prefix(self):
        e = '_'.join(sorted([e.value for e in self.extensions]))
        p = self.platform.value
        m = '_'.join(sorted([m.value for m in self.modifiers]))

        return f'{e}-{p}-{m}'

    def release_files(self, version: str):
        suffices = (
            'InRelease',
            'Release',
            'rootf.tar.xz',
            'rootfs.raw',
            'manifest',
        )

        prefix = self.canonical_name_prefix()

        for s in suffices:
            yield f'{prefix}-{version}-{s}'


@dataclasses.dataclass(frozen=True)
class GardenlinuxFlavourCombination:
    architectures: typing.Tuple[Architecture]
    platforms: typing.Tuple[Platform]
    extensions: typing.Tuple[typing.Tuple[Extension]]
    modifiers: typing.Tuple[typing.Tuple[Modifier]]


@dataclasses.dataclass(frozen=True)
class ReleaseFile:
    rel_path: str
    name: str
    suffix: str


@dataclasses.dataclass(frozen=True)
class ReleaseManifest:
    '''
    metadata for a gardenlinux release variant that has been published to a persistency
    store, such as an S3 bucket.
    '''
    build_committish: str
    gardenlinux_epoch: int
    architecture: Architecture
    rel_paths: typing.Tuple[ReleaseFile]
    # TODO: add features/extensions (once conctact was finalised)


class PipelineFlavour(enum.Enum):
    SNAPSHOT = 'snapshot'
    RELEASE = 'release'


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
