from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pytest

from .parse import SUPPORTED_FORMATS, Parse, ValidationResult

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
            ignore_missing: If True, return None when file is missing.
            error_context: Additional context for error message.

        Returns:
            Parse instance if file exists, or None if missing and ignore_missing=True.

        Raises:
            FileNotFoundError: If file is missing and ignore_missing=False.
        """
        try:
            return Parse.from_file(path)
        except (FileNotFoundError, PermissionError) as e:
            if ignore_missing:
                return None
            raise FileNotFoundError(
                f"File not found or cannot be read: {path}. {error_context}"
            ) from e

    def has_line(
        self,
        path: str,
        pattern: str,
        *,
        format: Optional[str] = None,
        comment_char: Optional[List[str]] = None,
        ignore_missing: bool = False,
    ) -> bool:
        """Check if a line exists in a file, automatically filtering comments.

        Args:
            path: File to read.
            pattern: The substring to search within lines.
            format: (optional) Format identifier. If None, auto-detect from file extension.
            comment_char: (optional) Character(s) used for comments. Can be list of strings
                         or None. If None, uses format-specific default.
                         For INI format, defaults to [";", "#"].
            ignore_missing: (optional, default=False) If False, raise exception if file is missing.
                          If True, return False when file is missing.

        Returns:
            bool: True if condition is met, False otherwise.

        Raises:
            FileNotFoundError: If file is missing and ignore_missing=False.
            PermissionError: If file cannot be read and ignore_missing=False.

        Example:
            >>> parse_file.has_line("/etc/ssh/sshd_config", "PermitRootLogin yes")
            >>> parse_file.has_line("/etc/config.json", "key", format="json")  # No comment filtering for JSON
            >>> parse_file.has_line("/etc/config.ini", "key")  # Supports both ; and # comments
        """
        parser = self._get_parser(
            path,
            ignore_missing,
            error_context=f"Cannot check for line pattern '{pattern}'.",
        )
        if parser is None:
            return False
        if format is None:
            format = _detect_format_from_path(path)
        return parser.has_line(pattern, format=format, comment_char=comment_char)

    def has_lines(
        self,
        path: str,
        patterns: List[str],
        *,
        order: bool = True,
        format: Optional[str] = None,
        comment_char: Optional[List[str]] = None,
        ignore_missing: bool = False,
    ) -> bool:
        """Check if multiple lines exist in a file, with comment filtering and optional ordering.

        Args:
            path: File to read.
            patterns: List of patterns to search for.
            order: (optional, default=True) If True, check patterns appear in order. If False, check all exist.
            format: (optional) Format identifier. If None, auto-detect from file extension.
            comment_char: (optional) Character(s) used for comments. Can be list of strings
                         or None. If None, uses format-specific default.
                         For INI format, defaults to [";", "#"].
            ignore_missing: (optional, default=False) If False, raise exception if file is missing.
                          If True, return False when file is missing.

        Returns:
            bool: True if condition is met, False otherwise.

        Raises:
            FileNotFoundError: If file is missing and ignore_missing=False.
            PermissionError: If file cannot be read and ignore_missing=False.
        """
        parser = self._get_parser(
            path,
            ignore_missing,
            error_context=f"Cannot check for line patterns: {patterns}.",
        )
        if parser is None:
            return False
        if format is None:
            format = _detect_format_from_path(path)
        return parser.has_lines(
            patterns, order=order, format=format, comment_char=comment_char
        )

    def regex(
        self,
        path: str,
        pattern: str,
        *,
        flags: int = 0,
        ignore_missing: bool = False,
    ) -> Optional[Any]:
        """Apply regex pattern to file content and return match object.

        Args:
            path: File to read.
            pattern: Regular expression pattern to search for.
            flags: (optional, default=0) Regex flags (e.g., re.IGNORECASE, re.MULTILINE).
            ignore_missing: (optional, default=False) If False, raise exception if file is missing.
                          If True, return None when file is missing.

        Returns:
            Match object if found, None otherwise.

        Raises:
            FileNotFoundError: If file is missing and ignore_missing=False.
            PermissionError: If file cannot be read and ignore_missing=False.

        Example:
            >>> match = parse_file.regex("/var/log/boot.log", r"Boot completed in ([\\d.]+)s")
        """
        parser = self._get_parser(
            path,
            ignore_missing,
            error_context=f"Cannot apply regex pattern '{pattern}'.",
        )
        if parser is None:
            return None
        return parser.regex(pattern, flags=flags)

    def include(
        self,
        path: str,
        list_path: str,
        value: Any,
        *,
        format: Optional[str] = None,
        ignore_comments: bool = True,
        ignore_missing: bool = False,
    ) -> bool:
        """Check that a value is present in a list within a structured file.

        Args:
            path: File to read.
            list_path: Dot-separated path to the list.
            value: The value to search for in the list.
            format: (optional) Format identifier. If None, auto-detect from file extension.
            ignore_comments: (optional, default=True) If True, strip comments where applicable.
            ignore_missing: (optional, default=False) If False, raise exception if file is missing.
                          If True, return False when file is missing.

        Returns:
            bool: True if value is in the list, False otherwise.

        Raises:
            FileNotFoundError: If file is missing and ignore_missing=False.
            PermissionError: If file cannot be read and ignore_missing=False.

        Example:
            >>> parse_file.include("/etc/users.json", "groups", "admin")
        """
        parser = self._get_parser(
            path,
            ignore_missing,
            error_context=f"Cannot check if value '{value}' is in list at path '{list_path}'.",
        )
        if parser is None:
            return False
        resolved_format = self._resolve_format(path, format)
        return parser.include(
            list_path, value, format=resolved_format, ignore_comments=ignore_comments
        )

    def get_value(
        self,
        path: str,
        key_path: str,
        *,
        format: Optional[str] = None,
        ignore_comments: bool = True,
        ignore_missing: bool = False,
    ) -> Optional[Any]:
        """Get value at a path in a structured file.

        Args:
            path: File to read.
            key_path: Dot-separated path to the key (e.g. ``database.host``).
            format: (optional) Format identifier. If None, auto-detect from file extension.
            ignore_comments: (optional, default=True) If True, strip comments where applicable.
            ignore_missing: (optional, default=False) If False, raise exception if file is missing.
                          If True, return None when file is missing.

        Returns:
            Value at the path if found, None otherwise.

        Raises:
            FileNotFoundError: If file is missing and ignore_missing=False.
            PermissionError: If file cannot be read and ignore_missing=False.

        Example:
            >>> parse_file.get_value("/etc/config.json", "database.host")
        """
        parser = self._get_parser(
            path,
            ignore_missing,
            error_context=f"Cannot get value at path '{key_path}'.",
        )
        if parser is None:
            return None
        resolved_format = self._resolve_format(path, format)
        return parser.get_value(
            key_path, format=resolved_format, ignore_comments=ignore_comments
        )

    def get_values(
        self,
        path: str,
        expected: Dict[str, Any],
        *,
        format: Optional[str] = None,
        ignore_comments: bool = True,
        ignore_missing: bool = False,
    ) -> ValidationResult:
        """Verify that multiple key-value pairs match expected values.

        Args:
            path: File to read.
            expected: Dictionary mapping key_path to expected_value (e.g. ``{"database.host": "localhost"}``).
            format: (optional) Format identifier. If None, auto-detect from file extension.
            ignore_comments: (optional, default=True) If True, strip comments where applicable.
            ignore_missing: (optional, default=False) If False, raise exception if file is missing.
                          If True, return ValidationResult with all keys marked as missing when file is missing.

        Returns:
            ValidationResult with missing and wrong values.

        Raises:
            FileNotFoundError: If file is missing and ignore_missing=False.
            PermissionError: If file cannot be read and ignore_missing=False.

        Example:
            >>> result = parse_file.get_values(
            ...     "/etc/config.json",
            ...     {"database.host": "localhost", "database.port": 5432}
            ... )
            >>> assert result, f"Missing: {result.missing}, Wrong: {result.wrong}"
        """
        parser = self._get_parser(
            path,
            ignore_missing,
            error_context=f"Cannot verify values: {list(expected.keys())}.",
        )
        if parser is None:
            # File is missing and ignore_missing=True, mark all keys as missing
            return ValidationResult(
                missing=list(expected.keys()), wrong={}, all_match=False
            )
        resolved_format = self._resolve_format(path, format)
        return parser.get_values(
            expected, format=resolved_format, ignore_comments=ignore_comments
        )

    def has_key(
        self,
        path: str,
        key_path: str,
        *,
        format: Optional[str] = None,
        ignore_comments: bool = True,
        ignore_missing: bool = False,
    ) -> bool:
        """Check if a key/path exists in a structured file.

        Args:
            path: File to read.
            key_path: Dot-separated path to the key (e.g. ``database.host``).
            format: (optional) Format identifier. If None, auto-detect from file extension.
            ignore_comments: (optional, default=True) If True, strip comments where applicable.
            ignore_missing: (optional, default=False) If False, raise exception if file is missing.
                          If True, return False when file is missing.

        Returns:
            bool: True if key exists, False otherwise.

        Raises:
            FileNotFoundError: If file is missing and ignore_missing=False.
            PermissionError: If file cannot be read and ignore_missing=False.

        Example:
            >>> parse_file.has_key("/etc/config.json", "database.host")
        """
        parser = self._get_parser(
            path,
            ignore_missing,
            error_context=f"Cannot check if key '{key_path}' exists.",
        )
        if parser is None:
            return False
        resolved_format = self._resolve_format(path, format)
        return parser.has_key(
            key_path, format=resolved_format, ignore_comments=ignore_comments
        )

    def has_keys(
        self,
        path: str,
        key_paths: List[str],
        *,
        format: Optional[str] = None,
        ignore_comments: bool = True,
        ignore_missing: bool = False,
    ) -> ValidationResult:
        """Check if multiple keys/paths exist in a structured file.

        Args:
            path: File to read.
            key_paths: List of dot-separated paths to keys (e.g. ``["database.host", "database.port"]``).
            format: (optional) Format identifier. If None, auto-detect from file extension.
            ignore_comments: (optional, default=True) If True, strip comments where applicable.
            ignore_missing: (optional, default=False) If False, raise exception if file is missing.
                          If True, return ValidationResult with all keys marked as missing when file is missing.

        Returns:
            ValidationResult with missing keys (keys that don't exist). The wrong dictionary will be empty
            since this method only checks existence, not values.

        Raises:
            FileNotFoundError: If file is missing and ignore_missing=False.
            PermissionError: If file cannot be read and ignore_missing=False.

        Example:
            >>> result = parse_file.has_keys(
            ...     "/etc/config.json",
            ...     ["database.host", "database.port"]
            ... )
            >>> assert result, f"Missing keys: {result.missing}"
        """
        parser = self._get_parser(
            path,
            ignore_missing,
            error_context=f"Cannot check if keys exist: {key_paths}.",
        )
        if parser is None:
            # File is missing and ignore_missing=True, mark all keys as missing
            return ValidationResult(missing=key_paths, wrong={}, all_match=False)
        resolved_format = self._resolve_format(path, format)
        return parser.has_keys(
            key_paths, format=resolved_format, ignore_comments=ignore_comments
        )

    def get_paths(
        self,
        path: str,
        value: Any,
        *,
        format: Optional[str] = None,
        ignore_comments: bool = True,
        ignore_missing: bool = False,
    ) -> List[str]:
        """Get all paths that contain a given value in a structured file.

        Args:
            path: File to read.
            value: The value to search for.
            format: (optional) Format identifier. If None, auto-detect from file extension.
            ignore_comments: (optional, default=True) If True, strip comments where applicable.
            ignore_missing: (optional, default=False) If False, raise exception if file is missing.
                          If True, return empty list when file is missing.

        Returns:
            List of dotted paths that have the given value. Empty list if not found.

        Raises:
            FileNotFoundError: If file is missing and ignore_missing=False.
            PermissionError: If file cannot be read and ignore_missing=False.

        Example:
            >>> parse_file.get_paths("/etc/config.json", "localhost")
        """
        parser = self._get_parser(
            path,
            ignore_missing,
            error_context=f"Cannot search for paths containing value '{value}'.",
        )
        if parser is None:
            return []
        resolved_format = self._resolve_format(path, format)
        return parser.get_paths(
            value, format=resolved_format, ignore_comments=ignore_comments
        )


@pytest.fixture
def parse_file() -> ParseFile:
    """Fixture providing the ``ParseFile`` helper for checking file contents."""
    return ParseFile()
