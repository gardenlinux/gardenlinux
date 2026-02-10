"""Comprehensive tests for parse_file.py plugin."""

import re

import pytest
from plugins.parse_file import ParseFile

# ============================================================================
# ParseFile Tests - File-based operations
# ============================================================================


class TestParseFileLines:
    """Tests for ParseFile.lines() method with __contains__ support."""

    def test_lines_string_literal_found(self, parse_file: ParseFile, tmp_path):
        """Test finding a string literal in file lines."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("This is a test line\nAnother line\nMulti word line\n")

        lines = parse_file.lines(test_file)
        assert "test line" in lines
        assert "Another" in lines
        assert "missing" not in lines

    def test_lines_string_literal_with_comments_json(
        self, parse_file: ParseFile, tmp_path
    ):
        """Test that JSON format doesn't filter comments (JSON has no comments)."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}\n# This is not a comment in JSON\n')

        lines = parse_file.lines(test_file, format="json")
        # JSON doesn't support comments, so # should be treated as part of content
        assert "# This is not a comment" in lines

    def test_lines_string_literal_with_comments_yaml(
        self, parse_file: ParseFile, tmp_path
    ):
        """Test comment filtering for YAML format."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("# Comment line\nkey: value\n# Another comment\n")

        lines = parse_file.lines(test_file)
        assert "key: value" in lines
        assert "Comment line" not in lines

    def test_lines_regex_pattern(self, parse_file: ParseFile, tmp_path):
        """Test regex pattern matching in file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Boot completed in 2.345s\n")

        lines = parse_file.lines(test_file)
        pattern = re.compile(r"Boot completed in ([\d.]+)s")
        assert pattern in lines
        match = pattern.search(test_file.read_text())
        assert match is not None
        assert match.group(1) == "2.345"

    def test_lines_regex_no_match(self, parse_file: ParseFile, tmp_path):
        """Test regex when pattern doesn't match."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Some other text\n")

        lines = parse_file.lines(test_file)
        pattern = re.compile(r"Boot completed in ([\d.]+)s")
        assert pattern not in lines

    def test_lines_list_unordered(self, parse_file: ParseFile, tmp_path):
        """Test list patterns in unordered mode."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3\n")

        lines = parse_file.lines(test_file)
        assert ["line1", "line2"] in lines
        assert ["line3", "line1"] in lines  # Unordered, so order doesn't matter
        assert ["line1", "missing"] not in lines

    def test_lines_format_auto_detection(self, parse_file: ParseFile, tmp_path):
        """Test automatic format detection from file extension."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("# Comment\nkey: value\n")

        lines = parse_file.lines(test_file)
        # Should auto-detect YAML and filter comments
        assert "key: value" in lines
        assert "Comment" not in lines

    def test_lines_ignore_missing_true(self, parse_file: ParseFile, tmp_path):
        """Test ignore_missing=True returns None for missing file."""
        missing_file = tmp_path / "missing.txt"
        lines = parse_file.lines(missing_file, ignore_missing=True)
        assert lines is None

    def test_lines_ignore_missing_false(self, parse_file: ParseFile, tmp_path):
        """Test ignore_missing=False raises FileNotFoundError for missing file."""
        missing_file = tmp_path / "missing.txt"
        with pytest.raises(FileNotFoundError, match="File not found"):
            parse_file.lines(missing_file, ignore_missing=False)

    def test_lines_empty_content(self, parse_file: ParseFile, tmp_path):
        """Test lines() with empty file content."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("")
        lines = parse_file.lines(test_file)
        assert "anything" not in lines
        assert [] in lines  # Empty list should match empty content
        pattern = re.compile(r".*")
        assert pattern in lines  # Regex should match empty

    def test_lines_only_comments(self, parse_file: ParseFile, tmp_path):
        """Test lines() with file containing only comments."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("# Comment 1\n# Comment 2\n")
        lines = parse_file.lines(test_file)
        assert "Comment" not in lines
        assert [] in lines  # Empty list should match

    def test_lines_explicit_comment_char(self, parse_file: ParseFile, tmp_path):
        """Test lines() with explicit comment_char parameter."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("; Custom comment\nkey = value\n")
        lines = parse_file.lines(test_file, comment_char=";")
        assert "key = value" in lines
        assert "Custom comment" not in lines

        # Test with list of comment chars
        test_file2 = tmp_path / "test2.txt"
        test_file2.write_text("; Comment 1\n# Comment 2\nkey = value\n")
        lines2 = parse_file.lines(test_file2, comment_char=[";", "#"])
        assert "key = value" in lines2
        assert "Comment 1" not in lines2
        assert "Comment 2" not in lines2

    def test_lines_whitespace_normalization(self, parse_file: ParseFile, tmp_path):
        """Test lines() normalizes whitespace correctly."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("key    =    value\nkey\t=\tvalue\n")
        lines = parse_file.lines(test_file)
        assert "key = value" in lines  # Multiple spaces normalized
        assert "key = value" in lines  # Tabs normalized


class TestParseFileLinesOrdered:
    """Tests for ParseFile.lines() method with ordered pattern matching."""

    def test_sorted_lines_in_order(self, parse_file: ParseFile, tmp_path):
        """Test finding lines in order."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nline2\nline3\n")

        sorted_lines = parse_file.lines(test_file, ordered=True)
        assert ["line1", "line2"] in sorted_lines
        assert ["line2", "line3"] in sorted_lines
        assert ["line3", "line1"] not in sorted_lines  # Wrong order

    def test_sorted_lines_with_comments(self, parse_file: ParseFile, tmp_path):
        """Test sorted_lines filters comments."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("# Comment 1\nline1\n# Comment 2\nline2\n")

        sorted_lines = parse_file.lines(test_file, ordered=True)
        assert ["line1", "line2"] in sorted_lines
        assert ["Comment 1", "line1"] not in sorted_lines

    def test_sorted_lines_ignore_missing(self, parse_file: ParseFile, tmp_path):
        """Test ignore_missing parameter for sorted_lines()."""
        missing_file = tmp_path / "missing.txt"
        sorted_lines = parse_file.lines(missing_file, ordered=True, ignore_missing=True)
        assert sorted_lines is None

        with pytest.raises(FileNotFoundError):
            parse_file.lines(missing_file, ordered=True, ignore_missing=False)

    def test_sorted_lines_ordered_with_gaps(self, parse_file: ParseFile, tmp_path):
        """Test ordered patterns with gaps between them."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("line1\nother_line\nline2\n")
        sorted_lines = parse_file.lines(test_file, ordered=True)
        assert ["line1", "line2"] in sorted_lines  # Should work with gaps
        assert ["line2", "line1"] not in sorted_lines  # Wrong order


