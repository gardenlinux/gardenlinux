import pytest
import os
from typing import Iterator, Optional, Union, TypeVar

FIND_RESULT_TYPE_FILE = TypeVar('file')
FIND_RESULT_TYPE_DIR = TypeVar('dir')
FIND_RESULT_TYPE_FILE_AND_DIR = TypeVar('all')


class Find:

    def __init__(self) -> None:
        """
        Initializes the object with default search parameters.

        Attributes:
            same_mnt_only (bool): If True, restricts search to the same mount point.
            root_path (str): The root directory path to start the search from.
            entry_type (Union[FIND_RESULT_TYPE_FILE, FIND_RESULT_TYPE_DIR, FIND_RESULT_TYPE_FILE_AND_DIR]):
                Specifies the type of entries to search for (files, directories, or both).
        """
        self.same_mnt_only: bool = False
        self.root_path: str = '/'
        self.entry_type: Union[FIND_RESULT_TYPE_FILE, FIND_RESULT_TYPE_DIR, FIND_RESULT_TYPE_FILE_AND_DIR] = FIND_RESULT_TYPE_FILE

    def __iter__(self) -> Iterator[str]:
        return iter(list(self._find()))

    def _find(self) -> Iterator[str]:
        # Intentionally don't use pathlib/rglob for performance reasons
        root_dev = os.stat(self.root_path).st_dev
        for dirpath, dirnames, filenames in os.walk(self.root_path):
            if self.entry_type in (FIND_RESULT_TYPE_DIR, FIND_RESULT_TYPE_FILE_AND_DIR):
                for dirname in dirnames:
                    full_path = os.path.join(dirpath, dirname)
                    if self.same_mnt_only and os.stat(full_path).st_dev != root_dev:
                        continue
                    yield full_path
            if self.entry_type in (FIND_RESULT_TYPE_FILE, FIND_RESULT_TYPE_FILE_AND_DIR):
                for filename in filenames:
                    full_path = os.path.join(dirpath, filename)
                    if self.same_mnt_only and os.stat(full_path).st_dev != root_dev:
                        continue
                    yield full_path

@pytest.fixture
def find() -> Find:
    return Find()
