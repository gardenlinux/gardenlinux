from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from .parse import Parse


class FileContent:
    """Pytest-facing facade for file-backed parsing assertions.

    Provides path-based assertion helpers that delegate to ``Parse`` while
    handling missing/permission cases via ``ignore_missing``.
    """

    def assert_line(
        self,
        path: str,
        line: str,
        *,
        invert: bool = False,
        ignore_missing: bool = False,
    ) -> None:
        """Assert that a normalized line exists (or not) in a file.

        Args:
            path: File to read.
            line: Substring to search within lines.
            invert: If True, assert that it does not exist.
            ignore_missing: If True, consider missing/unreadable files as passing.
        """
        try:
            parser = Parse.from_file(path)
        except (FileNotFoundError, PermissionError):
            assert ignore_missing, f"Content or file not found: {path}."
            return
        parser.assert_line(line, invert=invert)

    def assert_lines(
        self,
        path: str,
        lines: List[str],
        *,
        invert: bool = False,
        ignore_missing: bool = False,
    ) -> None:
        """Assert multiple normalized lines appear in order (or not) in a file.

        Args:
            path: File to read.
            lines: Expected lines in order.
            invert: If True, assert that the ordered sequence does not occur.
            ignore_missing: If True, consider missing/unreadable files as passing.
        """
        try:
            parser = Parse.from_file(path)
        except (FileNotFoundError, PermissionError):
            assert ignore_missing, f"Content or file not found: {path}."
            return
        parser.assert_lines(lines, invert=invert)

    def assert_mapping(
        self,
        path: str,
        expected: Dict[str, Any],
        *,
        format: str,
        invert: bool = False,
        ignore_missing: bool = False,
        ignore_comments: bool = True,
    ) -> None:
        """Assert key/value mappings in a structured file.

        Supports formats: ``keyval``, ``ini``, ``json``, ``yaml``, ``toml``.

        Args:
            path: File to read.
            expected: Mapping of expected keys to values.
            format: One of the supported format identifiers.
            invert: If True, assert none of the expected pairs match.
            ignore_missing: If True, consider missing/unreadable files as passing.
            ignore_comments: If True, strip comments where applicable.
        """
        try:
            parser = Parse.from_file(path)
        except (FileNotFoundError, PermissionError):
            assert ignore_missing, f"Content or file not found: {path}."
            return
        parser.assert_mapping(
            expected,
            format=format,
            invert=invert,
            ignore_comments=ignore_comments,
        )


@pytest.fixture
def file_content() -> FileContent:
    """Fixture providing the ``FileContent`` helper for asserting file contents."""
    return FileContent()
