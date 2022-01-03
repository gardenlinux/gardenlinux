import dataclasses
import typing


@dataclasses.dataclass(frozen=True, eq=True)
class _NamedParamBase:
    name: str


@dataclasses.dataclass(frozen=True, eq=True)
class _NamedParamWithValue(_NamedParamBase):
    value: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True, eq=True)
class _NamedParamWithDefault(_NamedParamBase):
    default: str = None
    description: str = None


def NamedParam(name: str, value: str = None, default: str = None, description: str = None):
    if value is None and default is None:
        return _NamedParamBase(name=name)
    elif value is None and default:
        return _NamedParamWithDefault(name=name, default=default, description=description)
    return _NamedParamWithValue(name=name, value=value)


@dataclasses.dataclass
class Workspace:
    name: str
    workspace: str
    subPath: str = None


@dataclasses.dataclass
class Metadata:
    name: str


@dataclasses.dataclass
class HostPath:
    path: str
    type: str


@dataclasses.dataclass
class Volume:
    name: str


@dataclasses.dataclass
class HostPathVolume(Volume):
    hostPath: HostPath


@dataclasses.dataclass
class EmptyDirVolume(Volume):
    medium: str


@dataclasses.dataclass
class SecretName():
    secretName: str


@dataclasses.dataclass
class SecretVolume(Volume):
    secret: SecretName


@dataclasses.dataclass
class VolumeMount:
    mountPath: str
    name: str


EnvVar = _NamedParamWithValue


@dataclasses.dataclass
class TaskStep:
    name: str
    image: str
    script: str
    volumeMounts: typing.List[VolumeMount] = dataclasses.field(default_factory=list)
    env: typing.List[EnvVar] = dataclasses.field(default_factory=list)
    resources: typing.Dict = dataclasses.field(default_factory=dict)
    securityContext: typing.Dict = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class TaskSpec:
    params: typing.List[_NamedParamWithValue]
    steps: typing.List[TaskStep]
    workspaces: typing.List[_NamedParamBase] = dataclasses.field(default_factory=list)
    volumes: typing.List[Volume] = dataclasses.field(default_factory=list)
    #volumeMounts: typing.List[VolumeMount]=dataclasses.field(default_factory=list)
    results: typing.List[_NamedParamWithValue] = None


@dataclasses.dataclass
class Task:
    metadata: Metadata
    spec: TaskSpec
    apiVersion: str = 'tekton.dev/v1beta1'
    kind: str = 'Task'


@dataclasses.dataclass
class TaskRef:
    name: str


@dataclasses.dataclass
class PipelineTask:
    name: str
    taskRef: TaskRef
    params: typing.List[NamedParam]
    workspaces: typing.List[Workspace] = dataclasses.field(default_factory=list)
    runAfter: typing.List[str] = dataclasses.field(default_factory=list)
    timeout: str = "1h"


@dataclasses.dataclass
class PipelineSpec:
    _finally: str
    tasks: typing.List[PipelineTask]
    params: typing.List[NamedParam] = dataclasses.field(default_factory=list)
    results: typing.List[_NamedParamWithValue] = None
    workspaces: typing.List[NamedParam] = dataclasses.field(default_factory=list)

    # special methods for handling finally which is a Python keyword
    def __post_init__(self):
        finally_attr = self.__dataclass_fields__.get('_finally')
        finally_attr.name = 'finally'

    def __getattribute__(self, name):
        if name == 'finally':
            name = '_finally'
        return super().__getattribute__(name)

    def __setattribute__(self, name, value):
        if name == 'finally':
            name = '_finally'
        super().__setattribute__(name, value)


@dataclasses.dataclass
class Pipeline:
    metadata: Metadata
    spec: PipelineSpec
    apiVersion: str = 'tekton.dev/v1beta1'
    kind: str = 'Pipeline'


@dataclasses.dataclass
class PipelineRunMetadata:
    name: str
    namespace: str


@dataclasses.dataclass
class PipelineRef:
    name: str


@dataclasses.dataclass
class PodTemplate:
    nodeSelector: dict
    securityContext: dict


@dataclasses.dataclass
class ResourcesClaimRequests:
    storage: str


@dataclasses.dataclass
class ResourcesClaim:
    requests: ResourcesClaimRequests


@dataclasses.dataclass
class VolumeClaimTemplateSpec:
    accessModes: typing.List[str]
    resources: ResourcesClaim


@dataclasses.dataclass
class VolumeClaimTemplate:
    spec: VolumeClaimTemplateSpec


@dataclasses.dataclass
class PipelineRunWorkspace:
    name: str
    volumeClaimTemplate: VolumeClaimTemplate


@dataclasses.dataclass
class PipelineRunSpec:
    params: typing.List[NamedParam]
    pipelineRef: PipelineRef
    podTemplate: PodTemplate
    workspaces: typing.List[PipelineRunWorkspace]
    timeout: str = '1h'


@dataclasses.dataclass
class PipelineRun:
    spec: PipelineRunSpec
    metadata: PipelineRunMetadata
    apiVersion: str = 'tekton.dev/v1beta1'
    kind: str = 'PipelineRun'


@dataclasses.dataclass(frozen=True)
class LimitObject:
    ephemeral_storage: str = None
    memory: str = None
    cpu: float = None


@dataclasses.dataclass(frozen=True)
class Limits:
    type: str
    max: LimitObject
    min: LimitObject
    default: LimitObject
    defaultRequest: LimitObject


@dataclasses.dataclass(frozen=True)
class LimitSpec:
    limits: typing.List[Limits]


@dataclasses.dataclass(frozen=True)
class LimitRange:
    metadata: Metadata
    spec: LimitSpec
    apiVersion: str = 'v1'
    kind: str = 'LimitRange'


def limits_asdict_factory(data):

    def convert_field(obj):
        if obj == 'ephemeral_storage':
            return 'ephemeral-storage'
        else:
            return obj

    return dict((convert_field(k), v) for k, v in data if v is not None)
