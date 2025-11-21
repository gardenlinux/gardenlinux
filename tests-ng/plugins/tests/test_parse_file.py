"""Comprehensive tests for parse_file.py plugin."""

import re

import pytest
from plugins.parse_file import ParseFile

# ============================================================================
# ParseFile Tests - File-based operations
# ============================================================================


class TestParseFileHasLine:
    """Tests for ParseFile.has_line() method."""

    def test_has_line_found(self, parse_file: ParseFile, tmp_path):
        """Test finding a line in a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("This is a test line\nAnother line\nMulti word line\n")

        assert parse_file.has_line(test_file, "test line")
        assert parse_file.has_line(test_file, "Another")
        assert not parse_file.has_line(test_file, "missing")

    def test_has_line_with_comments_json(self, parse_file: ParseFile, tmp_path):
        """Test that JSON format doesn't filter comments (JSON has no comments)."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}\n# This is not a comment in JSON\n')

        # JSON doesn't support comments, so # should be treated as part of content
        assert parse_file.has_line(test_file, "# This is not a comment", format="json")

    def test_has_line_with_comments_yaml(self, parse_file: ParseFile, tmp_path):
        """Test comment filtering for YAML format."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("# Comment line\nkey: value\n# Another comment\n")

        assert parse_file.has_line(test_file, "key: value")
        assert not parse_file.has_line(test_file, "Comment line")

    def test_has_line_with_comments_ini(self, parse_file: ParseFile, tmp_path):
        """Test comment filtering for INI format (supports both ; and #)."""
        test_file = tmp_path / "test.ini"
        test_file.write_text("; Semicolon comment\nkey = value\n# Hash comment\n")

        assert parse_file.has_line(test_file, "key = value")
        assert not parse_file.has_line(test_file, "Semicolon comment")
        assert not parse_file.has_line(test_file, "Hash comment")

    def test_has_line_format_auto_detection(self, parse_file: ParseFile, tmp_path):
        """Test automatic format detection from file extension."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("# Comment\nkey: value\n")

        # Should auto-detect YAML and filter comments
        assert parse_file.has_line(test_file, "key: value")
        assert not parse_file.has_line(test_file, "Comment")

    def test_has_line_ignore_missing_true(self, parse_file: ParseFile, tmp_path):
        """Test ignore_missing=True returns False for missing file."""
        missing_file = tmp_path / "missing.txt"
        assert not parse_file.has_line(missing_file, "pattern", ignore_missing=True)

    def test_has_line_ignore_missing_false(self, parse_file: ParseFile, tmp_path):
        """Test ignore_missing=False raises FileNotFoundError for missing file."""
        missing_file = tmp_path / "missing.txt"
        with pytest.raises(FileNotFoundError, match="File not found or cannot be read"):
            parse_file.has_line(missing_file, "pattern", ignore_missing=False)


class TestParseFileHasLines:
    """Tests for ParseFile.has_lines() method."""

    def test_has_lines_in_order(self, parse_file: ParseFile, tmp_path):
        """Test finding multiple lines in order."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3\n")

        assert parse_file.has_lines(test_file, ["line1", "line2"], order=True)
        assert parse_file.has_lines(test_file, ["line2", "line3"], order=True)
        assert not parse_file.has_lines(test_file, ["line3", "line1"], order=True)

    def test_has_lines_any_order(self, parse_file: ParseFile, tmp_path):
        """Test finding multiple lines in any order."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3\n")

        assert parse_file.has_lines(test_file, ["line1", "line2"], order=False)
        assert parse_file.has_lines(test_file, ["line3", "line1"], order=False)
        assert not parse_file.has_lines(test_file, ["line1", "missing"], order=False)

    def test_has_lines_with_comments(self, parse_file: ParseFile, tmp_path):
        """Test lines() filters comments correctly."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("# Comment 1\nline1\n# Comment 2\nline2\n")

        assert parse_file.has_lines(test_file, ["line1", "line2"], order=True)
        assert not parse_file.has_lines(test_file, ["Comment 1", "line1"], order=True)

    def test_has_lines_empty_list(self, parse_file: ParseFile, tmp_path):
        """Test has_lines() with empty patterns list."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\n")
        assert parse_file.has_lines(test_file, [], order=True)
        assert parse_file.has_lines(test_file, [], order=False)

    def test_has_lines_single_pattern(self, parse_file: ParseFile, tmp_path):
        """Test has_lines() with single pattern."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\n")
        assert parse_file.has_lines(test_file, ["line1"], order=True)
        assert parse_file.has_lines(test_file, ["line1"], order=False)
        assert not parse_file.has_lines(test_file, ["missing"], order=True)

    def test_has_lines_ignore_missing(self, parse_file: ParseFile, tmp_path):
        """Test ignore_missing parameter for lines()."""
        missing_file = tmp_path / "missing.txt"
        assert not parse_file.has_lines(missing_file, ["pattern"], ignore_missing=True)

        with pytest.raises(FileNotFoundError):
            parse_file.has_lines(missing_file, ["pattern"], ignore_missing=False)


