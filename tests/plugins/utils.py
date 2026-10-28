import logging
import os
from typing import List, Optional, TypeVar

# Various utility functions to make tests more readable
# This should not contain test-assertions, but only abstract details that make tests harder to read

logger = logging.getLogger(__name__)


def equals_ignore_case(a: str, b: str) -> bool:
    return a.casefold() == b.casefold()


def get_normalized_sets(*sets: set) -> tuple[set, ...]:
    normalized_sets = tuple({str(v).casefold() for v in s} for s in sets)
    return normalized_sets


def is_set(obj) -> bool:
    return isinstance(obj, set)


def tree(path: str) -> set[str]:
    """Returns all subpaths of `path`, like the find command"""
    tree = {path}
    for root, dirs, files in os.walk(path):
        for file in files:
            tree.add(f"{root}/{file}")
        for dir in dirs:
            tree.add(f"{root}/{dir}")

    return tree


T = TypeVar("T")


def check_for_duplicates(entries: List[T]) -> List[T]:
    """
    checks for duplicates, to change equality comparison, add a compare field to the dataclass.
    """
    duplicates = list[T]()
    visited_entries = list[T]()
    for entry in entries:
        if entry in visited_entries:
            duplicates.append(entry)
        else:
            visited_entries.append(entry)

    return duplicates


def get_os_release_value(key: str) -> Optional[str]:
    """Get the value of a key from /etc/os-release.

    Returns:
        The unquoted value if the key is found, None otherwise.
    """
    try:
        logger.debug(f"Reading /etc/os-release to find {key}")
        with open("/etc/os-release", "r") as f:
            for line in f:
                if line.startswith(f"{key}="):
                    value = line.split("=", 1)[1].strip().strip('"')
                    logger.debug(f"Found {key}={value} in /etc/os-release")
                    return value
        logger.debug(f"{key} not found in /etc/os-release")
    except FileNotFoundError:
        logger.warning("/etc/os-release file not found")
    except PermissionError:
        logger.warning("Permission denied reading /etc/os-release")
    return None


def get_versioned_flavor_from_os_release() -> Optional[str]:
    """Assemble the versioned flavor from /etc/os-release.

    The versioned flavor (ADR 0035) is:

        {cname}-{arch}-{version}

    It is reconstructed from the os-release records written by the builder:
    VARIANT_ID holds the flavor ({cname}-{arch}) and GARDENLINUX_VERSION the
    version.

    Returns:
        The versioned flavor if all components are found, None otherwise.
    """
    flavor = get_os_release_value("VARIANT_ID")
    version = get_os_release_value("GARDENLINUX_VERSION")
    if not flavor or not version:
        logger.debug(
            "Cannot assemble versioned flavor: missing VARIANT_ID or "
            "GARDENLINUX_VERSION in /etc/os-release"
        )
        return None
    return f"{flavor}-{version}"
