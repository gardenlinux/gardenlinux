import configparser
import json
import re
import tomllib
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pytest

# Supported formats for auto-detection
SUPPORTED_FORMATS = ["json", "yaml", "toml", "ini", "keyval"]

# Default comment characters per format
# Always a list - empty list means the format does not support comments
FORMAT_COMMENT_CHARS = {
    "json": [],  # JSON does not support comments
    "yaml": ["#"],
    "toml": ["#"],
    "ini": [";", "#"],  # INI supports both ; and # for comments
    "keyval": ["#"],
}


@dataclass
class ValidationResult:
    """Result of validating multiple key-value pairs.

    Attributes:
        missing: List of keys that don't exist (value was None).
        wrong: Dictionary mapping keys to (expected_value, actual_value) tuples for mismatched values.
        wrong_list: List of formatted strings for each wrong value.
        all_match: True if no missing keys and no wrong values.
    """

    missing: List[str]
    wrong: Dict[str, Tuple[Any, Any]]
    all_match: bool

    @property
    def wrong_list(self) -> List[str]:
        """List of formatted strings for each wrong value.

        Returns:
            List of formatted strings like ["key: 'actual'!='expected'"].
        """
        return [
            f"{key_path}: {actual_value!r}!={expected_value!r}"
            for key_path, (expected_value, actual_value) in self.wrong.items()
        ]

    def __bool__(self) -> bool:
        return self.all_match