class TestParseFileMatchRegex:
    """Tests for ParseFile.match_regex() method."""

    def test_match_regex_match(self, parse_file: ParseFile, tmp_path):
        """Test regex pattern matching."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Boot completed in 2.345s\n")

        match = parse_file.match_regex(test_file, r"Boot completed in ([\d.]+)s")
        assert match is not None
        assert match.group(1) == "2.345"

    def test_match_regex_no_match(self, parse_file: ParseFile, tmp_path):
        """Test regex when pattern doesn't match."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Some other text\n")

        match = parse_file.match_regex(test_file, r"Boot completed in ([\d.]+)s")
        assert match is None

    def test_match_regex_with_flags(self, parse_file: ParseFile, tmp_path):
        """Test regex with flags."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("UPPERCASE TEXT\n")

        match = parse_file.match_regex(test_file, r"uppercase", flags=re.IGNORECASE)
        assert match is not None

    def test_match_regex_ignore_missing(self, parse_file: ParseFile, tmp_path):
        """Test ignore_missing parameter for match_regex()."""
        missing_file = tmp_path / "missing.txt"
        assert (
            parse_file.match_regex(missing_file, r"pattern", ignore_missing=True)
            is None
        )

        with pytest.raises(FileNotFoundError):
            parse_file.match_regex(missing_file, r"pattern", ignore_missing=False)

    def test_match_regex_empty_file(self, parse_file: ParseFile, tmp_path):
        """Test regex with empty file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("")
        match = parse_file.match_regex(test_file, r"pattern")
        assert match is None

    def test_match_regex_multiline_flag(self, parse_file: ParseFile, tmp_path):
        """Test regex with MULTILINE flag."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\n")
        match = parse_file.match_regex(test_file, r"^line2$", flags=re.MULTILINE)
        assert match is not None


class TestParseFileListContainsValue:
    """Tests for ParseFile.list_contains_value() method."""

    def test_list_contains_value_json(self, parse_file: ParseFile, tmp_path):
        """Test list_contains_value() with JSON format."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"groups": ["admin", "users", "developers"]}')

        assert parse_file.list_contains_value(
            test_file, "groups", "admin", format="json"
        )
        assert parse_file.list_contains_value(
            test_file, "groups", "users", format="json"
        )
        assert not parse_file.list_contains_value(
            test_file, "groups", "root", format="json"
        )

    def test_list_contains_value_yaml(self, parse_file: ParseFile, tmp_path):
        """Test list_contains_value() with YAML format."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("groups:\n  - admin\n  - users\n")

        assert parse_file.list_contains_value(
            test_file, "groups", "admin", format="yaml"
        )
        assert not parse_file.list_contains_value(
            test_file, "groups", "root", format="yaml"
        )

    def test_list_contains_value_toml(self, parse_file: ParseFile, tmp_path):
        """Test list_contains_value() with TOML format."""
        test_file = tmp_path / "test.toml"
        test_file.write_text('groups = ["admin", "users"]\n')

        assert parse_file.list_contains_value(
            test_file, "groups", "admin", format="toml"
        )
        assert not parse_file.list_contains_value(
            test_file, "groups", "root", format="toml"
        )

    def test_list_contains_value_nested_path(self, parse_file: ParseFile, tmp_path):
        """Test list_contains_value() with nested path."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"user": {"groups": ["admin", "users"]}}')

        assert parse_file.list_contains_value(
            test_file, "user.groups", "admin", format="json"
        )

    def test_list_contains_value_format_auto_detection(
        self, parse_file: ParseFile, tmp_path
    ):
        """Test list_contains_value() with format auto-detection."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"groups": ["admin"]}')

        assert parse_file.list_contains_value(test_file, "groups", "admin")

    def test_list_contains_value_ignore_missing(self, parse_file: ParseFile, tmp_path):
        """Test ignore_missing parameter for list_contains_value()."""
        missing_file = tmp_path / "missing.json"
        assert not parse_file.list_contains_value(
            missing_file, "groups", "admin", format="json", ignore_missing=True
        )

    def test_list_contains_value_empty_list(self, parse_file: ParseFile, tmp_path):
        """Test list_contains_value() with empty list."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"groups": []}')
        assert not parse_file.list_contains_value(
            test_file, "groups", "admin", format="json"
        )

    def test_list_contains_value_list_with_duplicates(
        self, parse_file: ParseFile, tmp_path
    ):
        """Test list_contains_value() with list containing duplicates."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"groups": ["admin", "admin", "users"]}')
        assert parse_file.list_contains_value(
            test_file, "groups", "admin", format="json"
        )


class TestParseFileGetValue:
    """Tests for ParseFile.get_value() method."""

    def test_get_value_json(self, parse_file: ParseFile, tmp_path):
        """Test get_value() with JSON format."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"database": {"host": "localhost", "port": 5432}}')

        assert (
            parse_file.get_value(test_file, "database.host", format="json")
            == "localhost"
        )
        assert parse_file.get_value(test_file, "database.port", format="json") == 5432
        assert (
            parse_file.get_value(test_file, "database.missing", format="json") is None
        )

    def test_get_value_yaml(self, parse_file: ParseFile, tmp_path):
        """Test get_value() with YAML format."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("database:\n  host: localhost\n  port: 5432\n")

        assert (
            parse_file.get_value(test_file, "database.host", format="yaml")
            == "localhost"
        )
        assert parse_file.get_value(test_file, "database.port", format="yaml") == 5432

    def test_get_value_toml(self, parse_file: ParseFile, tmp_path):
        """Test get_value() with TOML format."""
        test_file = tmp_path / "test.toml"
        test_file.write_text('[database]\nhost = "localhost"\nport = 5432\n')

        assert (
            parse_file.get_value(test_file, "database.host", format="toml")
            == "localhost"
        )
        assert parse_file.get_value(test_file, "database.port", format="toml") == 5432

    def test_get_value_ini(self, parse_file: ParseFile, tmp_path):
        """Test get_value() with INI format."""
        test_file = tmp_path / "test.ini"
        test_file.write_text("[database]\nhost = localhost\nport = 5432\n")

        assert (
            parse_file.get_value(test_file, "database.host", format="ini")
            == "localhost"
        )
        assert parse_file.get_value(test_file, "database.port", format="ini") == "5432"

    def test_get_value_keyval(self, parse_file: ParseFile, tmp_path):
        """Test get_value() with keyval format."""
        test_file = tmp_path / "test.env"
        test_file.write_text("DATABASE_HOST=localhost\nDATABASE_PORT=5432\n")

        assert (
            parse_file.get_value(test_file, "DATABASE_HOST", format="keyval")
            == "localhost"
        )
        assert (
            parse_file.get_value(test_file, "DATABASE_PORT", format="keyval") == "5432"
        )

    def test_get_value_format_auto_detection(self, parse_file: ParseFile, tmp_path):
        """Test get_value() with format auto-detection."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')

        assert parse_file.get_value(test_file, "key") == "value"

    def test_get_value_ignore_missing(self, parse_file: ParseFile, tmp_path):
        """Test ignore_missing parameter for get_value()."""
        missing_file = tmp_path / "missing.json"
        assert (
            parse_file.get_value(
                missing_file, "key", format="json", ignore_missing=True
            )
            is None
        )


