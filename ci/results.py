import dataclasses
import tkn.model


NamedParam = tkn.model.NamedParam


@dataclasses.dataclass(frozen=True)
class AllResults:
    build_result = NamedParam(
        name='build_result',
        description='manifest key if build was sucessful',
    )
