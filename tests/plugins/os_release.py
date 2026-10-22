"""
os_release.py – shared parser for /etc/os-release.

Provides an immutable :class:`OsRelease` dataclass and a cached accessor
:func:`get_os_release` that returns the parsed values for the real system
file.  The :func:`parse_os_release` function accepts an explicit path so
the parser is unit-testable without touching the real file system.
"""

import logging
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

_OS_RELEASE_PATH = "/etc/os-release"


@dataclass(frozen=True)
class OsRelease:
    """Typed representation of /etc/os-release fields.

    All fields are optional; fields not present in the file remain ``None``
    (or their appropriate empty default).  The :attr:`raw` mapping contains
    every key that was parsed, without quote-stripping applied by the typed
    fields above.
    """

    # Generic os-release keys
    id: Optional[str] = None  # ID=
    name: Optional[str] = None  # NAME=
    pretty_name: Optional[str] = None  # PRETTY_NAME=
    variant_id: Optional[str] = None  # VARIANT_ID=
    image_version: Optional[str] = None  # IMAGE_VERSION=

    # Garden Linux-specific keys
    gardenlinux_version: Optional[str] = None  # GARDENLINUX_VERSION=
    cname: Optional[str] = None  # GARDENLINUX_CNAME=
    features: frozenset = field(default_factory=frozenset)  # GARDENLINUX_FEATURES=
    commit_id: Optional[str] = None  # GARDENLINUX_COMMIT_ID=
    commit_id_long: Optional[str] = None  # GARDENLINUX_COMMIT_ID_LONG=

    # All parsed raw key/value pairs (values already quote-stripped)
    raw: dict = field(default_factory=dict)

    def semver_tuple(self) -> Optional[tuple]:
        """Return ``(major, minor, patch)`` parsed from :attr:`gardenlinux_version`.

        Returns ``None`` when the version string is absent or cannot be parsed
        as a numeric version (e.g. nightly/dev builds whose version is
        ``today`` or another non-numeric token).

        Legacy 2-segment versions (e.g. ``1443.2``) are accepted and the
        missing patch component is treated as ``0``.
        """
        if not self.gardenlinux_version:
            return None
        parts = self.gardenlinux_version.split(".")
        try:
            if len(parts) == 2:
                return (int(parts[0]), int(parts[1]), 0)
            if len(parts) == 3:
                return (int(parts[0]), int(parts[1]), int(parts[2]))
        except ValueError:
            pass
        return None


def _strip_value(raw_value: str) -> str:
    """Strip surrounding whitespace and optional double-quotes from a value."""
    return raw_value.strip().strip('"')


def parse_os_release(path: str = _OS_RELEASE_PATH) -> OsRelease:
    """Parse an os-release file and return an :class:`OsRelease` instance.

    :param path: Path to the os-release file; defaults to
        ``/etc/os-release``.
    :returns: Populated :class:`OsRelease` dataclass.  On I/O errors an
        empty/default instance is returned and a warning is logged.
    """
    raw: dict[str, str] = {}

    try:
        with open(path, "r") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                raw[key.strip()] = _strip_value(value)
    except FileNotFoundError:
        logger.warning("os-release file not found: %s", path)
        return OsRelease()
    except PermissionError:
        logger.warning("Permission denied reading os-release file: %s", path)
        return OsRelease()

    features_raw = raw.get("GARDENLINUX_FEATURES", "")
    features: frozenset[str] = frozenset(
        f.strip() for f in features_raw.split(",") if f.strip()
    )

    return OsRelease(
        id=raw.get("ID"),
        name=raw.get("NAME"),
        pretty_name=raw.get("PRETTY_NAME"),
        variant_id=raw.get("VARIANT_ID"),
        image_version=raw.get("IMAGE_VERSION"),
        gardenlinux_version=raw.get("GARDENLINUX_VERSION"),
        cname=raw.get("GARDENLINUX_CNAME"),
        features=features,
        commit_id=raw.get("GARDENLINUX_COMMIT_ID"),
        commit_id_long=raw.get("GARDENLINUX_COMMIT_ID_LONG"),
        raw=raw,
    )


@lru_cache(maxsize=1)
def get_os_release() -> OsRelease:
    """Return the cached :class:`OsRelease` for the real system file.

    The result is cached after the first call so that all plugins share a
    single parsed instance.  Use :func:`parse_os_release` directly when you
    need to supply a custom path (e.g. in unit tests).
    """
    return parse_os_release(_OS_RELEASE_PATH)