class TestParseFileMatchValues:
    """Tests for ParseFile.match_values() method."""

    def test_match_values_json(self, parse_file: ParseFile, tmp_path):
        """Test match_values() with JSON format."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"database": {"host": "localhost", "port": 5432}}')

        result = parse_file.match_values(
            test_file,
            {
                "database.host": "localhost",
                "database.port": 5432,
                "database.missing": "value",
            },
            format="json",
        )
        assert result.all_match is False
        assert "database.missing" in result.missing
        assert len(result.wrong) == 0

    def test_match_values_json_all_match(self, parse_file: ParseFile, tmp_path):
        """Test match_values() with JSON format when all values match."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"database": {"host": "localhost", "port": 5432}}')

        result = parse_file.match_values(
            test_file,
            {"database.host": "localhost", "database.port": 5432},
            format="json",
        )
        assert result.all_match is True
        assert len(result.missing) == 0
        assert len(result.wrong) == 0

    def test_match_values_yaml(self, parse_file: ParseFile, tmp_path):
        """Test match_values() with YAML format."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("database:\n  host: localhost\n  port: 5432\n")

        result = parse_file.match_values(
            test_file,
            {"database.host": "localhost", "database.port": 5432},
            format="yaml",
        )
        assert result.all_match is True

    def test_match_values_toml(self, parse_file: ParseFile, tmp_path):
        """Test match_values() with TOML format."""
        test_file = tmp_path / "test.toml"
        test_file.write_text('[database]\nhost = "localhost"\nport = 5432\n')

        result = parse_file.match_values(
            test_file,
            {"database.host": "localhost", "database.port": 5432},
            format="toml",
        )
        assert result.all_match is True

    def test_match_values_ini(self, parse_file: ParseFile, tmp_path):
        """Test match_values() with INI format."""
        test_file = tmp_path / "test.ini"
        test_file.write_text("[database]\nhost = localhost\nport = 5432\n")

        result = parse_file.match_values(
            test_file,
            {"database.host": "localhost", "database.port": "5432"},
            format="ini",
        )
        assert result.all_match is True

    def test_match_values_keyval(self, parse_file: ParseFile, tmp_path):
        """Test match_values() with keyval format."""
        test_file = tmp_path / "test.env"
        test_file.write_text("DATABASE_HOST=localhost\nDATABASE_PORT=5432\n")

        result = parse_file.match_values(
            test_file,
            {
                "DATABASE_HOST": "localhost",
                "DATABASE_PORT": "5432",
                "MISSING_KEY": "value",
            },
            format="keyval",
        )
        assert result.all_match is False
        assert "MISSING_KEY" in result.missing

    def test_match_values_format_auto_detection(self, parse_file: ParseFile, tmp_path):
        """Test match_values() with format auto-detection."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key1": "value1", "key2": "value2"}')

        result = parse_file.match_values(
            test_file, {"key1": "value1", "key2": "value2"}
        )
        assert result.all_match is True

    def test_match_values_empty_dict(self, parse_file: ParseFile, tmp_path):
        """Test match_values() with empty dict."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')

        result = parse_file.match_values(test_file, {}, format="json")
        assert result.all_match is True
        assert len(result.missing) == 0
        assert len(result.wrong) == 0

    def test_match_values_all_missing(self, parse_file: ParseFile, tmp_path):
        """Test match_values() when all keys are missing."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"other": "value"}')

        result = parse_file.match_values(
            test_file, {"missing1": "v1", "missing2": "v2"}, format="json"
        )
        assert result.all_match is False
        assert "missing1" in result.missing
        assert "missing2" in result.missing

    def test_match_values_wrong_values(self, parse_file: ParseFile, tmp_path):
        """Test match_values() with wrong values."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key1": "value1", "key2": "wrong"}')

        result = parse_file.match_values(
            test_file, {"key1": "value1", "key2": "value2"}, format="json"
        )
        assert result.all_match is False
        assert len(result.missing) == 0
        assert "key2" in result.wrong
        assert result.wrong["key2"] == ("value2", "wrong")

    def test_match_values_mixed_missing_and_wrong(
        self, parse_file: ParseFile, tmp_path
    ):
        """Test match_values() with mix of missing and wrong values."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key1": "value1", "key2": "wrong"}')

        result = parse_file.match_values(
            test_file,
            {"key1": "value1", "key2": "value2", "missing": "value"},
            format="json",
        )
        assert result.all_match is False
        assert "missing" in result.missing
        assert "key2" in result.wrong

    def test_match_values_ignore_missing(self, parse_file: ParseFile, tmp_path):
        """Test ignore_missing parameter for match_values()."""
        missing_file = tmp_path / "missing.json"
        result = parse_file.match_values(
            missing_file,
            {"key1": "v1", "key2": "v2"},
            format="json",
            ignore_missing=True,
        )
        assert result.all_match is False
        assert "key1" in result.missing
        assert "key2" in result.missing

    def test_match_values_boolean_context(self, parse_file: ParseFile, tmp_path):
        """Test ValidationResult can be used in boolean context."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')

        result_match = parse_file.match_values(
            test_file, {"key": "value"}, format="json"
        )
        result_mismatch = parse_file.match_values(
            test_file, {"key": "wrong"}, format="json"
        )

        # Test __bool__() method
        assert result_match  # Should be True
        assert not result_mismatch  # Should be False

    def test_match_values_wrong_list_formatting(self, parse_file: ParseFile, tmp_path):
        """Test ValidationResult.wrong_list formatting."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key1": "value1", "key2": "wrong2", "key3": "wrong3"}')

        result = parse_file.match_values(
            test_file,
            {"key1": "value1", "key2": "value2", "key3": "value3"},
            format="json",
        )

        formatted = ", ".join(result.wrong_list)
        assert "key2" in formatted
        assert "key3" in formatted
        assert "wrong2" in formatted
        assert "wrong3" in formatted
        assert "value2" in formatted
        assert "value3" in formatted

        # Test with no wrong values
        result_match = parse_file.match_values(
            test_file, {"key1": "value1"}, format="json"
        )
        assert result_match.wrong_list == []

    def test_match_values_wrong_list(self, parse_file: ParseFile, tmp_path):
        """Test ValidationResult.wrong_list list."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key1": "wrong1", "key2": "wrong2"}')

        result = parse_file.match_values(
            test_file, {"key1": "value1", "key2": "value2"}, format="json"
        )

        assert len(result.wrong_list) == 2
        assert "key1: 'wrong1'!='value1'" in result.wrong_list
        assert "key2: 'wrong2'!='value2'" in result.wrong_list
        assert (
            ", ".join(result.wrong_list)
            == "key1: 'wrong1'!='value1', key2: 'wrong2'!='value2'"
        )

        # Test with no wrong values
        result_match = parse_file.match_values(
            test_file, {"key1": "wrong1"}, format="json"
        )
        assert result_match.wrong_list == []


class TestParseFileHasKey:
    """Tests for ParseFile.has_key() method."""

    def test_has_key_json(self, parse_file: ParseFile, tmp_path):
        """Test has_key() with JSON format."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"database": {"host": "localhost"}}')

        assert parse_file.has_key(test_file, "database.host", format="json")
        assert parse_file.has_key(test_file, "database", format="json")
        assert not parse_file.has_key(test_file, "database.port", format="json")

    def test_has_key_all_formats(self, parse_file: ParseFile, tmp_path):
        """Test has_key() with all supported formats."""
        formats_data = {
            "json": '{"key": "value"}',
            "yaml": "key: value\n",
            "toml": 'key = "value"\n',
            "ini": "[section]\nkey = value\n",
            "keyval": "KEY=value\n",
        }

        for fmt, content in formats_data.items():
            test_file = tmp_path / f"test.{fmt if fmt != 'keyval' else 'env'}"
            test_file.write_text(content)

            if fmt == "keyval":
                assert parse_file.has_key(test_file, "KEY", format=fmt)
            elif fmt == "ini":
                assert parse_file.has_key(test_file, "section.key", format=fmt)
            else:
                assert parse_file.has_key(test_file, "key", format=fmt)

    def test_has_key_ignore_missing(self, parse_file: ParseFile, tmp_path):
        """Test ignore_missing parameter for has_key()."""
        missing_file = tmp_path / "missing.json"
        assert not parse_file.has_key(
            missing_file, "key", format="json", ignore_missing=True
        )


