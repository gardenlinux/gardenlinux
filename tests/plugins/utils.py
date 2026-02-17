import logging
from typing import Dict, List, Optional, TypeVar

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


T = TypeVar("T")


def check_for_duplicates(entries: List[T]) -> List[T]:
    """
    checks for duplicates, to change equality comparision, add a compare field to the dataclass.
    """
    duplicates = list[T]()
    visited_entries = list[T]()
    for entry in entries:
        if entry in visited_entries:
            duplicates.append(entry)
        else:
            visited_entries.append(entry)

    return duplicates


def get_cname_from_os_release() -> Optional[str]:
    """Get GARDENLINUX_CNAME from /etc/os-release.

    Returns:
        CNAME string if found, None otherwise.
    """
    try:
        logger.debug("Reading /etc/os-release to find GARDENLINUX_CNAME")
        with open("/etc/os-release", "r") as f:
            for line in f:
                if line.startswith("GARDENLINUX_CNAME="):
                    cname = line.split("=", 1)[1].strip().strip('"')
                    logger.debug(f"Found GARDENLINUX_CNAME={cname} in /etc/os-release")
                    return cname
        logger.debug("GARDENLINUX_CNAME not found in /etc/os-release")
    except FileNotFoundError:
        logger.warning("/etc/os-release file not found")
    except PermissionError:
        logger.warning("Permission denied reading /etc/os-release")
    return None
