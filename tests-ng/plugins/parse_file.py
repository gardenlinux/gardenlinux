from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

from .parse import MappingResult, Parse


class FileContent:
    """Pytest-facing facade for file-backed parsing operations.

    Provides path-based helpers that delegate to ``Parse`` while
    handling missing/permission cases via ``ignore_missing``.
    """

    def check_line(
        self,
        path: str,
        line: str,
        *,
        invert: bool = False,
        ignore_missing: bool = False,
    ) -> Optional[bool]:
        """Check if a normalized line exists (or not) in a file.

        Args:
            path: File to read.
            line: Substring to search within lines.
            invert: If True, check that it does not exist.
            ignore_missing: If True, return None for missing/unreadable files.

        Returns:
            Optional[bool]: True if condition is met, False otherwise.
                           None if file is missing and ignore_missing=True.
        """
        try:
            parser = Parse.from_file(path)
        except (FileNotFoundError, PermissionError):
            if ignore_missing:
                return None
            raise
        return parser.check_line(line, invert=invert)

    def check_lines(
        self,
        path: str,
        lines: List[str],
        *,
        invert: bool = False,
        ignore_missing: bool = False,
    ) -> Optional[bool]:
        """Check if multiple normalized lines appear in order (or not) in a file.

        Args:
            path: File to read.
            lines: Expected lines in order.
            invert: If True, check that the ordered sequence does not occur.
            ignore_missing: If True, return None for missing/unreadable files.

        Returns:
            Optional[bool]: True if condition is met, False otherwise.
                           None if file is missing and ignore_missing=True.
        """
        try:
            parser = Parse.from_file(path)
        except (FileNotFoundError, PermissionError):
            if ignore_missing:
                return None
            raise
        return parser.check_lines(lines, invert=invert)

    def get_mapping(
        self,
        path: str,
        expected: Dict[str, Any],
        *,
        format: str,
        invert: bool = False,
        ignore_missing: bool = False,
        ignore_comments: bool = True,
    ) -> Optional[MappingResult]:
        """Get mapping check results for a structured file.

        Supports formats: ``keyval``, ``ini``, ``json``, ``yaml``, ``toml``.

        Args:
            path: File to read.
            expected: Mapping of expected keys to values.
            format: One of the supported format identifiers.
            invert: If True, check that none of the expected pairs match.
            ignore_missing: If True, return None for missing/unreadable files.
            ignore_comments: If True, strip comments where applicable.

        Returns:
            Optional[MappingResult]: Result containing matches, missing keys, wrong values.
                                    None if file is missing and ignore_missing=True.
        """
        try:
            parser = Parse.from_file(path)
        except (FileNotFoundError, PermissionError):
            if ignore_missing:
                return None
            raise
        return parser.get_mapping(
            expected,
            format=format,
            invert=invert,
            ignore_comments=ignore_comments,
        )

    def check_list(
        self,
        path: str,
        list_path: str,
        value: Any,
        *,
        format: str,
        invert: bool = False,
        ignore_missing: bool = False,
        ignore_comments: bool = True,
    ) -> Optional[bool]:
        """Check that a value is (or is not) present in a list within a structured file.

        Supports formats: ``json``, ``yaml``, ``toml``.

        Args:
            path: File to read.
            list_path: Dot-separated path to the list (e.g. ``datasource_list`` or
                ``system_info.default_user.groups``).
            value: The value to search for in the list.
            format: One of ``json``, ``yaml``, or ``toml``.
            invert: If True, check that the value is NOT in the list.
            ignore_missing: If True, return None for missing/unreadable files.
            ignore_comments: If True, strip comments where applicable.

        Returns:
            Optional[bool]: True if condition is met, False otherwise.
                           None if file is missing and ignore_missing=True.
        """
        try:
            parser = Parse.from_file(path)
        except (FileNotFoundError, PermissionError):
            if ignore_missing:
                return None
            raise
        return parser.check_list(
            list_path,
            value,
            format=format,
            invert=invert,
            ignore_comments=ignore_comments,
        )


@pytest.fixture
def file_content() -> FileContent:
    """Fixture providing the ``FileContent`` helper for checking file contents."""
    return FileContent()
