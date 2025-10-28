import configparser
import json
import re
import tomllib
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List


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

    def assert_line(self, line: str, *, invert: bool = False) -> None:
        """Assert that a normalized line exists (or not) in the content.

        Whitespace is normalized to single spaces before searching.

        Args:
            line: The substring to search within lines.
            invert: If True, assert that it does not exist.
        """
        found = any(
            re.sub(r"\s+", " ", l).find(line) != -1 for l in self.content.splitlines()
        )
        if not invert:
            assert found, f"Could not find line {line!r} in {self.label}."
        else:
            assert (
                not found
            ), f"Found line {line!r} in {self.label}, but should not be present."

    def assert_lines(self, lines: List[str], *, invert: bool = False) -> None:
        """Assert multiple lines appear in order (or not) in the content.

        Each expected line and the content are whitespace-normalized; the
        assertion checks for the ordered occurrence allowing arbitrary text
        between lines.

        Args:
            lines: Sequence of expected lines in order.
            invert: If True, assert that this ordered sequence does not occur.
        """
        norm = "\n".join(re.sub(r"\s+", " ", l) for l in self.content.splitlines())
        pattern = ".*".join(re.escape(re.sub(r"\s+", " ", l)) for l in lines)
        found_in_order = bool(re.search(pattern, norm, flags=re.S))
        if not invert:
            assert (
                found_in_order
            ), f"Could not find expected lines in order in {self.label}: {lines}"
        else:
            assert (
                not found_in_order
            ), f"Found unexpected lines in order in {self.label}, but should not: {lines}"

    def assert_mapping(
        self,
        expected: Dict[str, Any],
        *,
        format: str,
        invert: bool = False,
        ignore_comments: bool = True,
    ) -> None:
        """Assert key/value mappings in structured content.

        Supports formats: ``keyval``, ``ini``, ``json``, ``yaml``, ``toml``.
        For hierarchical formats, keys may use dotted paths (e.g. ``a.b.c``).

        Args:
            expected: Mapping of expected keys to values.
            format: One of the supported format identifiers.
            invert: If True, assert none of the expected pairs match.
            ignore_comments: If True, strip comments where applicable.
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
                raise AssertionError(f"Unsupported format: {format}")

        matches: Dict[str, Any] = {}
        for k, v in expected.items():
            actual = resolver(k)
            if actual is None:
                continue
            matches[k] = actual

        if not invert:
            missing = [k for k in expected.keys() if k not in matches]
            wrong = [k for k, v in expected.items() if k in matches and matches[k] != v]
            assert not missing and not wrong, (
                f"Could not find expected mapping in {self.label} (format={format}). "
                f"missing={missing}, wrong={{{', '.join(f'{k}:{matches.get(k)!r}!={v!r}' for k, v in expected.items() if k in matches and matches[k] != v)}}}"
            )
        else:
            found = {
                k: matches[k]
                for k, v in expected.items()
                if k in matches and matches[k] == v
            }
            assert (
                not found
            ), f"Found unexpected mapping in {self.label} (format={format}): {found}"
