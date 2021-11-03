from __future__ import annotations
import dataclasses
import datetime
import dateutil.parser
import enum
import functools
import itertools
import os
import typing

import dacite
import yaml

import paths

own_dir = os.path.abspath(os.path.dirname(__file__))
repo_root = os.path.abspath(os.path.join(
    own_dir, os.path.pardir, os.path.pardir))


class BuildTarget(enum.Enum):
    BUILD = 'build'                                # compile, link, create arifacts local
    MANIFEST = 'manifest'                          # upload artifacts to S3, create manifest
    COMPONENT_DESCRIPTOR = 'component-descriptor'  # create and upload component descr
    TESTS = 'tests'                                # run gardenlinux integration tests
    PUBLISH = 'publish'                            # upload images to cloud providers
    FREEZE_VERSION = 'freeze-version'              # use version epoch.y.z instead of epoch-commit
    GITHUB_RELEASE = 'github-release'              # create a github release (branch, tag, release)

    @staticmethod
    def set_from_str(comma_separated: str) -> typing.Set[BuildTarget]:
        return {BuildTarget(action.strip()) for action in comma_separated.split(',')}


class FeatureType(enum.Enum):
    '''
    gardenlinux feature types as used in `features/*/info.yaml`

    Each gardenlinux flavour MUST specify exactly one platform and MAY
    specify an arbitrary amount of modifiers.
    '''
    PLATFORM = 'platform'
    MODIFIER = 'modifier'


# TODO: Check feasibility of using proper enum(s)
Platform = str  # see `features/*/info.yaml` / platforms() for allowed values
Modifier = str  # see `features/*/info.yaml` / modifiers() for allowed values


@dataclasses.dataclass(frozen=True)
class Features:
    '''
    a FeatureDescriptor's feature cfg (currently, references to other features, only)
    '''
    include: typing.Tuple[Modifier, ...] = tuple()


@dataclasses.dataclass(frozen=True)
class FeatureDescriptor:
    '''
    A gardenlinux feature descriptor (parsed from $repo_root/features/*/info.yaml)
    '''
    type: FeatureType
    name: str
    description: str = 'no description available'
    features: Features = None

    def included_feature_names(self) -> typing.Tuple[Modifier, ...]:
        '''
        returns the tuple of feature names immediately depended-on by this feature
        '''
        if not self.features:
            return ()
        return self.features.include

    def included_features(self,
                          transitive=True
                          ) -> typing.Generator['FeatureDescriptor', None, None]:
        '''
        returns the tuple of features (transtively) included by this feature
        '''
        included_features = (feature_by_name(name)
                             for name in self.included_feature_names())

        for included_feature in included_features:
            if transitive:
                yield from included_feature.included_features()
            yield included_feature


class Architecture(enum.Enum):
    '''
    gardenlinux' target architectures, following Debian's naming
    '''
    AMD64 = 'amd64'


@dataclasses.dataclass(frozen=True)
class GardenlinuxFlavour:
    '''
    A specific flavour of gardenlinux.
    '''
    architecture: Architecture
    platform: str
    modifiers: typing.Tuple[Modifier, ...]

    def calculate_modifiers(self):
        yield from (
            feature_by_name(f) for f
            in normalised_modifiers(platform=self.platform, modifiers=self.modifiers)
        )

    def canonical_name_prefix(self):
        a = self.architecture.value
        fname_prefix = self.filename_prefix()

        return f'{a}/{fname_prefix}'

    def filename_prefix(self):
        p = self.platform
        m = '_'.join(sorted([m for m in self.modifiers]))

        return f'{p}-{m}'

    def __post_init__(self):
        # validate platform and modifiers
        platform_names = {platform.name for platform in platforms()}
        if not self.platform in platform_names:
            raise ValueError(
                f'unknown platform: {self.platform}. known: {platform_names}'
            )

        modifier_names = {modifier.name for modifier in modifiers()}
        unknown_mods = set(self.modifiers) - modifier_names
        if unknown_mods:
            raise ValueError(
                f'unknown modifiers: {unknown_mods}. known: {modifier_names}'
            )


@dataclasses.dataclass(frozen=True)
class GardenlinuxFlavourCombination:
    '''
    A declaration of a set of gardenlinux flavours. Deserialised from `flavours.yaml`.

    We intend to build a two-digit number of gardenlinux flavours (combinations
    of different architectures, platforms, and modifiers). To avoid tedious and redundant
    manual configuration, flavourset combinations are declared. Subsequently, the
    cross product of said combinations are generated.
    '''
    architectures: typing.Tuple[Architecture, ...]
    platforms: typing.Tuple[Platform, ...]
    modifiers: typing.Tuple[typing.Tuple[Modifier, ...], ...]