class TestParseFileMatchKeys:
    """Tests for ParseFile.match_keys() method."""

    def test_match_keys_json(self, parse_file: ParseFile, tmp_path):
        """Test match_keys() with JSON format."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"database": {"host": "localhost", "port": 5432}}')

        result = parse_file.match_keys(
            test_file,
            ["database.host", "database.port", "database.missing"],
            format="json",
        )
        assert result.all_match is False
        assert "database.missing" in result.missing
        assert len(result.wrong) == 0

    def test_match_keys_json_all_exist(self, parse_file: ParseFile, tmp_path):
        """Test match_keys() with JSON format when all keys exist."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"database": {"host": "localhost", "port": 5432}}')

        result = parse_file.match_keys(
            test_file, ["database.host", "database.port"], format="json"
        )
        assert result.all_match is True
        assert len(result.missing) == 0
        assert len(result.wrong) == 0

    def test_match_keys_yaml(self, parse_file: ParseFile, tmp_path):
        """Test match_keys() with YAML format."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("database:\n  host: localhost\n  port: 5432\n")

        result = parse_file.match_keys(
            test_file, ["database.host", "database.port"], format="yaml"
        )
        assert result.all_match is True

    def test_match_keys_toml(self, parse_file: ParseFile, tmp_path):
        """Test match_keys() with TOML format."""
        test_file = tmp_path / "test.toml"
        test_file.write_text('[database]\nhost = "localhost"\nport = 5432\n')

        result = parse_file.match_keys(
            test_file, ["database.host", "database.port"], format="toml"
        )
        assert result.all_match is True

    def test_match_keys_ini(self, parse_file: ParseFile, tmp_path):
        """Test match_keys() with INI format."""
        test_file = tmp_path / "test.ini"
        test_file.write_text("[database]\nhost = localhost\nport = 5432\n")

        result = parse_file.match_keys(
            test_file, ["database.host", "database.port"], format="ini"
        )
        assert result.all_match is True

    def test_match_keys_keyval(self, parse_file: ParseFile, tmp_path):
        """Test match_keys() with keyval format."""
        test_file = tmp_path / "test.env"
        test_file.write_text("DATABASE_HOST=localhost\nDATABASE_PORT=5432\n")

        result = parse_file.match_keys(
            test_file,
            ["DATABASE_HOST", "DATABASE_PORT", "MISSING_KEY"],
            format="keyval",
        )
        assert result.all_match is False
        assert "MISSING_KEY" in result.missing
        assert len(result.wrong) == 0

    def test_match_keys_format_auto_detection(self, parse_file: ParseFile, tmp_path):
        """Test match_keys() with format auto-detection."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key1": "value1", "key2": "value2"}')

        result = parse_file.match_keys(test_file, ["key1", "key2"])
        assert result.all_match is True

    def test_match_keys_empty_list(self, parse_file: ParseFile, tmp_path):
        """Test match_keys() with empty list."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')

        result = parse_file.match_keys(test_file, [], format="json")
        assert result.all_match is True
        assert len(result.missing) == 0
        assert len(result.wrong) == 0

    def test_match_keys_all_missing(self, parse_file: ParseFile, tmp_path):
        """Test match_keys() when all keys are missing."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"other": "value"}')

        result = parse_file.match_keys(
            test_file, ["missing1", "missing2"], format="json"
        )
        assert result.all_match is False
        assert "missing1" in result.missing
        assert "missing2" in result.missing

    def test_match_keys_ignore_missing(self, parse_file: ParseFile, tmp_path):
        """Test ignore_missing parameter for match_keys()."""
        missing_file = tmp_path / "missing.json"
        result = parse_file.match_keys(
            missing_file, ["key1", "key2"], format="json", ignore_missing=True
        )
        assert result.all_match is False
        assert "key1" in result.missing
        assert "key2" in result.missing