class TestParseFileParse:
    """Tests for ParseFile.parse() method."""

    def test_parse_json(self, parse_file: ParseFile, tmp_path):
        """Test parse() with JSON format."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"database": {"host": "localhost", "port": 5432}}')

        config = parse_file.parse(test_file, format="json")
        assert config["database"]["host"] == "localhost"
        assert config["database"]["port"] == 5432
        assert "missing" not in config["database"]

    def test_parse_json_direct_access(self, parse_file: ParseFile, tmp_path):
        """Test parse() allows direct dictionary access."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value", "nested": {"key": "nested_value"}}')

        config = parse_file.parse(test_file, format="json")
        assert config["key"] == "value"
        assert config["nested"]["key"] == "nested_value"
        assert "key" in config
        assert "missing" not in config

    def test_parse_yaml(self, parse_file: ParseFile, tmp_path):
        """Test parse() with YAML format."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("database:\n  host: localhost\n  port: 5432\n")

        config = parse_file.parse(test_file, format="yaml")
        assert config["database"]["host"] == "localhost"
        assert config["database"]["port"] == 5432

    def test_parse_toml(self, parse_file: ParseFile, tmp_path):
        """Test parse() with TOML format."""
        test_file = tmp_path / "test.toml"
        test_file.write_text('[database]\nhost = "localhost"\nport = 5432\n')

        config = parse_file.parse(test_file, format="toml")
        assert config["database"]["host"] == "localhost"
        assert config["database"]["port"] == 5432

    def test_parse_ini(self, parse_file: ParseFile, tmp_path):
        """Test parse() with INI format."""
        test_file = tmp_path / "test.ini"
        test_file.write_text("[database]\nhost = localhost\nport = 5432\n")

        config = parse_file.parse(test_file, format="ini")
        assert config["database"]["host"] == "localhost"
        assert config["database"]["port"] == "5432"

    def test_parse_keyval(self, parse_file: ParseFile, tmp_path):
        """Test parse() with keyval format."""
        test_file = tmp_path / "test.env"
        test_file.write_text("DATABASE_HOST=localhost\nDATABASE_PORT=5432\n")

        config = parse_file.parse(test_file, format="keyval")
        assert config["DATABASE_HOST"] == "localhost"
        assert config["DATABASE_PORT"] == "5432"
        assert "MISSING_KEY" not in config

    def test_parse_format_auto_detection(self, parse_file: ParseFile, tmp_path):
        """Test parse() with format auto-detection."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')

        config = parse_file.parse(test_file)
        assert config["key"] == "value"

    def test_parse_with_lists(self, parse_file: ParseFile, tmp_path):
        """Test parse() with lists in data."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"items": ["item1", "item2"], "count": 2}')

        config = parse_file.parse(test_file, format="json")
        assert config["items"] == ["item1", "item2"]
        assert "item1" in config["items"]
        assert "item3" not in config["items"]
        assert config["count"] == 2

    def test_parse_ignore_missing(self, parse_file: ParseFile, tmp_path):
        """Test ignore_missing parameter for parse()."""
        missing_file = tmp_path / "missing.json"
        config = parse_file.parse(missing_file, format="json", ignore_missing=True)
        assert config is None

        with pytest.raises(FileNotFoundError):
            parse_file.parse(missing_file, format="json", ignore_missing=False)

    def test_parse_invalid_format(self, parse_file: ParseFile, tmp_path):
        """Test parse() raises error for invalid format."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("some content")
        with pytest.raises(ValueError, match="Unsupported format"):
            parse_file.parse(test_file, format="invalid")

    def test_parse_empty_json(self, parse_file: ParseFile, tmp_path):
        """Test parse() with empty JSON."""
        test_file = tmp_path / "test.json"
        test_file.write_text("{}")
        config = parse_file.parse(test_file, format="json")
        assert config == {}

    def test_parse_empty_list(self, parse_file: ParseFile, tmp_path):
        """Test parse() with empty list."""
        test_file = tmp_path / "test.json"
        test_file.write_text("[]")
        config = parse_file.parse(test_file, format="json")
        assert config == []

    def test_parse_deeply_nested(self, parse_file: ParseFile, tmp_path):
        """Test parse() with deeply nested structures."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"level1": {"level2": {"level3": {"level4": "value"}}}}')
        config = parse_file.parse(test_file, format="json")
        assert config["level1"]["level2"]["level3"]["level4"] == "value"

    def test_parse_ignore_comments_false_toml(self, parse_file: ParseFile, tmp_path):
        """Test parse() with ignore_comments=False for TOML."""
        test_file = tmp_path / "test.toml"
        test_file.write_text('# Comment\nkey = "value"\n')
        config = parse_file.parse(test_file, format="toml", ignore_comments=False)
        assert config["key"] == "value"

    def test_parse_ignore_comments_false_ini(self, parse_file: ParseFile, tmp_path):
        """Test parse() with ignore_comments=False for INI."""
        test_file = tmp_path / "test.ini"
        test_file.write_text("; Comment\n[section]\nkey = value\n")
        config = parse_file.parse(test_file, format="ini", ignore_comments=False)
        assert config["section"]["key"] == "value"

    def test_parse_ignore_comments_false_keyval(self, parse_file: ParseFile, tmp_path):
        """Test parse() with ignore_comments=False for keyval."""
        test_file = tmp_path / "test.env"
        test_file.write_text("# Comment\nKEY=value\n")
        config = parse_file.parse(test_file, format="keyval", ignore_comments=False)
        assert config["KEY"] == "value"

    def test_parse_empty_string_json(self, parse_file: ParseFile, tmp_path):
        """Test parse() with empty string for JSON."""
        test_file = tmp_path / "test.json"
        test_file.write_text("")
        with pytest.raises(Exception):  # json.JSONDecodeError
            parse_file.parse(test_file, format="json")

    def test_parse_malformed_yaml(self, parse_file: ParseFile, tmp_path):
        """Test parse() with malformed YAML."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("key: value\n  invalid_indent: value\n")
        with pytest.raises(Exception):  # yaml.YAMLError
            parse_file.parse(test_file, format="yaml")

    def test_parse_malformed_toml(self, parse_file: ParseFile, tmp_path):
        """Test parse() with malformed TOML."""
        test_file = tmp_path / "test.toml"
        test_file.write_text('key = "unclosed string\n')
        with pytest.raises(Exception):  # tomllib.TOMLDecodeError
            parse_file.parse(test_file, format="toml")

    def test_parse_malformed_ini(self, parse_file: ParseFile, tmp_path):
        """Test parse() with malformed INI."""
        test_file = tmp_path / "test.ini"
        test_file.write_text("[section\nkey = value\n")  # Missing closing bracket
        with pytest.raises(Exception):  # configparser.Error
            parse_file.parse(test_file, format="ini")


