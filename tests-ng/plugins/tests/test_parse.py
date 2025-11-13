"""Comprehensive tests for parse.py plugin using the parse fixture."""

import re

import pytest

# ============================================================================
# Parse Tests - Direct string-based operations
# ============================================================================


class TestParseHasLine:
    """Tests for Parse.has_line() method."""

    def test_has_line_found(self, parse):
        """Test finding a line in content."""
        parser = parse.from_str("line1\nline2\nline3\n")
        assert parser.has_line("line2")
        assert not parser.has_line("missing")

    def test_has_line_with_comments_default(self, parse):
        """Test comment filtering with default comment char."""
        parser = parse.from_str("# Comment\nkey: value\n")
        assert parser.has_line("key: value")
        assert not parser.has_line("Comment")

    def test_has_line_with_comments_json_format(self, parse):
        """Test that JSON format doesn't filter comments."""
        parser = parse.from_str('{"key": "value"}\n# Not a comment\n')
        # JSON has no comment support, so # is part of content
        assert parser.has_line("# Not a comment", format="json")

    def test_has_line_with_comments_ini_format(self, parse):
        """Test INI format supports both ; and # comments."""
        parser = parse.from_str("; Semicolon comment\nkey = value\n# Hash comment\n")
        assert parser.has_line("key = value", format="ini")
        assert not parser.has_line("Semicolon comment", format="ini")
        assert not parser.has_line("Hash comment", format="ini")

    def test_has_line_with_explicit_comment_char(self, parse):
        """Test explicit comment character."""
        parser = parse.from_str("// Comment\nkey: value\n")
        assert parser.has_line("key: value", comment_char="//")
        assert not parser.has_line("Comment", comment_char="//")

    def test_has_line_with_multiple_comment_chars(self, parse):
        """Test multiple comment characters."""
        parser = parse.from_str("; Comment1\nkey: value\n# Comment2\n")
        assert parser.has_line("key: value", comment_char=[";", "#"])
        assert not parser.has_line("Comment1", comment_char=[";", "#"])
        assert not parser.has_line("Comment2", comment_char=[";", "#"])


class TestParseHasLines:
    """Tests for Parse.has_lines() method."""

    def test_has_lines_in_order(self, parse):
        """Test finding lines in order."""
        parser = parse.from_str("line1\nline2\nline3\n")
        assert parser.has_lines(["line1", "line2"], order=True)
        assert not parser.has_lines(["line3", "line1"], order=True)

    def test_has_lines_any_order(self, parse):
        """Test finding lines in any order."""
        parser = parse.from_str("line1\nline2\nline3\n")
        assert parser.has_lines(["line1", "line2"], order=False)
        assert parser.has_lines(["line3", "line1"], order=False)
        assert not parser.has_lines(["line1", "missing"], order=False)

    def test_has_lines_with_comments(self, parse):
        """Test lines() filters comments."""
        parser = parse.from_str("# Comment\nline1\n# Another\nline2\n")
        assert parser.has_lines(["line1", "line2"], order=True)
        assert not parser.has_lines(["Comment", "line1"], order=True)

    def test_has_lines_empty_list(self, parse):
        """Test has_lines() with empty patterns list."""
        parser = parse.from_str("line1\nline2\n")
        assert parser.has_lines([], order=True)
        assert parser.has_lines([], order=False)

    def test_has_lines_single_pattern(self, parse):
        """Test has_lines() with single pattern."""
        parser = parse.from_str("line1\nline2\n")
        assert parser.has_lines(["line1"], order=True)
        assert parser.has_lines(["line1"], order=False)
        assert not parser.has_lines(["missing"], order=True)