class TestParseFileGetPaths:
    """Tests for ParseFile.get_paths() method."""

    def test_get_paths_json(self, parse_file: ParseFile, tmp_path):
        """Test get_paths() with JSON format."""
        test_file = tmp_path / "test.json"
        test_file.write_text(
            '{"host": "localhost", "database": {"host": "localhost", "port": 5432}}'
        )

        paths = parse_file.get_paths(test_file, "localhost", format="json")
        assert "host" in paths
        assert "database.host" in paths
        assert len(paths) == 2

    def test_get_paths_yaml(self, parse_file: ParseFile, tmp_path):
        """Test get_paths() with YAML format."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("host: localhost\ndatabase:\n  host: localhost\n")

        paths = parse_file.get_paths(test_file, "localhost", format="yaml")
        assert "host" in paths
        assert "database.host" in paths

    def test_get_paths_not_found(self, parse_file: ParseFile, tmp_path):
        """Test get_paths() when value is not found."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')

        paths = parse_file.get_paths(test_file, "missing", format="json")
        assert paths == []

    def test_get_paths_ignore_missing(self, parse_file: ParseFile, tmp_path):
        """Test ignore_missing parameter for get_paths()."""
        missing_file = tmp_path / "missing.json"
        assert (
            parse_file.get_paths(
                missing_file, "value", format="json", ignore_missing=True
            )
            == []
        )

    def test_get_paths_toml(self, parse_file: ParseFile, tmp_path):
        """Test get_paths() with TOML format."""
        test_file = tmp_path / "test.toml"
        test_file.write_text('host = "localhost"\n[database]\nhost = "localhost"\n')
        paths = parse_file.get_paths(test_file, "localhost", format="toml")
        assert "host" in paths
        assert "database.host" in paths

    def test_get_paths_ini(self, parse_file: ParseFile, tmp_path):
        """Test get_paths() with INI format."""
        test_file = tmp_path / "test.ini"
        test_file.write_text(
            "[section]\nhost = localhost\n[database]\nhost = localhost\n"
        )
        paths = parse_file.get_paths(test_file, "localhost", format="ini")
        assert "section.host" in paths
        assert "database.host" in paths

    def test_get_paths_keyval(self, parse_file: ParseFile, tmp_path):
        """Test get_paths() with keyval format."""
        test_file = tmp_path / "test.env"
        test_file.write_text("HOST=localhost\nDATABASE_HOST=localhost\n")
        paths = parse_file.get_paths(test_file, "localhost", format="keyval")
        assert "HOST" in paths
        assert "DATABASE_HOST" in paths

    def test_get_paths_empty_structure(self, parse_file: ParseFile, tmp_path):
        """Test get_paths() with empty structure."""
        test_file = tmp_path / "test.json"
        test_file.write_text("{}")
        paths = parse_file.get_paths(test_file, "value", format="json")
        assert paths == []

    def test_get_paths_nested_same_value(self, parse_file: ParseFile, tmp_path):
        """Test get_paths() finds same value at different nesting levels."""
        test_file = tmp_path / "test.json"
        test_file.write_text(
            '{"level1": {"level2": {"value": "target"}, "value": "target"}, "value": "target"}'
        )
        paths = parse_file.get_paths(test_file, "target", format="json")
        assert "value" in paths
        assert "level1.value" in paths
        assert "level1.level2.value" in paths
        assert len(paths) == 3


