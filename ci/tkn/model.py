import dataclasses
import typing


@dataclasses.dataclass
class _NamedParamBase:
    name: str


@dataclasses.dataclass
class _NamedParamWithValue(_NamedParamBase):
    value: typing.Optional[str] = None


@dataclasses.dataclass
class _NamedParamWithDefault(_NamedParamBase):
    default: str = None
    description: str = None


def NamedParam(name: str, value: str = None, default: str = None, description: str = None):
    if value is None and default is None:
        return _NamedParamBase(name=name)
    elif value is None and default:
        return _NamedParamWithDefault(name=name, default=default)
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


@dataclasses.dataclass
class TaskSpec:
    params: typing.List[_NamedParamWithValue]
    steps: typing.List[TaskStep]
    workspaces: typing.List[_NamedParamBase] = dataclasses.field(default_factory=list)
    #volumeMounts: typing.List[VolumeMount]=dataclasses.field(default_factory=list)


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
    tasks: typing.List[PipelineTask]
    params: typing.List[NamedParam] = dataclasses.field(default_factory=list)
    workspaces: typing.List[NamedParam] = dataclasses.field(default_factory=list)


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


@dataclasses.dataclass
class PipelineRun:
    spec: PipelineRunSpec
    metadata: PipelineRunMetadata
    apiVersion: str = 'tekton.dev/v1beta1'
    kind: str = 'PipelineRun'