class TestParseMatchRegex:
    """Tests for Parse.match_regex() method."""

    def test_match_regex_match(self, parse):
        """Test regex pattern matching."""
        parser = parse.from_str("Boot completed in 2.345s\n")
        match = parser.match_regex(r"Boot completed in ([\d.]+)s")
        assert match is not None
        assert match.group(1) == "2.345"

    def test_match_regex_no_match(self, parse):
        """Test regex when pattern doesn't match."""
        parser = parse.from_str("Some other text\n")
        match = parser.match_regex(r"Boot completed in ([\d.]+)s")
        assert match is None

    def test_match_regex_with_flags(self, parse):
        """Test regex with flags."""
        parser = parse.from_str("UPPERCASE TEXT\n")
        match = parser.match_regex(r"uppercase", flags=re.IGNORECASE)
        assert match is not None

    def test_match_regex_empty_content(self, parse):
        """Test regex with empty content."""
        parser = parse.from_str("")
        match = parser.match_regex(r"pattern")
        assert match is None

    def test_match_regex_multiline_flag(self, parse):
        """Test regex with MULTILINE flag."""
        parser = parse.from_str("line1\nline2\n")
        match = parser.match_regex(r"^line2$", flags=re.MULTILINE)
        assert match is not None

    def test_match_regex_dotall_flag(self, parse):
        """Test regex with DOTALL flag."""
        parser = parse.from_str("line1\nline2")
        match = parser.match_regex(r"line1.line2", flags=re.DOTALL)
        assert match is not None


class TestParseListContainsValue:
    """Tests for Parse.list_contains_value() method."""

    def test_list_contains_value_json(self, parse):
        """Test list_contains_value() with JSON format."""
        parser = parse.from_str('{"groups": ["admin", "users"]}')
        assert parser.list_contains_value("groups", "admin", format="json")
        assert not parser.list_contains_value("groups", "root", format="json")

    def test_list_contains_value_yaml(self, parse):
        """Test list_contains_value() with YAML format."""
        parser = parse.from_str("groups:\n  - admin\n  - users\n")
        assert parser.list_contains_value("groups", "admin", format="yaml")
        assert not parser.list_contains_value("groups", "root", format="yaml")

    def test_list_contains_value_toml(self, parse):
        """Test list_contains_value() with TOML format."""
        parser = parse.from_str('groups = ["admin", "users"]\n')
        assert parser.list_contains_value("groups", "admin", format="toml")
        assert not parser.list_contains_value("groups", "root", format="toml")

    def test_list_contains_value_nested_path(self, parse):
        """Test list_contains_value() with nested path."""
        parser = parse.from_str('{"user": {"groups": ["admin"]}}')
        assert parser.list_contains_value("user.groups", "admin", format="json")

    def test_list_contains_value_invalid_format(self, parse):
        """Test list_contains_value() raises error for unsupported format."""
        parser = parse.from_str("key = value\n")
        with pytest.raises(ValueError, match="Unsupported format"):
            parser.list_contains_value("key", "value", format="ini")

    def test_list_contains_value_path_not_found(self, parse):
        """Test list_contains_value() raises error when path doesn't exist."""
        parser = parse.from_str('{"other": "value"}')
        with pytest.raises(ValueError, match="List path.*not found"):
            parser.list_contains_value("groups", "admin", format="json")

    def test_list_contains_value_not_a_list(self, parse):
        """Test list_contains_value() raises error when path is not a list."""
        parser = parse.from_str('{"groups": "not a list"}')
        with pytest.raises(ValueError, match="is not a list"):
            parser.list_contains_value("groups", "admin", format="json")

    def test_list_contains_value_empty_list(self, parse):
        """Test list_contains_value() with empty list."""
        parser = parse.from_str('{"groups": []}')
        assert not parser.list_contains_value("groups", "admin", format="json")

    def test_list_contains_value_list_with_duplicates(self, parse):
        """Test list_contains_value() with list containing duplicates."""
        parser = parse.from_str('{"groups": ["admin", "admin", "users"]}')
        assert parser.list_contains_value("groups", "admin", format="json")