@dataclasses.dataclass(frozen=True)
class GardenlinuxFlavourSet:
    '''
    A set of gardenlinux flavours
    '''
    name: str
    flavour_combinations: typing.Tuple[GardenlinuxFlavourCombination, ...]

    def flavours(self):
        for comb in self.flavour_combinations:
            for arch, platf, mods in itertools.product(
                comb.architectures,
                comb.platforms,
                comb.modifiers,
            ):
                yield GardenlinuxFlavour(
                    architecture=arch,
                    platform=platf,
                    modifiers=normalised_modifiers(
                        platform=platf, modifiers=mods),
                )


@dataclasses.dataclass(frozen=True)
class ReleaseFile:
    '''
    base class for release-files
    '''
    name: str
    suffix: str


@dataclasses.dataclass(frozen=True)
class S3_ReleaseFile(ReleaseFile):
    '''
    A single build result file that was (or will be) uploaded to build result persistency store
    (S3).
    '''
    s3_key: str
    s3_bucket_name: str


@dataclasses.dataclass(frozen=True)
class ReleaseIdentifier:
    '''
    a partial ReleaseManifest with all attributes required to unambiguosly identify a
    release.
    '''
    build_committish: str
    version: str
    gardenlinux_epoch: int
    architecture: Architecture
    platform: Platform
    modifiers: typing.Tuple[Modifier, ...]

    def flavour(self, normalise=True) -> GardenlinuxFlavour:
        mods = normalised_modifiers(
            platform=self.platform, modifiers=self.modifiers)

        return GardenlinuxFlavour(
            architecture=self.architecture,
            platform=self.platform,
            modifiers=mods,
        )

    def canonical_release_manifest_key_suffix(self):
        '''
        returns the canonical release manifest key. This key is used as a means to
        unambiguously identify it, and to thus be able to calculate its name if checking
        whether or not the given gardenlinux flavour has already been built and published.

        the key consists of:

        <canonical flavour name>-<version>-<commit-hash[:6]>

        where <canonical flavour name> is calculated from canonicalised_features()
        and <version> is the intended target release version.

        note that the full key should be prefixed (e.g. with manifest_key_prefix)
        '''
        flavour_name = '-'.join((
            f.name for f in canonicalised_features(
                platform=self.platform,
                modifiers=self.modifiers,
            )
        ))
        return f'{flavour_name}-{self.version}-{self.build_committish[:6]}'

    def canonical_release_manifest_key(self):
        return f'{self.manifest_key_prefix}/{self.canonical_release_manifest_key_suffix()}'

    # attrs below are _transient_ (no typehint) and thus exempted from x-serialisation
    # treat as "static final"
    manifest_key_prefix = 'meta/singles'


class PublishedImageBase:
    pass


@dataclasses.dataclass(frozen=True)
class AwsPublishedImage:
    ami_id: str
    aws_region_id: str
    image_name: str


@dataclasses.dataclass(frozen=True)
class AwsPublishedImageSet(PublishedImageBase):
    published_aws_images: typing.Tuple[AwsPublishedImage, ...]
    # release_identifier: typing.Optional[ReleaseIdentifier]


@dataclasses.dataclass(frozen=True)
class AlicloudPublishedImage:
    image_id: str
    region_id: str
    image_name: str


@dataclasses.dataclass(frozen=True)
class AlicloudPublishedImageSet(PublishedImageBase):
    published_alicloud_images: typing.Tuple[AlicloudPublishedImage, ...]


@dataclasses.dataclass(frozen=True)
class GcpPublishedImage(PublishedImageBase):
    gcp_image_name: str
    gcp_project_name: str


class AzureTransportState(enum.Enum):
    PROVISIONAL = 'provisional'
    PUBLISH = 'publishing'
    GO_LIVE = 'going_live'
    RELEASED = 'released'
    FAILED = 'failed'


@dataclasses.dataclass(frozen=True)
class AzurePublishedImage:
    '''
    AzurePublishedImage hold information about the publishing process of an image
    to the Azure Marketplace.

    transport_state reflect the current stage of the image in the publishing process.

    urn is the image identfier used to spawn virtual machines with the image.

    publish_operation_id is the id of the publish operation of the image to the
    Azure Marketplace. At the end of this process step the image is validated and
    can be used for user their subscription get whitelisted.

    golive_operation_id is the id of the go live/release operation of the image
    to the Azure Marketplace. At the end of this process step the image is available
    in all Azure regions for general usage.
    '''

    transport_state: AzureTransportState
    urn: str
    publish_operation_id: str
    golive_operation_id: str


