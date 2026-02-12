import os
from typing import Optional

import pytest


class EfiVarsUUID:
    def __init__(self, uuid: str, efivars_dir: str):
        self.uuid = uuid.lower()
        self.efivars_dir = efivars_dir

    def _path_for(self, var_name: str) -> Optional[str]:
        name = f"{var_name}-{self.uuid}"
        path = os.path.join(self.efivars_dir, name)
        return path if os.path.exists(path) else None

    def __contains__(self, var_name: str) -> bool:
        return self._path_for(var_name) is not None

    def __getitem__(self, var_name: str) -> bytes:
        path = self._path_for(var_name)
        if not path:
            raise KeyError(var_name)
        with open(path, "rb") as fh:
            return fh.read()


class EfiVars:
    def __init__(self, efivars_dir: str):
        self.efivars_dir = efivars_dir

    def __getitem__(self, uuid: str) -> EfiVarsUUID:
        return EfiVarsUUID(uuid, self.efivars_dir)


@pytest.fixture()
def efivars() -> EfiVars:
    return EfiVars("/sys/firmware/efi/efivars")
