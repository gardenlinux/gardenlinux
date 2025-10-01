import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pytest

SUPPORTED_HASH_ALGORITHMS = ["yescrypt", "sha512"]


@dataclass
class PamEntry:
    """
    Representation of one non-comment PAM configuration line.

    Example:
    password [success=1 default=ignore] pam_unix.so obscure sha512
    ^type^   ^control^^^^^^^^^^^^^^^^^^ ^module^^^^ ^options^^^^^^

    @include    common-password
    ^directive^ ^include_target^^^

    :param type_: PAM type (auth/account/password/session)
    :type type_: str
    :param control: raw control token (either a single token like 'required'
                    or bracketed expression like '[success=1 default=ignore]')
    :type control: Optional[str]
    :param module: module name, e.g. 'pam_unix.so'
    :type module: str
    :param options: list of module arguments (tokens after the module name)
    :type options: List[str]
    :param include_target: target of an @include directive, e.g 'common-password'
                           None if this is a regular entry.
    :type include_target: Optional[str]
    """

    type_: str
    control: str
    module: str
    options: List[str]
    include_target: Optional[str] = None

    @property
    def control_dict(self) -> Dict[str, str]:
        """
        Parse bracketed control expressions into a dict.
        Example:
            '[success=1 default=ignore]' -> {'success': '1', 'default': 'ignore'}

        Multiple bracketed expressions are folded into the same dict.
        Example:
            '[success=1 default=ignore] [user_unknown=ignore]' -> {'success': '1', 'default': 'ignore', 'user_unknown': 'ignore'}

        Handles escaped brackets (\]) as literals.
        If control is a simple token (e.g. 'required'), return {}
        """
        result: Dict[str, str] = {}

        if not self.control:
            return result

        control_line = self.control.strip()

        # Find all bracketed control expressions like [success=1 default=ignore]
        # PAM allows multiple such expressions, and `]` can be escaped as `\]`.
        # Example: "[success=1 default=ignore] [some\]thing=ok]"
        #
        # Regex structure:
        #   \[           -> match literal '['
        #   (.*?)        -> capture everything inside until...
        #   (?<!\\)\]    -> a ']' that is NOT preceded by a backslash
        for match in re.finditer(r"\[(.*?)(?<!\\)\]", control_line):
            # Extract content between brackets and replace any escaped brackets
            inner = match.group(1).replace(r"\]", "]").strip()
            if not inner:
                continue  # Skip empty bracketed groups like '[]'

            # Split into tokens
            for token in inner.split():
                if "=" in token:
                    key, value = token.split("=", 1)
                    result[key] = value
                else:
                    result[token] = ""  # presence-only token
        return result

    @property
    def hash_algo(self) -> Optional[str]:
        """Return the hash algorithm specified in the options, if any."""
        for opt in self.options:
            if opt in SUPPORTED_HASH_ALGORITHMS:
                return opt
        return None

    def __repr__(self) -> str:
        return f"PamEntry(type_={self.type_!r}, control={self.control!r}, module={self.module!r}, options={self.options!r})"