# ============================================================================
# Format Auto-detection Tests
# ============================================================================


class TestFormatAutoDetection:
    """Tests for format auto-detection from file extensions."""

    def test_auto_detect_json(self, parse_file: ParseFile, tmp_path):
        """Test auto-detection of JSON format."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')
        assert parse_file.get_value(test_file, "key") == "value"

    def test_auto_detect_yaml(self, parse_file: ParseFile, tmp_path):
        """Test auto-detection of YAML format."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("key: value\n")
        assert parse_file.get_value(test_file, "key") == "value"

        test_file = tmp_path / "test.yml"
        test_file.write_text("key: value\n")
        assert parse_file.get_value(test_file, "key") == "value"

    def test_auto_detect_toml(self, parse_file: ParseFile, tmp_path):
        """Test auto-detection of TOML format."""
        test_file = tmp_path / "test.toml"
        test_file.write_text('key = "value"\n')
        assert parse_file.get_value(test_file, "key") == "value"

    def test_auto_detect_ini(self, parse_file: ParseFile, tmp_path):
        """Test auto-detection of INI format."""
        test_file = tmp_path / "test.ini"
        test_file.write_text("[section]\nkey = value\n")
        assert parse_file.get_value(test_file, "section.key") == "value"

        test_file = tmp_path / "test.cfg"
        test_file.write_text("[section]\nkey = value\n")
        assert parse_file.get_value(test_file, "section.key") == "value"

    def test_auto_detect_keyval(self, parse_file: ParseFile, tmp_path):
        """Test auto-detection of keyval format."""
        test_file = tmp_path / "test.conf"
        test_file.write_text("key = value\n")
        assert parse_file.get_value(test_file, "key") == "value"

        test_file = tmp_path / "test.env"
        test_file.write_text("KEY=value\n")
        assert parse_file.get_value(test_file, "KEY") == "value"

    def test_auto_detect_no_extension(self, parse_file: ParseFile, tmp_path):
        """Test error when format cannot be auto-detected."""
        test_file = tmp_path / "test"
        test_file.write_text('{"key": "value"}')
        with pytest.raises(ValueError, match="Cannot auto-detect format"):
            parse_file.get_value(test_file, "key")