# ============================================================================
# Format Auto-detection Tests
# ============================================================================


class TestFormatAutoDetection:
    """Tests for format auto-detection from file extensions."""

    def test_auto_detect_json(self, parse_file: ParseFile, tmp_path):
        """Test auto-detection of JSON format."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')
        config = parse_file.parse(test_file)
        assert config["key"] == "value"

    def test_auto_detect_yaml(self, parse_file: ParseFile, tmp_path):
        """Test auto-detection of YAML format."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("key: value\n")
        config = parse_file.parse(test_file)
        assert config["key"] == "value"

        test_file = tmp_path / "test.yml"
        test_file.write_text("key: value\n")
        config = parse_file.parse(test_file)
        assert config["key"] == "value"

    def test_auto_detect_toml(self, parse_file: ParseFile, tmp_path):
        """Test auto-detection of TOML format."""
        test_file = tmp_path / "test.toml"
        test_file.write_text('key = "value"\n')
        config = parse_file.parse(test_file)
        assert config["key"] == "value"

    def test_auto_detect_ini(self, parse_file: ParseFile, tmp_path):
        """Test auto-detection of INI format."""
        test_file = tmp_path / "test.ini"
        test_file.write_text("[section]\nkey = value\n")
        config = parse_file.parse(test_file)
        assert config["section"]["key"] == "value"

        test_file = tmp_path / "test.cfg"
        test_file.write_text("[section]\nkey = value\n")
        config = parse_file.parse(test_file)
        assert config["section"]["key"] == "value"

    def test_auto_detect_keyval(self, parse_file: ParseFile, tmp_path):
        """Test auto-detection of keyval format."""
        test_file = tmp_path / "test.conf"
        test_file.write_text("key = value\n")
        config = parse_file.parse(test_file)
        assert config["key"] == "value"

        test_file = tmp_path / "test.env"
        test_file.write_text("KEY=value\n")
        config = parse_file.parse(test_file)
        assert config["KEY"] == "value"

    def test_auto_detect_no_extension(self, parse_file: ParseFile, tmp_path):
        """Test error when format cannot be auto-detected."""
        test_file = tmp_path / "test"
        test_file.write_text('{"key": "value"}')
        with pytest.raises(ValueError, match="Cannot auto-detect format"):
            parse_file.parse(test_file)


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
        lines = parse_file.lines(test_file, format="json")
        assert "# This is not a comment" in lines

    def test_comments_yaml_hash(self, parse_file: ParseFile, tmp_path):
        """Test YAML comment filtering with #."""
        test_file = tmp_path / "test.yaml"
        test_file.write_text("# Comment\nkey: value\n")
        lines = parse_file.lines(test_file, format="yaml")
        assert "key: value" in lines
        assert "Comment" not in lines

    def test_comments_ini_semicolon_and_hash(self, parse_file: ParseFile, tmp_path):
        """Test INI comment filtering with both ; and #."""
        test_file = tmp_path / "test.ini"
        test_file.write_text("; Semicolon comment\nkey = value\n# Hash comment\n")
        lines = parse_file.lines(test_file, format="ini")
        assert "key = value" in lines
        assert "Semicolon comment" not in lines
        assert "Hash comment" not in lines

    def test_comments_toml_hash(self, parse_file: ParseFile, tmp_path):
        """Test TOML comment filtering with #."""
        test_file = tmp_path / "test.toml"
        test_file.write_text('# Comment\nkey = "value"\n')
        lines = parse_file.lines(test_file, format="toml")
        assert "key =" in lines
        assert "Comment" not in lines

    def test_comments_keyval_hash(self, parse_file: ParseFile, tmp_path):
        """Test keyval comment filtering with #."""
        test_file = tmp_path / "test.env"
        test_file.write_text("# Comment\nKEY=value\n")
        lines = parse_file.lines(test_file, format="keyval")
        assert "KEY=value" in lines
        assert "Comment" not in lines


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_missing_file_error_message(self, parse_file: ParseFile, tmp_path):
        """Test that missing file error message is helpful."""
        missing_file = tmp_path / "missing.txt"
        with pytest.raises(FileNotFoundError) as exc_info:
            parse_file.lines(missing_file, ignore_missing=False)
        assert "File not found" in str(exc_info.value)
        assert "missing.txt" in str(exc_info.value)

    def test_invalid_json(self, parse_file: ParseFile, tmp_path):
        """Test handling of invalid JSON."""
        test_file = tmp_path / "test.json"
        test_file.write_text("{invalid json}")
        with pytest.raises(Exception):  # json.JSONDecodeError
            parse_file.parse(test_file, format="json")

    def test_invalid_path_in_parse(self, parse_file: ParseFile, tmp_path):
        """Test parse() with non-existent keys."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"key": "value"}')
        config = parse_file.parse(test_file, format="json")
        # With parse(), we can check directly using 'in' operator
        assert "nonexistent" not in config
        # Accessing nested non-existent path raises KeyError (standard Python behavior)
        with pytest.raises(KeyError):
            _ = config["nonexistent"]["path"]