class PamConfig:
    """
    Represents the entire PAM config.

    Reads the file and parses all non-comment and non-empty lines into
    `PamEntry` objects and provides helper methods to filter and query
    entries.

    Example PAM line:
        password [success=1 default=ignore] pam_unix.so obscure sha512
        ^type^   ^control^^^^^^^^^^^^^^^^^^ ^module^^^^ ^options^^^^^^

    Supports regular PAM entries, bracketed control expressions,
    simple control tokens like 'required' or 'sufficient' and
    include directives via '@include <file>' lines.

    :param path: Path to the PAM configuration file
    :type path: Path
    :raises FileNotFoundError: if the provided path does not exist

    Attributes:
        path (Path): Path to the PAM config
        lines (List[str]): Raw lines read from the file
        entries (List[PamEntries]): Parsed PAM Entries

    Example usage:
        pam = PamConfig(Path("/etc/pam.d/common-password"))
        password_entries = pam.find_entries(type_="password")
        for entry in password_entries:
            print(entry.hash_algo)
    """

    def __init__(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"PAM config file at '{path}' not found!")
        self.path = path
        # Keep raw lines for debugging / future use
        self.lines = [
            line.rstrip()
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
        ]
        self.entries: List[PamEntry] = self._parse_entries()

    def _parse_entries(self) -> List[PamEntry]:
        """
        Parse non-empty, non-comment lines into PamEntry objects.

        Handles bracketed control expressions that may contain spaces,
        e.g. '[success=1 default=ignore]'.
        """
        entries: List[PamEntry] = []

        for line in self.lines:
            stripped = line.lstrip()
            if not stripped or stripped.startswith("#"):
                continue

            if stripped.startswith("@include"):
                _, target = stripped.split(maxsplit=1)
                entries.append(
                    PamEntry(
                        type_="",
                        control="",
                        module="",
                        options=[],
                        include_target=target,
                    )
                )
                continue

            # Split into tokens: type, control, module, args
            tokens = stripped.split()
            if len(tokens) < 3:
                continue  # skip malformed line

            type_ = tokens[0]

            # parse control token(s)
            # if token[1] starts with '[' we must join until matching ']'
            index = 1
            control_token = tokens[index]
            control_full = control_token  # fallback default

            if control_token.startswith("["):
                # Find the token that ends with ']'
                if control_token.endswith("]"):
                    control_full = control_token
                    index = 2
                else:
                    found = False
                    for j in range(2, len(tokens)):
                        if tokens[j].endswith("]"):
                            control_full = " ".join(tokens[1 : j + 1])
                            index = j + 1
                            found = True
                            break
                    if not found:
                        # malformed bracket expression: fall back to single token
                        index = 2
            else:
                control_full = control_token
                index = 2

            # next token is the module name
            if index >= len(tokens):
                # malformed line
                continue
            module = tokens[index]
            args = tokens[index + 1 :] if index + 1 < len(tokens) else []

            entries.append(
                PamEntry(type_=type_, control=control_full, module=module, options=args)
            )
        return entries

    def find_entries(
        self,
        type_: Optional[str] = None,
        module_contains: Optional[str] = None,
        arg_contains: Optional[List[str]] = None,
        control_contains: Optional[str | Dict[str, str] | List[str]] = None,
        match_all: Optional[bool] = False,
        include_target: Optional[str] = None,
    ) -> List[PamEntry]:
        """
            Return entries filtered by the provided criteria.

        Examples:
            - control_contains="required" → match entries whose raw control string contains 'required'
            - control_contains={"success": "1"} → match entries where control_dict['success'] == '1'
            - control_contains=["required", "sufficient"] → match entries where raw control string contains one/all of them
              (depending on match_all)

        :param type_: exact PAM type (case-insensitive)
        :type type_: Optional[str]
        :param module_contains: substring matched against module name
        :type module_contains: Optional[str]
        :param arg_contains: list of option tokens that mus all be present in entry.options
        :type arg_contains: Optional[List[str]]
        :param control_contains: expected string, list of strings or set of fields that must be present in entry.control
        :type control_contains: Optional[str | Dict[str, str] | List[str]]
        :param match_all: requires all parameters in arg_contains and control_contains must match for returned entries
        :type match_all: bool
        :param include_target: filter by exact match for the @include target.
        :type include_target: Optional[str]
        """
        results = self.entries

        if type_ is not None:
            results = [
                entry for entry in results if entry.type_.lower() == type_.lower()
            ]

        if module_contains is not None:
            results = [entry for entry in results if module_contains in entry.module]

        if arg_contains:
            if match_all:
                results = [
                    entry
                    for entry in results
                    if all(token in entry.options for token in arg_contains)
                ]
            else:
                results = [
                    entry
                    for entry in results
                    if any(token in entry.options for token in arg_contains)
                ]

        if control_contains is not None:
            if isinstance(control_contains, str):
                # simple substring matching in raw control statement
                results = [
                    entry for entry in results if control_contains in entry.control
                ]

            elif isinstance(control_contains, list):
                if match_all:
                    results = [
                        entry
                        for entry in results
                        if all(token in entry.control for token in control_contains)
                    ]
                else:
                    results = [
                        entry
                        for entry in results
                        if any(tok in entry.control for tok in control_contains)
                    ]

        if isinstance(control_contains, dict):
            if match_all:
                results = [
                    entry
                    for entry in results
                    if all(
                        value == "*" or entry.control_dict.get(key) == value
                        for key, value in control_contains.items()
                    )
                ]
            else:
                results = [
                    entry
                    for entry in results
                    if any(
                        value == "*" or entry.control_dict.get(key) == value
                        for key, value in control_contains.items()
                    )
                ]

        if include_target is not None:
            results = [
                entry for entry in results if entry.include_target == include_target
            ]

        return results


@pytest.fixture
def pam_config(request: pytest.FixtureRequest):
    """
    Return a PamConfig object for /etc/pam.d/common-password.
    """
    return PamConfig(Path(request.param))