# ============================================================================
# Comment Handling Tests
# ============================================================================


class TestCommentHandling:
    """Tests for comment filtering across different formats."""

    def test_comments_json_no_filtering(self, parse_file: ParseFile, tmp_path):
        """Test that JSON doesn't filter comments (JSON has no comment support)."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}\n# This is not a comment\n')
        # In JSON, # is part of the content, not a comment
        assert parse_file.has_line(test_file, "# This is not a comment", format="json")

    def test_comments_yaml_hash(self, parse_file: ParseFile, tmp_path):
        """Test YAML comment filtering with #."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("# Comment\nkey: value\n")
        assert parse_file.has_line(test_file, "key: value", format="yaml")
        assert not parse_file.has_line(test_file, "Comment", format="yaml")

    def test_comments_ini_semicolon_and_hash(self, parse_file: ParseFile, tmp_path):
        """Test INI comment filtering with both ; and #."""
        test_file = tmp_path / "test.ini"
        test_file.write_text("; Semicolon comment\nkey = value\n# Hash comment\n")
        assert parse_file.has_line(test_file, "key = value", format="ini")
        assert not parse_file.has_line(test_file, "Semicolon comment", format="ini")
        assert not parse_file.has_line(test_file, "Hash comment", format="ini")

    def test_comments_toml_hash(self, parse_file: ParseFile, tmp_path):
        """Test TOML comment filtering with #."""
        test_file = tmp_path / "test.toml"
        test_file.write_text('# Comment\nkey = "value"\n')
        assert parse_file.has_line(test_file, "key =", format="toml")
        assert not parse_file.has_line(test_file, "Comment", format="toml")

    def test_comments_keyval_hash(self, parse_file: ParseFile, tmp_path):
        """Test keyval comment filtering with #."""
        test_file = tmp_path / "test.env"
        test_file.write_text("# Comment\nKEY=value\n")
        assert parse_file.has_line(test_file, "KEY=value", format="keyval")
        assert not parse_file.has_line(test_file, "Comment", format="keyval")


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_missing_file_error_message(self, parse_file: ParseFile, tmp_path):
        """Test that missing file error message is helpful."""
        missing_file = tmp_path / "missing.txt"
        with pytest.raises(FileNotFoundError) as exc_info:
            parse_file.has_line(missing_file, "pattern")
        assert "File not found or cannot be read" in str(exc_info.value)
        assert "missing.txt" in str(exc_info.value)

    def test_invalid_json(self, parse_file: ParseFile, tmp_path):
        """Test handling of invalid JSON."""
        test_file = tmp_path / "test.json"
        test_file.write_text("{invalid json}")
        with pytest.raises(Exception):  # json.JSONDecodeError
            parse_file.get_value(test_file, "key", format="json")

    def test_invalid_path_in_get_value(self, parse_file: ParseFile, tmp_path):
        """Test get_value() with invalid path."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')
        # Should return None for non-existent path, not raise error
        assert (
            parse_file.get_value(test_file, "nonexistent.path", format="json") is None
        )
