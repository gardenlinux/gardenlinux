from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union, overload

import pytest

from .parse import SUPPORTED_FORMATS, Lines, Parse

# Format detection mapping: extension -> format
FORMAT_EXTENSIONS = {
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".conf": "keyval",
    ".env": "keyval",
}


def _detect_format_from_path(path: str | Path) -> Optional[str]:
    """Detect file format from file extension.

    Args:
        path: File path to analyze.

    Returns:
        Format string if detected, None otherwise.
    """
    p = Path(path)
    ext = p.suffix.lower()
    return FORMAT_EXTENSIONS.get(ext)


class ParseFile:
    """Pytest-facing facade for file-backed parsing operations.

    Provides path-based helpers that delegate to ``Parse``.
    Supports format auto-detection from file extensions.
    """

    def _resolve_format(self, path: str, format: Optional[str]) -> str:
        """Resolve format parameter with auto-detection.

        Args:
            path: File path.
            format: Explicitly provided format, or None for auto-detection.

        Returns:
            Resolved format string.

        Raises:
            ValueError: If format cannot be auto-detected and not provided.
        """
        if format is not None:
            return format

        detected = _detect_format_from_path(path)
        if detected is None:
            raise ValueError(
                f"Cannot auto-detect format for {path}. "
                f"File has no extension or extension is not recognized. "
                f"Please specify format parameter. "
                f"Supported formats: {', '.join(SUPPORTED_FORMATS)}"
            )
        return detected

    def _get_parser(
        self,
        path: str,
        ignore_missing: bool,
        error_context: str,
    ) -> Optional[Parse]:
        """Get Parse instance from file with error handling.

        Args:
            path: File path to read.
            ignore_missing: If True, return None when file is missing or cannot be read.
            error_context: Additional context for error message.

        Returns:
            Parse instance if file exists, or None if missing/unreadable and ignore_missing=True.

        Raises:
            FileNotFoundError: If file is missing and ignore_missing=False.
            PermissionError: If file cannot be read and ignore_missing=False.
        """
        try:
            return Parse.from_file(path)
        except FileNotFoundError as e:
            if ignore_missing:
                return None
            raise FileNotFoundError(f"File not found: {path}. {error_context}") from e
        except PermissionError as e:
            if ignore_missing:
                return None
            raise PermissionError(
                f"Permission denied reading file: {path}. {error_context}"
            ) from e

    @overload
    def parse(
        self,
        path: str,
        *,
        format: Optional[str] = None,
        ignore_comments: bool = True,
        ignore_missing: Literal[False] = False,
    ) -> Any:
        """Parse file and return data structure based on format (when ignore_missing=False)."""
        ...

    @overload
    def parse(
        self,
        path: str,
        *,
        format: Optional[str] = None,
        ignore_comments: bool = True,
        ignore_missing: Literal[True] = ...,
    ) -> Optional[Any]:
        """Parse file and return data structure based on format (when ignore_missing=True)."""
        ...

    def parse(
        self,
        path: str,
        *,
        format: Optional[str] = None,
        ignore_comments: bool = True,
        ignore_missing: bool = False,
    ) -> Optional[Any]:
        """Parse file and return data structure based on format.

        Args:
            path: File to read.
            format: (optional) Format identifier. If None, auto-detect from file extension.
            ignore_comments: (optional, default=True) If True, strip comments where applicable.
            ignore_missing: (optional, default=False) If False, raise exception if file is missing.
                          If True, return None when file is missing.

        Returns:
            Parsed data structure (dict, list, etc.) or None if file missing and ignore_missing=True.

        Raises:
            FileNotFoundError: If file is missing and ignore_missing=False.
            PermissionError: If file cannot be read and ignore_missing=False.

        Example:
            >>> config = parse_file.parse("/etc/config.json")
            >>> assert config["database"]["host"] == "localhost"
            >>> assert config["database"]["port"] == 5432
            >>> assert "missing" not in config["database"]
        """
        parser = self._get_parser(
            path,
            ignore_missing,
            error_context="Cannot parse file.",
        )
        if parser is None:
            return None
        resolved_format = self._resolve_format(path, format)
        return parser.parse(format=resolved_format, ignore_comments=ignore_comments)

    @overload
    def lines(
        self,
        path: str,
        *,
        format: Optional[str] = None,
        comment_char: Optional[Union[str, List[str]]] = None,
        ignore_missing: Literal[False] = False,
        ordered: bool = False,
    ) -> Lines:
        """Get Lines container (when ignore_missing=False)."""
        ...

    @overload
    def lines(
        self,
        path: str,
        *,
        format: Optional[str] = None,
        comment_char: Optional[Union[str, List[str]]] = None,
        ignore_missing: Literal[True] = ...,
        ordered: bool = False,
    ) -> Optional[Lines]:
        """Get Lines container (when ignore_missing=True)."""
        ...

    def lines(
        self,
        path: str,
        *,
        format: Optional[str] = None,
        comment_char: Optional[Union[str, List[str]]] = None,
        ignore_missing: bool = False,
        ordered: bool = False,
    ) -> Optional[Lines]:
        """Get Lines container for line-based operations on a file.

        Supports checking patterns using the `in` operator:
        - String literals: `assert "line" in parse_file.lines(path)`
        - Regex patterns: `assert re.compile(r"\\d+") in parse_file.lines(path)`
        - Lists (unordered): `assert ["lineA", "lineB"] in parse_file.lines(path)`
        - Lists (ordered): `assert ["lineA", "lineB"] in parse_file.lines(path, ordered=True)`

        Args:
            path: File to read.
            format: (optional) Format identifier. If None, auto-detect from file extension.
            comment_char: (optional) Character(s) used for comments. Can be list of strings
                         or None. If None, uses format-specific default.
            ignore_missing: (optional, default=False) If False, raise exception if file is missing.
                          If True, return None when file is missing.
            ordered: (optional, default=False) If True, list patterns must appear in order.

        Returns:
            Lines container instance or None if file missing and ignore_missing=True.

        Raises:
            FileNotFoundError: If file is missing and ignore_missing=False.
            PermissionError: If file cannot be read and ignore_missing=False.

        Example:
            >>> assert "PermitRootLogin yes" in parse_file.lines("/etc/ssh/sshd_config")
            >>> assert re.compile(r"\\d+") in parse_file.lines("/var/log/boot.log")
            >>> assert ["line1", "line2"] in parse_file.lines("/etc/config", ordered=True)
        """
        parser = self._get_parser(
            path,
            ignore_missing,
            error_context="Cannot get lines container.",
        )
        if parser is None:
            return None
        if format is None:
            format = _detect_format_from_path(path)
        return Lines(
            content=parser.content,
            label=parser.label,
            format=format,
            comment_char=comment_char,
            ordered=ordered,
        )


@pytest.fixture
def parse_file() -> ParseFile:
    """Fixture providing the ``ParseFile`` helper for checking file contents."""
    return ParseFile()
