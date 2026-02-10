import configparser
import json
import re
import tomllib
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pytest

# Supported formats for auto-detection
SUPPORTED_FORMATS = ["json", "yaml", "toml", "ini", "keyval", "spacedelim"]

# Default comment characters per format
# Always a list - empty list means the format does not support comments
FORMAT_COMMENT_CHARS = {
    "json": [],  # JSON does not support comments
    "yaml": ["#"],
    "toml": ["#"],
    "ini": [";", "#"],  # INI supports both ; and # for comments
    "keyval": ["#"],
    "spacedelim": ["#"],
}


def _resolve_comment_chars(
    format: Optional[str],
    comment_char: Optional[Union[str, List[str]]],
) -> List[str]:
    """Resolve comment characters from format or explicit parameter.

    Args:
        format: Optional format identifier.
        comment_char: Optional comment character(s).

    Returns:
        List of comment characters to use.
    """
    if comment_char is None:
        if format is not None:
            return FORMAT_COMMENT_CHARS.get(format.lower(), ["#"])
        else:
            return ["#"]
    else:
        if isinstance(comment_char, list):
            return comment_char
        else:
            return [comment_char]


def _strip_comments_from_line(line: str, comment_chars: List[str]) -> str:
    """Strip comments from a single line using the first matching comment character.

    Args:
        line: Line to process.
        comment_chars: List of comment characters to check.

    Returns:
        Line with comments stripped.
    """
    if not comment_chars:
        return line
    for char in comment_chars:
        if char in line:
            return line.split(char, 1)[0]
    return line


