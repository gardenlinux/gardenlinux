import configparser
import json
import re
import tomllib
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class MappingResult:
    """Result of mapping check operation."""

    matches: Dict[str, Any]
    missing: List[str]
    wrong: Dict[str, Tuple[Any, Any]]  # key -> (expected, actual)
    all_match: bool

    def __post_init__(self):
        """Compute all_match after initialization."""
        self.all_match = len(self.missing) == 0 and len(self.wrong) == 0

    @property
    def wrong_formatted(self) -> str:
        """Format wrong values as a string for assertion messages.

        Returns:
            str: Formatted string with wrong key-value pairs.
        """
        if not self.wrong:
            return ""
        return ", ".join(f"{k}:{v[1]!r}!={v[0]!r}" for k, v in self.wrong.items())


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

    def _strip_comments(self, content: str, comment_char: str = "#") -> str:
        return "\n".join(
            line.split(comment_char, 1)[0].rstrip() if comment_char in line else line
            for line in content.splitlines()
        )

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
            content = self._strip_comments(content)
        return yaml.safe_load(content)

    def _parse_toml(self, content: str, ignore_comments: bool) -> Any:
        if ignore_comments:
            content = self._strip_comments(content, "#")
        return tomllib.loads(content)

    def _get_by_path(self, data: Any, path: str) -> Any:
        cur: Any = data
        for part in path.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return None
        return cur

    def check_line(self, line: str, *, invert: bool = False) -> bool:
        """Check if a normalized line exists (or not) in the content.

        Whitespace is normalized to single spaces before searching.

        Args:
            line: The substring to search within lines.
            invert: If True, check that it does not exist.

        Returns:
            bool: True if the condition is met (line found when invert=False,
                  or line not found when invert=True), False otherwise.
        """
        found = any(
            re.sub(r"\s+", " ", l).find(line) != -1 for l in self.content.splitlines()
        )
        if invert:
            return not found
        return found

    def check_lines(self, lines: List[str], *, invert: bool = False) -> bool:
        """Check if multiple lines appear in order (or not) in the content.

        Each expected line and the content are whitespace-normalized; the
        check looks for the ordered occurrence allowing arbitrary text
        between lines.

        Args:
            lines: Sequence of expected lines in order.
            invert: If True, check that this ordered sequence does not occur.

        Returns:
            bool: True if the condition is met (lines found in order when invert=False,
                  or lines not found in order when invert=True), False otherwise.
        """
        norm = "\n".join(re.sub(r"\s+", " ", l) for l in self.content.splitlines())
        pattern = ".*".join(re.escape(re.sub(r"\s+", " ", l)) for l in lines)
        found_in_order = bool(re.search(pattern, norm, flags=re.S))
        if invert:
            return not found_in_order
        return found_in_order

    def get_mapping(
        self,
        expected: Dict[str, Any],
        *,
        format: str,
        invert: bool = False,
        ignore_comments: bool = True,
    ) -> MappingResult:
        """Get mapping check results for structured content.

        Supports formats: ``keyval``, ``ini``, ``json``, ``yaml``, ``toml``.
        For hierarchical formats, keys may use dotted paths (e.g. ``a.b.c``).

        Args:
            expected: Mapping of expected keys to values.
            format: One of the supported format identifiers.
            invert: If True, check that none of the expected pairs match.
            ignore_comments: If True, strip comments where applicable.

        Returns:
            MappingResult: Result containing matches, missing keys, wrong values,
                          and all_match flag indicating if all expected mappings match.
        """
        fmt = format.lower()
        match fmt:
            case "keyval":
                data: Any = self._parse_keyval(self.content)
                resolver = lambda k: data.get(k)
            case "ini":
                data = self._parse_ini(self.content)
                resolver = lambda k: self._get_by_path(data, k)
            case "json":
                data = self._parse_json(self.content)
                resolver = lambda k: self._get_by_path(data, k)
            case "yaml":
                data = self._parse_yaml(self.content, ignore_comments)
                resolver = lambda k: self._get_by_path(data, k)
            case "toml":
                data = self._parse_toml(self.content, ignore_comments)
                resolver = lambda k: self._get_by_path(data, k)
            case _:
                raise ValueError(f"Unsupported format: {format}")

        matches: Dict[str, Any] = {}
        for k, v in expected.items():
            actual = resolver(k)
            if actual is None:
                continue
            matches[k] = actual

        missing = [k for k in expected.keys() if k not in matches]
        wrong = {
            k: (expected[k], matches[k])
            for k, v in expected.items()
            if k in matches and matches[k] != v
        }

        return MappingResult(
            matches=matches,
            missing=missing,
            wrong=wrong,
            all_match=False,  # Will be set in __post_init__
        )

    def check_list(
        self,
        list_path: str,
        value: Any,
        *,
        format: str,
        invert: bool = False,
        ignore_comments: bool = True,
    ) -> bool:
        """Check that a value is (or is not) present in a list within structured content.

        Supports formats: ``json``, ``yaml``, ``toml``.
        For hierarchical formats, the list path may use dotted notation (e.g. ``a.b.c``).

        Args:
            list_path: Dot-separated path to the list (e.g. ``datasource_list`` or
                ``system_info.default_user.groups``).
            value: The value to search for in the list.
            format: One of ``json``, ``yaml``, or ``toml``.
            invert: If True, check that the value is NOT in the list.
            ignore_comments: If True, strip comments where applicable.
        """
        fmt = format.lower()
        match fmt:
            case "json":
                data: Any = self._parse_json(self.content)
                target = self._get_by_path(data, list_path)
            case "yaml":
                data = self._parse_yaml(self.content, ignore_comments)
                target = self._get_by_path(data, list_path)
            case "toml":
                data = self._parse_toml(self.content, ignore_comments)
                target = self._get_by_path(data, list_path)
            case _:
                raise ValueError(
                    f"Unsupported format for list assertion: {format}. "
                    f"Supported formats: json, yaml, toml"
                )

        if target is None:
            raise ValueError(
                f"List path '{list_path}' not found or does not exist in {self.label} (format={format})"
            )

        if not isinstance(target, list):
            raise ValueError(
                f"Path '{list_path}' in {self.label} is not a list (format={format}, got {type(target).__name__})"
            )

        found = value in target
        if not invert:
            return found
        return not found