class TestParseGetValue:
    """Tests for Parse.get_value() method."""

    def test_get_value_json(self, parse):
        """Test get_value() with JSON format."""
        parser = parse.from_str('{"database": {"host": "localhost", "port": 5432}}')
        assert parser.get_value("database.host", format="json") == "localhost"
        assert parser.get_value("database.port", format="json") == 5432
        assert parser.get_value("database.missing", format="json") is None

    def test_get_value_yaml(self, parse):
        """Test get_value() with YAML format."""
        parser = parse.from_str("database:\n  host: localhost\n  port: 5432\n")
        assert parser.get_value("database.host", format="yaml") == "localhost"
        assert parser.get_value("database.port", format="yaml") == 5432

    def test_get_value_toml(self, parse):
        """Test get_value() with TOML format."""
        parser = parse.from_str('[database]\nhost = "localhost"\nport = 5432\n')
        assert parser.get_value("database.host", format="toml") == "localhost"
        assert parser.get_value("database.port", format="toml") == 5432

    def test_get_value_ini(self, parse):
        """Test get_value() with INI format."""
        parser = parse.from_str("[database]\nhost = localhost\nport = 5432\n")
        assert parser.get_value("database.host", format="ini") == "localhost"
        assert parser.get_value("database.port", format="ini") == "5432"

    def test_get_value_keyval(self, parse):
        """Test get_value() with keyval format."""
        parser = parse.from_str("DATABASE_HOST=localhost\nDATABASE_PORT=5432\n")
        assert parser.get_value("DATABASE_HOST", format="keyval") == "localhost"
        assert parser.get_value("DATABASE_PORT", format="keyval") == "5432"

    def test_get_value_invalid_format(self, parse):
        """Test get_value() raises error for invalid format."""
        parser = parse.from_str("some content")
        with pytest.raises(ValueError, match="Unsupported format"):
            parser.get_value("key", format="invalid")


