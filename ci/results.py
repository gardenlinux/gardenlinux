import dataclasses
import tkn.model


NamedParam = tkn.model.NamedParam


@dataclasses.dataclass(frozen=True)
class AllResults:
    build_result = NamedParam(
        name='build_result',
        description='manifest key if build was successful',
    )
    manifest_set_key_result = NamedParam(
        name='manifest_set_key_result',
        description='s3 key with timestamp when manifest-set is created',
    )
