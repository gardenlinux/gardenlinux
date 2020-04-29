import dataclasses
import typing


@dataclasses.dataclass
class NamedParam:
    name: str
    value: str=None


@dataclasses.dataclass
class PipelineMetadata:
    name: str
    namespace: str


@dataclasses.dataclass
class TaskRef:
    name: str


@dataclasses.dataclass
class PipelineTask:
    name: str
    taskRef: TaskRef
    params: typing.List[NamedParam]


@dataclasses.dataclass
class PipelineSpec:
    tasks: typing.List[PipelineTask]
    params: typing.List[NamedParam] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Pipeline:
    metadata: PipelineMetadata
    spec: PipelineSpec
    apiVersion: str='tekton.dev/v1beta1'
    kind: str='Pipeline'


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


@dataclasses.dataclass
class PipelineRunSpec:
    params: typing.List[NamedParam]
    pipelineRef: PipelineRef
    podTemplate: PodTemplate


@dataclasses.dataclass
class PipelineRun:
    spec: PipelineRunSpec
    metadata: PipelineRunMetadata
    apiVersion: str='tekton.dev/v1beta1'
    kind: str='PipelineRun'