class TestParseMatchValues:
    """Tests for Parse.match_values() method."""

    def test_match_values_json(self, parse):
        """Test match_values() with JSON format."""
        parser = parse.from_str('{"database": {"host": "localhost", "port": 5432}}')
        result = parser.match_values(
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

    def test_match_values_json_all_match(self, parse):
        """Test match_values() with JSON format when all values match."""
        parser = parse.from_str('{"database": {"host": "localhost", "port": 5432}}')
        result = parser.match_values(
            {"database.host": "localhost", "database.port": 5432}, format="json"
        )
        assert result.all_match is True
        assert len(result.missing) == 0
        assert len(result.wrong) == 0

    def test_match_values_yaml(self, parse):
        """Test match_values() with YAML format."""
        parser = parse.from_str("database:\n  host: localhost\n  port: 5432\n")
        result = parser.match_values(
            {"database.host": "localhost", "database.port": 5432}, format="yaml"
        )
        assert result.all_match is True

    def test_match_values_toml(self, parse):
        """Test match_values() with TOML format."""
        parser = parse.from_str('[database]\nhost = "localhost"\nport = 5432\n')
        result = parser.match_values(
            {"database.host": "localhost", "database.port": 5432}, format="toml"
        )
        assert result.all_match is True

    def test_match_values_ini(self, parse):
        """Test match_values() with INI format."""
        parser = parse.from_str("[database]\nhost = localhost\nport = 5432\n")
        result = parser.match_values(
            {"database.host": "localhost", "database.port": "5432"}, format="ini"
        )
        assert result.all_match is True

    def test_match_values_keyval(self, parse):
        """Test match_values() with keyval format."""
        parser = parse.from_str("DATABASE_HOST=localhost\nDATABASE_PORT=5432\n")
        result = parser.match_values(
            {
                "DATABASE_HOST": "localhost",
                "DATABASE_PORT": "5432",
                "MISSING_KEY": "value",
            },
            format="keyval",
        )
        assert result.all_match is False
        assert "MISSING_KEY" in result.missing

    def test_match_values_empty_dict(self, parse):
        """Test match_values() with empty dict."""
        parser = parse.from_str('{"key": "value"}')
        result = parser.match_values({}, format="json")
        assert result.all_match is True
        assert len(result.missing) == 0
        assert len(result.wrong) == 0

    def test_match_values_all_missing(self, parse):
        """Test match_values() when all keys are missing."""
        parser = parse.from_str('{"other": "value"}')
        result = parser.match_values(
            {"missing1": "v1", "missing2": "v2"}, format="json"
        )
        assert result.all_match is False
        assert "missing1" in result.missing
        assert "missing2" in result.missing

    def test_match_values_wrong_values(self, parse):
        """Test match_values() with wrong values."""
        parser = parse.from_str('{"key1": "value1", "key2": "wrong"}')
        result = parser.match_values(
            {"key1": "value1", "key2": "value2"}, format="json"
        )
        assert result.all_match is False
        assert len(result.missing) == 0
        assert "key2" in result.wrong
        assert result.wrong["key2"] == ("value2", "wrong")

    def test_match_values_mixed_missing_and_wrong(self, parse):
        """Test match_values() with mix of missing and wrong values."""
        parser = parse.from_str('{"key1": "value1", "key2": "wrong"}')
        result = parser.match_values(
            {"key1": "value1", "key2": "value2", "missing": "value"}, format="json"
        )
        assert result.all_match is False
        assert "missing" in result.missing
        assert "key2" in result.wrong

    def test_match_values_invalid_format(self, parse):
        """Test match_values() raises error for invalid format."""
        parser = parse.from_str("some content")
        with pytest.raises(ValueError, match="Unsupported format"):
            parser.match_values({"key": "value"}, format="invalid")

    def test_match_values_boolean_context(self, parse):
        """Test ValidationResult can be used in boolean context."""
        parser = parse.from_str('{"key": "value"}')
        result_match = parser.match_values({"key": "value"}, format="json")
        result_mismatch = parser.match_values({"key": "wrong"}, format="json")

        # Test __bool__() method
        assert result_match  # Should be True
        assert not result_mismatch  # Should be False

    def test_match_values_wrong_list_formatting(self, parse):
        """Test ValidationResult.wrong_list formatting."""
        parser = parse.from_str(
            '{"key1": "value1", "key2": "wrong2", "key3": "wrong3"}'
        )
        result = parser.match_values(
            {"key1": "value1", "key2": "value2", "key3": "value3"}, format="json"
        )

        formatted = ", ".join(result.wrong_list)
        assert "key2" in formatted
        assert "key3" in formatted
        assert "wrong2" in formatted
        assert "wrong3" in formatted
        assert "value2" in formatted
        assert "value3" in formatted

        # Test with no wrong values
        result_match = parser.match_values({"key1": "value1"}, format="json")
        assert result_match.wrong_list == []

    def test_match_values_wrong_list(self, parse):
        """Test ValidationResult.wrong_list list."""
        parser = parse.from_str('{"key1": "wrong1", "key2": "wrong2"}')
        result = parser.match_values(
            {"key1": "value1", "key2": "value2"}, format="json"
        )

        assert len(result.wrong_list) == 2
        assert "key1: 'wrong1'!='value1'" in result.wrong_list
        assert "key2: 'wrong2'!='value2'" in result.wrong_list
        assert (
            ", ".join(result.wrong_list)
            == "key1: 'wrong1'!='value1', key2: 'wrong2'!='value2'"
        )

        # Test with no wrong values
        result_match = parser.match_values({"key1": "wrong1"}, format="json")
        assert result_match.wrong_list == []


class TestParseHasKey:
    """Tests for Parse.has_key() method."""

    def test_has_key_json(self, parse):
        """Test has_key() with JSON format."""
        parser = parse.from_str('{"database": {"host": "localhost"}}')
        assert parser.has_key("database.host", format="json")
        assert parser.has_key("database", format="json")
        assert not parser.has_key("database.port", format="json")

    def test_has_key_all_formats(self, parse):
        """Test has_key() with all supported formats."""
        test_cases = [
            ('{"key": "value"}', "json", "key"),
            ("key: value\n", "yaml", "key"),
            ('key = "value"\n', "toml", "key"),
            ("[section]\nkey = value\n", "ini", "section.key"),
            ("KEY=value\n", "keyval", "KEY"),
        ]

        for content, fmt, path in test_cases:
            parser = parse.from_str(content)
            assert parser.has_key(path, format=fmt)


class TestParseMatchKeys:
    """Tests for Parse.match_keys() method."""

    def test_match_keys_json(self, parse):
        """Test match_keys() with JSON format."""
        parser = parse.from_str('{"database": {"host": "localhost", "port": 5432}}')
        result = parser.match_keys(
            ["database.host", "database.port", "database.missing"], format="json"
        )
        assert result.all_match is False
        assert "database.missing" in result.missing
        assert len(result.wrong) == 0

    def test_match_keys_json_all_exist(self, parse):
        """Test match_keys() with JSON format when all keys exist."""
        parser = parse.from_str('{"database": {"host": "localhost", "port": 5432}}')
        result = parser.match_keys(["database.host", "database.port"], format="json")
        assert result.all_match is True
        assert len(result.missing) == 0
        assert len(result.wrong) == 0

    def test_match_keys_yaml(self, parse):
        """Test match_keys() with YAML format."""
        parser = parse.from_str("database:\n  host: localhost\n  port: 5432\n")
        result = parser.match_keys(["database.host", "database.port"], format="yaml")
        assert result.all_match is True

    def test_match_keys_toml(self, parse):
        """Test match_keys() with TOML format."""
        parser = parse.from_str('[database]\nhost = "localhost"\nport = 5432\n')
        result = parser.match_keys(["database.host", "database.port"], format="toml")
        assert result.all_match is True

    def test_match_keys_ini(self, parse):
        """Test match_keys() with INI format."""
        parser = parse.from_str("[database]\nhost = localhost\nport = 5432\n")
        result = parser.match_keys(["database.host", "database.port"], format="ini")
        assert result.all_match is True

    def test_match_keys_keyval(self, parse):
        """Test match_keys() with keyval format."""
        parser = parse.from_str("DATABASE_HOST=localhost\nDATABASE_PORT=5432\n")
        result = parser.match_keys(
            ["DATABASE_HOST", "DATABASE_PORT", "MISSING_KEY"], format="keyval"
        )
        assert result.all_match is False
        assert "MISSING_KEY" in result.missing
        assert len(result.wrong) == 0

    def test_match_keys_empty_list(self, parse):
        """Test match_keys() with empty list."""
        parser = parse.from_str('{"key": "value"}')
        result = parser.match_keys([], format="json")
        assert result.all_match is True
        assert len(result.missing) == 0
        assert len(result.wrong) == 0

    def test_match_keys_all_missing(self, parse):
        """Test match_keys() when all keys are missing."""
        parser = parse.from_str('{"other": "value"}')
        result = parser.match_keys(["missing1", "missing2"], format="json")
        assert result.all_match is False
        assert "missing1" in result.missing
        assert "missing2" in result.missing


class TestParseGetPaths:
    """Tests for Parse.get_paths() method."""

    def test_get_paths_json(self, parse):
        """Test get_paths() with JSON format."""
        parser = parse.from_str(
            '{"host": "localhost", "database": {"host": "localhost", "port": 5432}}'
        )
        paths = parser.get_paths("localhost", format="json")
        assert "host" in paths
        assert "database.host" in paths
        assert len(paths) == 2

    def test_get_paths_yaml(self, parse):
        """Test get_paths() with YAML format."""
        parser = parse.from_str("host: localhost\ndatabase:\n  host: localhost\n")
        paths = parser.get_paths("localhost", format="yaml")
        assert "host" in paths
        assert "database.host" in paths

    def test_get_paths_not_found(self, parse):
        """Test get_paths() when value is not found."""
        parser = parse.from_str('{"key": "value"}')
        paths = parser.get_paths("missing", format="json")
        assert paths == []

    def test_get_paths_with_lists(self, parse):
        """Test get_paths() finds values in lists."""
        parser = parse.from_str('{"items": ["value1", "value2", "value1"]}')
        paths = parser.get_paths("value1", format="json")
        assert "items[0]" in paths
        assert "items[2]" in paths

    def test_get_paths_toml(self, parse):
        """Test get_paths() with TOML format."""
        parser = parse.from_str('host = "localhost"\n[database]\nhost = "localhost"\n')
        paths = parser.get_paths("localhost", format="toml")
        assert "host" in paths
        assert "database.host" in paths

    def test_get_paths_ini(self, parse):
        """Test get_paths() with INI format."""
        parser = parse.from_str(
            "[section]\nhost = localhost\n[database]\nhost = localhost\n"
        )
        paths = parser.get_paths("localhost", format="ini")
        assert "section.host" in paths
        assert "database.host" in paths

    def test_get_paths_keyval(self, parse):
        """Test get_paths() with keyval format."""
        parser = parse.from_str("HOST=localhost\nDATABASE_HOST=localhost\n")
        paths = parser.get_paths("localhost", format="keyval")
        assert "HOST" in paths
        assert "DATABASE_HOST" in paths

    def test_get_paths_empty_structure(self, parse):
        """Test get_paths() with empty structure."""
        parser = parse.from_str("{}")
        paths = parser.get_paths("value", format="json")
        assert paths == []

    def test_get_paths_nested_same_value(self, parse):
        """Test get_paths() finds same value at different nesting levels."""
        parser = parse.from_str(
            '{"level1": {"level2": {"value": "target"}, "value": "target"}, "value": "target"}'
        )
        paths = parser.get_paths("target", format="json")
        assert "value" in paths
        assert "level1.value" in paths
        assert "level1.level2.value" in paths
        assert len(paths) == 3


# ============================================================================
# Comment Handling Tests
# ============================================================================


class TestCommentHandling:
    """Tests for comment filtering across different formats."""

    def test_comments_json_no_filtering(self, parse):
        """Test that JSON doesn't filter comments (JSON has no comment support)."""
        parser = parse.from_str('{"key": "value"}\n# This is not a comment\n')
        # In JSON, # is part of the content, not a comment
        assert parser.has_line("# This is not a comment", format="json")

    def test_comments_yaml_hash(self, parse):
        """Test YAML comment filtering with #."""
        parser = parse.from_str("# Comment\nkey: value\n")
        assert parser.has_line("key: value", format="yaml")
        assert not parser.has_line("Comment", format="yaml")

    def test_comments_ini_semicolon_and_hash(self, parse):
        """Test INI comment filtering with both ; and #."""
        parser = parse.from_str("; Semicolon comment\nkey = value\n# Hash comment\n")
        assert parser.has_line("key = value", format="ini")
        assert not parser.has_line("Semicolon comment", format="ini")
        assert not parser.has_line("Hash comment", format="ini")

    def test_comments_toml_hash(self, parse):
        """Test TOML comment filtering with #."""
        parser = parse.from_str('# Comment\nkey = "value"\n')
        assert parser.has_line("key =", format="toml")
        assert not parser.has_line("Comment", format="toml")

    def test_comments_keyval_hash(self, parse):
        """Test keyval comment filtering with #."""
        parser = parse.from_str("# Comment\nKEY=value\n")
        assert parser.has_line("KEY=value", format="keyval")
        assert not parser.has_line("Comment", format="keyval")

    def test_comments_with_ignore_comments_false(self, parse):
        """Test that ignore_comments=False preserves comments in YAML/TOML."""
        yaml_content = "# Comment\nkey: value\n"
        parser = parse.from_str(yaml_content)
        # When ignore_comments=False, comments are not stripped before parsing
        # But YAML parser itself may handle comments
        assert parser.get_value("key", format="yaml", ignore_comments=False) == "value"
