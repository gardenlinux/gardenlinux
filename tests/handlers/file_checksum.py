import hashlib

import pytest


@pytest.fixture
def file_checksum():
    def _checksum(file_path):
        print(f"{file_path=}")
        with open(file_path, "rb") as fd:
            md5sum = hashlib.md5(fd.read(), usedforsecurity=False).hexdigest()
        return md5sum

    return _checksum