@dataclasses.dataclass(frozen=True)
class OpenstackPublishedImage:
    region_name: str
    image_id: str
    image_name: str


@dataclasses.dataclass(frozen=True)
class OpenstackPublishedImageSet(PublishedImageBase):
    published_openstack_images: typing.Tuple[OpenstackPublishedImage, ...]


@dataclasses.dataclass(frozen=True)
class OciPublishedImage:
    image_reference: str


class TestResultCode(enum.Enum):
    OK = 'success'
    FAILED = 'failure'


@dataclasses.dataclass(frozen=True)
class ReleaseTestResult:
    test_suite_cfg_name: str
    test_result: TestResultCode
    test_timestamp: str


@dataclasses.dataclass(frozen=True)
class ReleaseManifest(ReleaseIdentifier):
    '''
    metadata for a gardenlinux release variant that can be (or was) published to a persistency
    store, such as an S3 bucket.
    '''
    build_timestamp: str
    paths: typing.Tuple[S3_ReleaseFile, ...]
    published_image_metadata: typing.Union[
        AlicloudPublishedImageSet,
        AwsPublishedImageSet,
        AzurePublishedImage,
        GcpPublishedImage,
        OciPublishedImage,
        OpenstackPublishedImageSet,
        None,
    ]

    def path_by_suffix(self, suffix: str):
        for path in self.paths:
            if path.suffix == suffix:
                return path
        else:
            raise ValueError(f'no path with {suffix=} in {self=}')

    def release_identifier(self) -> ReleaseIdentifier:
        return ReleaseIdentifier(
            build_committish=self.build_committish,
            version=self.version,
            gardenlinux_epoch=int(self.gardenlinux_epoch),
            architecture=self.architecture,
            platform=self.platform,
            modifiers=self.modifiers,
        )

    def build_ts_as_date(self) -> datetime.datetime:
        return dateutil.parser.isoparse(self.build_timestamp)


def normalised_modifiers(platform: Platform, modifiers) -> typing.Tuple[str, ...]:
    '''
    determines the transitive closure of all features from the given platform and modifiers,
    and returns the (ASCII-upper-case-sorted) result as a `tuple` of str of all modifiers,
    except for the platform
    '''
    platform = feature_by_name(platform)
    modifiers = {feature_by_name(f) for f in modifiers}

    all_modifiers = set((m.name for m in modifiers))
    for m in modifiers:
        all_modifiers |= set((m.name for m in m.included_features()))

    for f in platform.included_features():
        all_modifiers.add(f.name)

    normalised_features = tuple(sorted(all_modifiers, key=str.upper))

    return normalised_features


def normalised_release_identifier(release_identifier: ReleaseIdentifier):
    modifiers = normalised_modifiers(
        platform=release_identifier.platform,
        modifiers=release_identifier.modifiers,
    )

    return dataclasses.replace(release_identifier, modifiers=modifiers)


def canonicalised_features(platform: Platform, modifiers) -> typing.Tuple[FeatureDescriptor]:
    '''
    calculates the "canonical" (/minimal) tuple of features required to unambiguosly identify
    a gardenlinux flavour. The result is returned as a (ASCII-upper-case-sorted) tuple of
    `FeatureDescriptor`, including the platform (which is always the first element).

    The minimal featureset is determined by removing all transitive dependencies (which are thus
    implied by the retained features).
    '''
    platform = feature_by_name(platform)
    minimal_modifiers = set((feature_by_name(m) for m in modifiers))

    # rm all transitive dependencies from platform
    minimal_modifiers -= set((platform.included_features(), *modifiers))

    # rm all transitive dependencies from modifiers
    for modifier in (feature_by_name(m) for m in modifiers):
        minimal_modifiers -= set(modifier.included_features())

    # canonical name: <platform>-<ordered-features> (UPPER-cased-sort, so _ is after alpha)
    minimal_modifiers = sorted(minimal_modifiers, key=lambda m: m.name.upper())

    return tuple((platform, *minimal_modifiers))