class Lines:
    """Supports checking for string literals, regex patterns, and lists of patterns
    using the `in` operator. Automatically handles comment filtering for string literals.
    """

    def __init__(
        self,
        content: str,
        label: str = "input",
        format: Optional[str] = None,
        comment_char: Optional[Union[str, List[str]]] = None,
        ordered: bool = False,
    ):
        """Initialize Lines container.

        Args:
            content: Raw content string to search.
            label: Human-readable label for error messages.
            format: Optional format identifier for comment filtering.
            comment_char: Optional comment character(s).
            ordered: If True, list patterns must appear in order.
        """
        self.content = content
        self.label = label
        self.format = format
        self.comment_char = comment_char
        self.ordered = ordered

    def _check_string_literal(self, pattern: str) -> bool:
        """Check if a string literal exists in lines (with comment filtering)."""
        comment_chars = _resolve_comment_chars(self.format, self.comment_char)
        # Normalize the pattern as well to match normalized lines
        normalized_pattern = re.sub(r"\s+", " ", pattern)

        # Check if pattern starts with a comment character - if so, don't strip comments
        pattern_is_comment = any(
            pattern.lstrip().startswith(char) for char in comment_chars
        )

        for line in self.content.splitlines():
            # Only strip comments if the pattern itself is not a comment
            if not pattern_is_comment:
                line = _strip_comments_from_line(line, comment_chars)
            line = line.rstrip()
            normalized_line = re.sub(r"\s+", " ", line)
            if normalized_line.find(normalized_pattern) != -1:
                return True
        return False

    def _check_regex_pattern(self, pattern: re.Pattern[str]) -> bool:
        """Check if a regex pattern matches the content."""
        return bool(pattern.search(self.content))

    def _check_pattern_list(self, patterns: List[str]) -> bool:
        """Check if multiple patterns exist (with optional ordering)."""
        if not self.ordered:
            # Unordered: check each pattern individually
            return all(self._check_string_literal(pattern) for pattern in patterns)

        # Ordered: check patterns appear in sequence
        comment_chars = _resolve_comment_chars(self.format, self.comment_char)

        filtered_lines = []
        for line in self.content.splitlines():
            line = _strip_comments_from_line(line, comment_chars)
            line = line.rstrip()
            if line:  # Skip empty lines
                normalized = re.sub(r"\s+", " ", line)
                filtered_lines.append(normalized)

        norm_patterns = [re.sub(r"\s+", " ", p) for p in patterns]
        pattern = ".*".join(re.escape(p) for p in norm_patterns)
        content = "\n".join(filtered_lines)
        return bool(re.search(pattern, content, flags=re.S))

    def __contains__(self, pattern: Union[str, re.Pattern[str], List[str]]) -> bool:
        """Check if pattern exists in lines.

        Supports three pattern types:
        - str: String literal search (with comment filtering)
        - re.Pattern: Regex pattern matching (full content, multiline)
        - list: Multiple patterns (ordered or unordered based on container config)

        Args:
            pattern: Pattern to search for (str, re.Pattern, or list of str).

        Returns:
            bool: True if pattern is found, False otherwise.

        Example:
            >>> lines = Lines("line1\\nline2\\nline3")
            >>> "line2" in lines  # True
            >>> re.compile(r"line\\d+") in lines  # True
            >>> ["line1", "line2"] in lines  # True
        """
        if isinstance(pattern, str):
            return self._check_string_literal(pattern)
        elif isinstance(pattern, re.Pattern):
            return self._check_regex_pattern(pattern)
        elif isinstance(pattern, list):
            return self._check_pattern_list(pattern)
        else:
            raise TypeError(
                f"Unsupported pattern type {type(pattern).__name__} in {self.label}. "
                f"Expected str, re.Pattern, or list of str."
            )

    def __eq__(self, other: object) -> bool:
        """Check if Lines content matches a list of expected lines exactly.

        Args:
            other: List of expected lines to compare against.

        Returns:
            bool: True if all lines match in order, False otherwise.
        """
        if not isinstance(other, list):
            return NotImplemented

        comment_chars = _resolve_comment_chars(self.format, self.comment_char)

        # Get actual lines from content, stripping full-line comments but keeping inline comments
        actual_lines = []
        for line in self.content.splitlines():
            line = line.rstrip()
            if not line:  # Skip empty lines
                continue
            # Skip lines that are purely comments (start with comment char after whitespace)
            stripped = line.lstrip()
            if comment_chars and any(
                stripped.startswith(char) for char in comment_chars
            ):
                continue
            actual_lines.append(line)

        return actual_lines == other

    def __repr__(self) -> str:
        """Return representation of Lines for debugging."""
        comment_chars = _resolve_comment_chars(self.format, self.comment_char)

        actual_lines = []
        for line in self.content.splitlines():
            line = line.rstrip()
            if not line:  # Skip empty lines
                continue
            # Skip lines that are purely comments
            stripped = line.lstrip()
            if comment_chars and any(
                stripped.startswith(char) for char in comment_chars
            ):
                continue
            actual_lines.append(line)
        return repr(actual_lines)


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

        Raises:
            FileNotFoundError: If the file does not exist.
            PermissionError: If the file cannot be read due to insufficient permissions.
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

    def _parse_keyval(self, content: str) -> Dict[str, str]:
        cfg = configparser.ConfigParser(allow_no_value=True)
        cfg.optionxform = lambda optionstr: optionstr  # type: ignore[assignment]
        wrapped = "[default]\n" + content
        cfg.read_file(StringIO(wrapped))
        result = dict(cfg.items("default")) if "default" in cfg else {}
        # Strip quotes from values (both single and double quotes)
        return {k: v.strip('"').strip("'") if v else v for k, v in result.items()}

    def _parse_spacedelim(self, content: str) -> Dict[str, str]:
        result = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) == 2:
                key, value = parts
                result[key] = value
        return result

    def _parse_ini(self, content: str) -> Dict[str, Any]:
        cfg = configparser.ConfigParser()
        cfg.optionxform = str  # type: ignore[method-assign] # Preserve case of option names
        cfg.read_file(StringIO(content))
        return {section: dict(cfg[section]) for section in cfg.sections()}

    def _parse_json(self, content: str) -> Any:
        return json.loads(content)

    def _parse_yaml(self, content: str, ignore_comments: bool) -> Any:
        import yaml

        if ignore_comments:
            comment_chars = FORMAT_COMMENT_CHARS.get("yaml", ["#"])
            content = "\n".join(
                _strip_comments_from_line(line, comment_chars)
                for line in content.splitlines()
            )
        return yaml.safe_load(content)

    def _parse_toml(self, content: str, ignore_comments: bool) -> Any:
        if ignore_comments:
            comment_chars = FORMAT_COMMENT_CHARS.get("toml", ["#"])
            content = "\n".join(
                _strip_comments_from_line(line, comment_chars)
                for line in content.splitlines()
            )
        return tomllib.loads(content)

    def _parse_content(self, format: str, ignore_comments: bool = True) -> Any:
        fmt = format.lower()
        match fmt:
            case "keyval":
                return self._parse_keyval(self.content)
            case "spacedelim":
                return self._parse_spacedelim(self.content)
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

    def parse(self, format: str, ignore_comments: bool = True) -> Any:
        """Parse content and return data structure based on format.


        Args:
            format: One of the supported format identifiers (json, yaml, toml, ini, keyval).
            ignore_comments: (optional, default=True) If True, strip comments where applicable.

        Returns:
            Parsed data structure (dict, list, etc.) based on format.

        Example:
            >>> parser = Parse.from_str('{"database": {"host": "localhost", "port": 5432}}')
            >>> config = parser.parse(format="json")
            >>> assert config["database"]["host"] == "localhost"
            >>> assert config["database"]["port"] == 5432
            >>> assert "missing" not in config["database"]
        """
        return self._parse_content(format, ignore_comments)

    def lines(
        self,
        *,
        format: Optional[str] = None,
        comment_char: Optional[Union[str, List[str]]] = None,
        ordered: bool = False,
    ) -> Lines:
        """Get Lines container for line-based operations.

        Supports checking patterns using the `in` operator:
        - String literals: `assert "line" in parser.lines()`
        - Regex patterns: `assert re.compile(r"\\d+") in parser.lines()`
        - Lists (unordered): `assert ["lineA", "lineB"] in parser.lines()`
        - Lists (ordered): `assert ["lineA", "lineB"] in parser.lines(ordered=True)`

        Args:
            format: (optional) Format identifier for comment filtering.
            comment_char: (optional) Character(s) used for comments.
            ordered: (optional, default=False) If True, list patterns must appear in order.

        Returns:
            Lines container instance.

        Example:
            >>> parser = Parse.from_str("line1\\nline2\\nline3")
            >>> assert "line2" in parser.lines()
            >>> assert ["line1", "line3"] in parser.lines()  # Unordered
            >>> assert ["line1", "line2"] in parser.lines(ordered=True)  # Ordered
        """
        return Lines(
            content=self.content,
            label=self.label,
            format=format,
            comment_char=comment_char,
            ordered=ordered,
        )


@pytest.fixture
def parse() -> type[Parse]:
    """Fixture providing the ``Parse`` class for parsing string content."""
    return Parse