@dataclass
class Parse:
    """Generic parser for line-based and structured content.

    The instance holds the raw string ``content`` and a human-readable ``label``
    used in assertion messages (e.g., a filename or source description).
    """

    content: str
    label: str = "input"

    @classmethod
    def from_file(cls, path: str | Path) -> "Parse":
        """Create a parser by loading content from a file.

        Args:
            path: File system path to read.

        Returns:
            Parse: A parser with file content and label set to the path.
        """
        p = Path(path)
        text = p.read_text(encoding="utf-8", errors="ignore")
        return cls(text, str(p))

    @classmethod
    def from_str(cls, content: str, label: str = "input") -> "Parse":
        """Create a parser from an in-memory string.

        Args:
            content: Raw string to parse.
            label: Identifier for assertion messages.

        Returns:
            Parse: A parser over the provided string.
        """
        return cls(content, label)

    def _resolve_comment_chars(
        self,
        format: Optional[str],
        comment_char: Optional[Union[str, List[str], tuple]],
    ) -> List[str]:
        if comment_char is None:
            if format is not None:
                return FORMAT_COMMENT_CHARS.get(format.lower(), ["#"])
            else:
                return ["#"]
        else:
            # Normalize to list for consistent handling
            if isinstance(comment_char, (list, tuple)):
                return list(comment_char)
            else:
                return [comment_char]

    def _strip_comments_from_line(self, line: str, comment_chars: List[str]) -> str:
        """Strip comments from a single line using the first matching comment character.

        Args:
            line: Line to process.
            comment_chars: List of comment characters to check.

        Returns:
            Line with comments stripped.
        """
        if not comment_chars:
            return line
        # Find the first matching comment character
        for char in comment_chars:
            if char in line:
                return line.split(char, 1)[0]
        return line

    def _parse_keyval(self, content: str) -> Dict[str, str]:
        cfg = configparser.ConfigParser(allow_no_value=True)
        cfg.optionxform = lambda optionstr: optionstr
        wrapped = "[default]\n" + content
        cfg.read_file(StringIO(wrapped))
        return dict(cfg.items("default")) if "default" in cfg else {}

    def _parse_ini(self, content: str) -> Dict[str, Any]:
        cfg = configparser.ConfigParser()
        cfg.read_file(StringIO(content))
        return {section: dict(cfg[section]) for section in cfg.sections()}

    def _parse_json(self, content: str) -> Any:
        return json.loads(content)

    def _parse_yaml(self, content: str, ignore_comments: bool) -> Any:
        import yaml

        if ignore_comments:
            comment_chars = FORMAT_COMMENT_CHARS.get("yaml", ["#"])
            content = "\n".join(
                self._strip_comments_from_line(line, comment_chars)
                for line in content.splitlines()
            )
        return yaml.safe_load(content)

    def _parse_toml(self, content: str, ignore_comments: bool) -> Any:
        if ignore_comments:
            comment_chars = FORMAT_COMMENT_CHARS.get("toml", ["#"])
            content = "\n".join(
                self._strip_comments_from_line(line, comment_chars)
                for line in content.splitlines()
            )
        return tomllib.loads(content)

    def _get_by_path(self, data: Any, path: str) -> Any:
        cur: Any = data
        for part in path.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return None
        return cur

    def _parse_content(self, format: str, ignore_comments: bool = True) -> Any:
        fmt = format.lower()
        match fmt:
            case "keyval":
                return self._parse_keyval(self.content)
            case "ini":
                return self._parse_ini(self.content)
            case "json":
                return self._parse_json(self.content)
            case "yaml":
                return self._parse_yaml(self.content, ignore_comments)
            case "toml":
                return self._parse_toml(self.content, ignore_comments)
            case _:
                raise ValueError(
                    f"Unsupported format '{format}' in {self.label}. "
                    f"Supported formats: {', '.join(SUPPORTED_FORMATS)}."
                )

    def has_line(
        self,
        pattern: str,
        *,
        format: Optional[str] = None,
        comment_char: Optional[Union[str, List[str], tuple]] = None,
    ) -> bool:
        """Check if a line exists, automatically filtering comments.

        Filters out commented lines (lines starting with comment_char or containing
        comment_char after whitespace) and matches pattern at line boundaries.
        Whitespace is normalized to single spaces before searching.

        Args:
            pattern: The substring to search within lines.
            format: (optional) Format identifier. If provided, uses format-specific comment character(s).
            comment_char: (optional) Character(s) used for comments. Can be a string, list of strings,
                         or None. If None and format is provided, uses format-specific default
                         (always a list - empty list means no comments, e.g., JSON).
                         If None and format is not provided, defaults to ["#"].
                         For INI format, defaults to [";", "#"].

        Returns:
            bool: True if any non-comment line matches the pattern, False otherwise.

        Example:
            >>> parser = Parse.from_str("# PermitRootLogin no\\nPermitRootLogin yes")
            >>> parser.has_line("PermitRootLogin yes")  # True
            >>> parser.has_line("PermitRootLogin no")   # False (commented out)
        """
        comment_chars = self._resolve_comment_chars(format, comment_char)

        for line in self.content.splitlines():
            line = self._strip_comments_from_line(line, comment_chars)
            line = line.rstrip()
            normalized = re.sub(r"\s+", " ", line)
            if normalized.find(pattern) != -1:
                return True
        return False

    def has_lines(
        self,
        patterns: List[str],
        *,
        order: bool = True,
        format: Optional[str] = None,
        comment_char: Optional[Union[str, List[str], tuple]] = None,
    ) -> bool:
        """Check if multiple lines exist, with comment filtering and optional ordering.

        Filters comments like `has_line()` method. If order=True, checks if patterns
        appear in order (allowing text between). If order=False, checks if all
        patterns exist in any order.

        Args:
            patterns: List of patterns to search for.
            order: (optional, default=True) If True, check patterns appear in order. If False, check all exist.
            format: (optional) Format identifier. If provided, uses format-specific comment character(s).
            comment_char: (optional) Character(s) used for comments. Can be a string, list of strings,
                         or None. If None and format is provided, uses format-specific default
                         (always a list - empty list means no comments, e.g., JSON).
                         If None and format is not provided, defaults to ["#"].
                         For INI format, defaults to [";", "#"].

        Returns:
            bool: True if condition is met, False otherwise.

        Example:
            >>> parser = Parse.from_str("#line0 \\n# line1\\nline1\\nline2\\nline3")
            >>> parser.has_lines(["line0", "line1"], order=True)   # False (line0 is commented out)
            >>> parser.has_lines(["line1", "line2"], order=True)   # True
            >>> parser.has_lines(["line2", "line1"], order=False)  # True
            >>> parser.has_lines(["line2", "line1"], order=True)   # False
        """
        if not order:
            # When order=False, we can simply check each pattern using has_line
            return all(
                self.has_line(pattern, format=format, comment_char=comment_char)
                for pattern in patterns
            )

        # When order=True, we need to check patterns appear in sequence
        comment_chars = self._resolve_comment_chars(format, comment_char)

        filtered_lines = []
        for line in self.content.splitlines():
            line = self._strip_comments_from_line(line, comment_chars)
            line = line.rstrip()
            if line:  # Skip empty lines
                normalized = re.sub(r"\s+", " ", line)
                filtered_lines.append(normalized)

        norm_patterns = [re.sub(r"\s+", " ", p) for p in patterns]
        pattern = ".*".join(re.escape(p) for p in norm_patterns)
        content = "\n".join(filtered_lines)
        return bool(re.search(pattern, content, flags=re.S))

    def regex(self, pattern: str, *, flags: int = 0) -> Optional[re.Match[str]]:
        """Apply regex pattern to content and return match object.

        Provides full regex power for file parsing. Only available for
        unstructured content (no format specified).

        Args:
            pattern: Regular expression pattern to search for.
            flags: (optional, default=0) Regex flags (e.g., re.IGNORECASE, re.MULTILINE).

        Returns:
            Match object if found, None otherwise.

        Example:
            >>> parser = Parse.from_str("Boot completed in 2.345s")
            >>> match = parser.regex(r"Boot completed in ([\\d.]+)s")
            >>> if match:
            ...     boot_time = float(match.group(1))  # 2.345
        """
        return re.search(pattern, self.content, flags=flags)

    def include(
        self,
        list_path: str,
        value: Any,
        *,
        format: str,
        ignore_comments: bool = True,
    ) -> bool:
        """Check that a value is present in a list within structured content.

        Only works with structured formats (json, yaml, toml).

        Args:
            list_path: Dot-separated path to the list (e.g. ``datasource_list`` or
                ``system_info.default_user.groups``).
            value: The value to search for in the list.
            format: One of ``json``, ``yaml``, or ``toml``.
            ignore_comments: (optional, default=True) If True, strip comments where applicable.

        Returns:
            bool: True if value is in the list, False otherwise.

        Example:
            >>> parser = Parse.from_str('{"application": {"groups": ["admin", "users"]}}', label="test")
            >>> parser.include("application.groups", "admin", format="json")  # True
            >>> parser.include("application.groups", "root", format="json")   # False
        """
        fmt = format.lower()
        if fmt not in ["json", "yaml", "toml"]:
            raise ValueError(
                f"Unsupported format '{format}' for list assertion in {self.label}. "
                f"Supported formats: json, yaml, toml"
            )

        data: Any = self._parse_content(fmt, ignore_comments)
        target = self._get_by_path(data, list_path)

        if target is None:
            raise ValueError(
                f"List path '{list_path}' not found or does not exist in {self.label} (format={format}). "
                f"Check the path and file structure."
            )

        if not isinstance(target, list):
            raise ValueError(
                f"Path '{list_path}' in {self.label} is not a list (format={format}, got {type(target).__name__}). "
                f"Expected a list but found {type(target).__name__}."
            )

        return value in target

    def get_value(
        self,
        key_path: str,
        *,
        format: str,
        ignore_comments: bool = True,
    ) -> Optional[Any]:
        """Get value at a path in structured formats.

        Uses dotted path notation to access nested values in structured formats.
        Works with all structured formats: json, yaml, toml, ini, keyval.

        Args:
            key_path: Dot-separated path to the key (e.g. ``database.host``).
            format: One of the supported format identifiers.
            ignore_comments: (optional, default=True) If True, strip comments where applicable.

        Returns:
            Value at the path if found, None otherwise.

        Example:
            >>> parser = Parse.from_str('{"database": {"host": "localhost"}}', label="test")
            >>> parser.get_value("database.host", format="json")  # "localhost"
            >>> parser.get_value("database.port", format="json")  # None
        """
        fmt = format.lower()
        data: Any = self._parse_content(fmt, ignore_comments)

        # Special handling for keyval format (flat dict)
        if fmt == "keyval":
            return data.get(key_path)

        return self._get_by_path(data, key_path)

    def get_values(
        self,
        expected: Dict[str, Any],
        *,
        format: str,
        ignore_comments: bool = True,
    ) -> ValidationResult:
        """Verify that multiple key-value pairs match expected values.

        Uses dotted path notation to access nested values in structured formats.
        Works with all structured formats: json, yaml, toml, ini, keyval.

        Args:
            expected: Dictionary mapping key_path to expected_value (e.g. ``{"database.host": "localhost"}``).
            format: One of the supported format identifiers.
            ignore_comments: (optional, default=True) If True, strip comments where applicable.

        Returns:
            ValidationResult with missing and wrong values.

        Example:
            >>> parser = Parse.from_str(
            ...     '{"database": {"host": "localhost", "port": 5432}}',
            ...     label="test"
            ... )
            >>> result = parser.get_values(
            ...     {"database.host": "localhost", "database.port": 5432, "database.missing": "value"},
            ...     format="json"
            ... )
            >>> result.missing
            ['database.missing']
            >>> result.wrong
            {}
            >>> result.all_match
            False
        """
        missing: List[str] = []
        wrong: Dict[str, Tuple[Any, Any]] = {}

        for key_path, expected_value in expected.items():
            actual_value = self.get_value(
                key_path, format=format, ignore_comments=ignore_comments
            )
            if actual_value is None:
                missing.append(key_path)
            elif actual_value != expected_value:
                wrong[key_path] = (expected_value, actual_value)

        return ValidationResult(
            missing=missing,
            wrong=wrong,
            all_match=len(missing) == 0 and len(wrong) == 0,
        )

    def has_key(
        self,
        key_path: str,
        *,
        format: str,
        ignore_comments: bool = True,
    ) -> bool:
        """Check if a key/path exists in structured format.

        Uses dotted path notation to check for key existence in structured formats.

        Args:
            key_path: Dot-separated path to the key (e.g. ``database.host``).
            format: One of the supported format identifiers.
            ignore_comments: (optional, default=True) If True, strip comments where applicable.

        Returns:
            bool: True if key exists, False otherwise.

        Example:
            >>> parser = Parse.from_str('{"database": {"host": "localhost"}}', label="test")
            >>> parser.has_key("database.host", format="json")  # True
            >>> parser.has_key("database.port", format="json")  # False
        """
        return (
            self.get_value(key_path, format=format, ignore_comments=ignore_comments)
            is not None
        )

    def has_keys(
        self,
        key_paths: List[str],
        *,
        format: str,
        ignore_comments: bool = True,
    ) -> ValidationResult:
        """Check if multiple keys/paths exist in structured format.

        Uses dotted path notation to check for key existence in structured formats.

        Args:
            key_paths: List of dot-separated paths to keys (e.g. ``["database.host", "database.port"]``).
            format: One of the supported format identifiers.
            ignore_comments: (optional, default=True) If True, strip comments where applicable.

        Returns:
            ValidationResult with missing keys (keys that don't exist). The wrong dictionary will be empty
            since this method only checks existence, not values.

        Example:
            >>> parser = Parse.from_str(
            ...     '{"database": {"host": "localhost", "port": 5432}}',
            ...     label="test"
            ... )
            >>> result = parser.has_keys(["database.host", "database.port", "database.missing"], format="json")
            >>> result.missing
            ['database.missing']
            >>> result.wrong
            {}
            >>> result.all_match
            False
        """
        missing: List[str] = []
        wrong: Dict[str, Tuple[Any, Any]] = {}

        for key_path in key_paths:
            if not self.has_key(
                key_path, format=format, ignore_comments=ignore_comments
            ):
                missing.append(key_path)

        return ValidationResult(
            missing=missing, wrong=wrong, all_match=len(missing) == 0
        )

    def get_paths(
        self,
        value: Any,
        *,
        format: str,
        ignore_comments: bool = True,
    ) -> List[str]:
        """Get all paths that contain a given value in structured formats.

        Searches recursively through nested structures to find all keys/paths
        that have the given value.

        Args:
            value: The value to search for.
            format: One of the supported format identifiers.
            ignore_comments: (optional, default=True) If True, strip comments where applicable.

        Returns:
            List of dotted paths that have the given value. Empty list if not found.

        Example:
            >>> content = '{"host": "localhost", "database": {"host": "localhost"}}'
            >>> parser = Parse.from_str(content, label="test")
            >>> parser.get_paths("localhost", format="json")
            # Returns: ["host", "database.host"]
        """
        data: Any = self._parse_content(format, ignore_comments)

        paths: List[str] = []

        def _find_paths(obj: Any, current_path: str = "") -> None:
            """Recursively find paths with the given value."""
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_path = f"{current_path}.{k}" if current_path else k
                    if v == value:
                        paths.append(new_path)
                    _find_paths(v, new_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    new_path = f"{current_path}[{i}]" if current_path else f"[{i}]"
                    if item == value:
                        paths.append(new_path)
                    _find_paths(item, new_path)

        _find_paths(data)
        return paths


@pytest.fixture
def parse() -> type[Parse]:
    """Fixture providing the ``Parse`` class for parsing string content."""
    return Parse