@dataclasses.dataclass(frozen=True)
class OnlineReleaseManifest(ReleaseManifest):
    '''
    a `ReleaseManifest` that was uploaded to a S3 bucket
    '''
    # injected iff retrieved from s3 bucket
    s3_key: str
    s3_bucket: str
    test_result: typing.Optional[ReleaseTestResult]
    logs: typing.Optional[str]

    def stripped_manifest(self):
        raw = dataclasses.asdict(self)
        del raw['s3_key']
        del raw['s3_bucket']

        return ReleaseManifest(**raw)

    @classmethod
    def from_release_manifest(cls, release_manifest: ReleaseManifest, test_result: ReleaseTestResult):
        return OnlineReleaseManifest(
            **release_manifest.__dict__,
            test_result=test_result
        )

    def with_test_result(self,  test_result: ReleaseTestResult):
        return dataclasses.replace(self, test_result=test_result)

    def with_logfile(self,  blob_name: str):
        return dataclasses.replace(self, logs=blob_name)

@dataclasses.dataclass(frozen=True)
class ReleaseManifestSet:
    manifests: typing.Tuple[OnlineReleaseManifest, ...]
    flavour_set_name: str

    # treat as static final
    release_manifest_set_prefix = 'meta/sets'


@dataclasses.dataclass(frozen=True)
class OnlineReleaseManifestSet(ReleaseManifestSet):
    # injected iff retrieved from s3 bucket
    s3_key: str
    s3_bucket: str


class PipelineFlavour(enum.Enum):
    SNAPSHOT = 'snapshot'
    RELEASE = 'release'


class BuildType(enum.Enum):
    SNAPSHOT = 'snapshot'
    DAILY = 'daily'
    RELEASE = 'release'


@dataclasses.dataclass(frozen=True)
class BuildCfg:
    aws_cfg_name: str
    aws_region: str
    s3_bucket_name: str
    gcp_bucket_name: str
    gcp_cfg_name: str
    storage_account_config_name: str
    service_principal_name: str
    plan_config_name: str
    oss_bucket_name: str
    alicloud_region: str
    alicloud_cfg_name: str


@dataclasses.dataclass(frozen=True)
class PackageBuildCfg:
    aws_cfg_name: str
    s3_bucket_name: str


@dataclasses.dataclass(frozen=True)
class AzureMarketplaceCfg:
    offer_id: str
    publisher_id: str
    plan_id: str


@dataclasses.dataclass(frozen=True)
class AzureServicePrincipalCfg:
    tenant_id: str
    client_id: str
    client_secret: str
    subscription_id: str

@dataclasses.dataclass(frozen=True)
class AzureStorageAccountCfg:
    storage_account_name: str
    container_name: str
    access_key: str


@dataclasses.dataclass(frozen=True)
class AzurePublishCfg:
    offer_id: str
    publisher_id: str
    plan_id: str
    service_principal_cfg_name: str
    storage_account_cfg_name: str
    notification_emails: typing.Tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class OpenstackEnvironment:
    auth_url: str
    domain: str
    region: str
    project_name: str
    username: str
    password: str


@dataclasses.dataclass(frozen=True)
class OpenstackPublishCfg:
    environment_cfg_name: str
    image_properties_cfg_name: str


@dataclasses.dataclass(frozen=True)
class OciPublishCfg:
    image_prefix: str


@dataclasses.dataclass(frozen=True)
class PublishCfg:
    azure: AzurePublishCfg
    openstack: OpenstackPublishCfg
    oci: OciPublishCfg


@dataclasses.dataclass(frozen=True)
class NotificationCfg:
    email_cfg_name: str


@dataclasses.dataclass(frozen=True)
class CicdCfg:
    name: str
    build: BuildCfg
    publish: PublishCfg
    notify: NotificationCfg
    package_build: typing.Optional[PackageBuildCfg]


epoch_date = datetime.datetime.fromisoformat('2020-04-01')

# special version value - use "today" as gardenlinux epoch (depend on build-time)
version_today = 'today'


def gardenlinux_epoch(date: typing.Union[str, datetime.datetime] = None):
    '''
    calculates the gardenlinux epoch for the given date (the amount of days since 2020-04-01)
    @param date: date (defaults to today); if str, must be compliant to iso-8601
    '''
    if date is None:
        date = datetime.datetime.today()
    elif isinstance(date, str):
        date = dateutil.parser.isoparse(date)

    if not isinstance(date, datetime.datetime):
        raise ValueError(date)

    gardenlinux_epoch = (date - epoch_date).days + 1

    if gardenlinux_epoch < 1:
        raise ValueError()  # must not be older than gardenlinux' inception
    return gardenlinux_epoch


_gl_epoch = gardenlinux_epoch  # alias for usage in snapshot_date


