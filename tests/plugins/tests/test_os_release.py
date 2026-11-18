"""Unit tests for plugins.os_release."""

import textwrap
from pathlib import Path

import pytest
from plugins.os_release import OsRelease, parse_os_release

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def write_os_release(tmp_path: Path, content: str) -> str:
    """Write *content* to a temp file and return its path as a string."""
    p = tmp_path / "os-release"
    p.write_text(textwrap.dedent(content))
    return str(p)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def test_parse_basic_fields(tmp_path):
    path = write_os_release(
        tmp_path,
        """\
        ID=gardenlinux
        NAME="Garden Linux"
        PRETTY_NAME="Garden Linux 1592.0.0"
        VARIANT_ID=server
        IMAGE_VERSION=1592.0.0
        GARDENLINUX_VERSION=1592.0.0
        GARDENLINUX_CNAME=gardener
        GARDENLINUX_FEATURES=base,server,cloud
        GARDENLINUX_COMMIT_ID=abc123
        GARDENLINUX_COMMIT_ID_LONG=abc123def456
        """,
    )
    result = parse_os_release(path)

    assert result.id == "gardenlinux"
    assert result.name == "Garden Linux"
    assert result.pretty_name == "Garden Linux 1592.0.0"
    assert result.variant_id == "server"
    assert result.image_version == "1592.0.0"
    assert result.gardenlinux_version == "1592.0.0"
    assert result.cname == "gardener"
    assert result.features == frozenset({"base", "server", "cloud"})
    assert result.commit_id == "abc123"
    assert result.commit_id_long == "abc123def456"


def test_parse_strips_double_quotes(tmp_path):
    path = write_os_release(
        tmp_path,
        """\
        GARDENLINUX_CNAME="gardener"
        GARDENLINUX_VERSION="1592.0.0"
        """,
    )
    result = parse_os_release(path)
    assert result.cname == "gardener"
    assert result.gardenlinux_version == "1592.0.0"


def test_parse_features_absent_returns_empty_frozenset(tmp_path):
    path = write_os_release(tmp_path, "ID=gardenlinux\n")
    result = parse_os_release(path)
    assert result.features == frozenset()


def test_parse_missing_file_returns_default():
    result = parse_os_release("/nonexistent/os-release")
    assert isinstance(result, OsRelease)
    assert result.id is None
    assert result.gardenlinux_version is None
    assert result.features == frozenset()


def test_parse_ignores_comments_and_blank_lines(tmp_path):
    path = write_os_release(
        tmp_path,
        """\
        # This is a comment
        ID=gardenlinux

        NAME="Garden Linux"
        """,
    )
    result = parse_os_release(path)
    assert result.id == "gardenlinux"
    assert result.name == "Garden Linux"


def test_raw_contains_all_keys(tmp_path):
    path = write_os_release(
        tmp_path,
        """\
        ID=gardenlinux
        GARDENLINUX_VERSION=1592.0.0
        CUSTOM_KEY=custom_value
        """,
    )
    result = parse_os_release(path)
    assert result.raw["ID"] == "gardenlinux"
    assert result.raw["GARDENLINUX_VERSION"] == "1592.0.0"
    assert result.raw["CUSTOM_KEY"] == "custom_value"


def test_os_release_is_frozen(tmp_path):
    path = write_os_release(tmp_path, "ID=gardenlinux\n")
    result = parse_os_release(path)
    with pytest.raises((AttributeError, TypeError)):
        result.id = "changed"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# OsRelease.semver_tuple()
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "version,expected",
    [
        ("1592.0.0", (1592, 0, 0)),  # standard 3-segment
        ("1443.2", (1443, 2, 0)),  # legacy 2-segment
        ("2016.0", (2016, 0, 0)),  # pre-SemVer 2-segment
        ("2016", None),  # single segment rejected
        ("today", None),  # non-numeric (nightly)
        (None, None),  # missing version key
        ("1592.0.0-beta", None),  # mixed alphanumeric
    ],
)
def test_semver_tuple(version, expected, tmp_path):
    if version is None:
        path = write_os_release(tmp_path, "ID=gardenlinux\n")
    else:
        path = write_os_release(tmp_path, f"GARDENLINUX_VERSION={version}\n")
    result = parse_os_release(path)
    assert result.semver_tuple() == expected