def snapshot_date(gardenlinux_epoch: int = None):
    '''
    calculates the debian snapshot repository timestamp from the given gardenlinux epoch in the
    format that is expected for said snapshot repository.
    @param gardenlinux_epoch: int, the gardenlinux epoch
    '''
    if gardenlinux_epoch is None:
        gardenlinux_epoch = _gl_epoch()
    gardenlinux_epoch = int(gardenlinux_epoch)
    if gardenlinux_epoch < 1:
        raise ValueError(gardenlinux_epoch)

    time_d = datetime.timedelta(days=gardenlinux_epoch - 1)

    date_str = (epoch_date + time_d).strftime('%Y%m%d')
    return date_str


def _parse_version_from_workingtree(version_file_path: str=paths.version_path) -> str:
    '''
    parses the raw version as configured (defaulting to the contents of `VERSION` file)

    In particular, the contents of `VERSION` (a regular text file) are parsed, with the following
    semantics:

    - lines are stripped
    - after stripping, lines starting with `#` are ignored
    - the first non-empty line (after stripping and comment-stripping) is considered
    - extra lines are ignored
    - from this line, trailing comments are removed (with another subsequent strip)
    - the result is then expected to be one of:
      - a semver-ish version (<major>.<minor>)
      - the string literal `today`
    - the afforementioned assumptions about the version are, however, not validated by this function
    '''
    with open(version_file_path) as f:
        for line in f.readlines():
            if not (line := line.strip()) or line.startswith('#'): continue
            version_str = line
            if '#' in version_str:
                # ignore comments
                version_str = version_str.split('#', 1)[0].strip()
            return version_str
        else:
            raise ValueError(f'did not find uncommented, non-empty line in {version_file_path}')


def next_release_version_from_workingtree(version_file_path: str=paths.version_path):
    version_str = _parse_version_from_workingtree(version_file_path=version_file_path)

    if version_str == version_today:
        # the first release-candidate is always <gardenlinux-epoch>.0
        return f'{gardenlinux_epoch_from_workingtree()}.0'

    # if version is not `today`, we expect to period-separated integers (<epoch>.<patchlevel>)
    epoch, patchlevel = version_str.split('.')

    # ensure the components are both parsable to int
    int(epoch)
    int(patchlevel)

    return version_str


def gardenlinux_epoch_from_workingtree(version_file_path: str=paths.version_path):
    '''
    determines the configured gardenlinux epoch from the current working tree.

    see `_parse_version_from_workingtree` for details about pre-parsing / comment-stripping

    - the version_str is expected to be one of:
      - a semver-ish version (<major>.<minor>)
        - only <major> is considered (and must be parsable to an integer
        - the parsing result is the gardenlinux epoch
      - the string literal `today`
        - in this case, the returned epoch is today's gardenlinux epoch (days since 2020-04-01)
    '''
    version_str = _parse_version_from_workingtree(version_file_path=version_file_path)

    # version_str may either be a semver-ish (gardenlinux only uses two components (x.y))
    try:
        epoch = int(version_str.split('.')[0])
        return epoch
    except ValueError:
        pass

    if version_str == version_today:
        return gardenlinux_epoch()

    raise ValueError(f'{version_str=} was not understood - either semver or "today" are supported')


def _enumerate_feature_files(features_dir=os.path.join(repo_root, 'features')):
    for root, _, files in os.walk(features_dir):
        for name in files:
            if not name == 'info.yaml':
                continue
            yield os.path.join(root, name)


def _deserialise_feature(feature_file):
    with open(feature_file) as f:
        parsed = yaml.safe_load(f)
    # hack: inject name from pardir
    pardir = os.path.basename(os.path.dirname(feature_file))
    parsed['name'] = pardir

    # HACK HACK HACK: patch flags and features back to just `modifiers`
    if parsed['type'] in ('element', 'flag'):
        parsed['type'] = 'modifier'

    return dacite.from_dict(
        data_class=FeatureDescriptor,
        data=parsed,
        config=dacite.Config(
            cast=[
                FeatureType,
                tuple,
            ],
        ),
    )


@functools.lru_cache
def features():
    return {
        _deserialise_feature(feature_file)
        for feature_file in _enumerate_feature_files()
    }


def platforms():
    return {
        feature for feature in features() if feature.type is FeatureType.PLATFORM
    }


def platform_names():
    return {p.name for p in platforms()}


def modifiers():
    return {
        feature for feature in features() if feature.type is FeatureType.MODIFIER
    }


def feature_by_name(feature_name: str):
    for feature in features():
        if feature.name == feature_name:
            return feature
    raise ValueError(feature_name)

