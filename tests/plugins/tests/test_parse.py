"""Comprehensive tests for parse.py plugin using the parse fixture."""

import re

import pytest

# ============================================================================
# Parse Tests - Direct string-based operations
# ============================================================================


class TestParseLines:
    """Tests for Parse.lines property with __contains__ support."""

    def test_lines_string_literal_found(self, parse):
        """Test finding a string literal in lines."""
        parser = parse.from_str("line1\nline2\nline3\n")
        assert "line2" in parser.lines()
        assert "missing" not in parser.lines()

    def test_lines_string_literal_with_comments_default(self, parse):
        """Test comment filtering with default comment char."""
        parser = parse.from_str("# Comment\nkey: value\n")
        assert "key: value" in parser.lines()
        assert "Comment" not in parser.lines()

    def test_lines_regex_pattern(self, parse):
        """Test regex pattern matching."""
        parser = parse.from_str("Boot completed in 2.345s\n")
        pattern = re.compile(r"Boot completed in ([\d.]+)s")
        assert pattern in parser.lines()
        match = pattern.search(parser.content)
        assert match is not None
        assert match.group(1) == "2.345"

    def test_lines_regex_no_match(self, parse):
        """Test regex when pattern doesn't match."""
        parser = parse.from_str("Some other text\n")
        pattern = re.compile(r"Boot completed in ([\d.]+)s")
        assert pattern not in parser.lines()

    def test_lines_regex_with_flags(self, parse):
        """Test regex with flags."""
        parser = parse.from_str("UPPERCASE TEXT\n")
        pattern = re.compile(r"uppercase", flags=re.IGNORECASE)
        assert pattern in parser.lines()

    def test_lines_regex_multiline(self, parse):
        """Test regex with multiline content."""
        parser = parse.from_str("line1\nline2\n")
        pattern = re.compile(r"^line2$", flags=re.MULTILINE)
        assert pattern in parser.lines()

    def test_lines_list_unordered(self, parse):
        """Test list patterns in unordered mode."""
        parser = parse.from_str("line1\nline2\nline3\n")
        assert ["line1", "line2"] in parser.lines()
        assert [
            "line3",
            "line1",
        ] in parser.lines()  # Unordered, so order doesn't matter
        assert ["line1", "missing"] not in parser.lines()

    def test_lines_list_with_comments(self, parse):
        """Test list patterns with comment filtering."""
        parser = parse.from_str("# Comment\nline1\n# Another\nline2\n")
        assert ["line1", "line2"] in parser.lines()
        assert ["Comment", "line1"] not in parser.lines()

    def test_lines_empty_list(self, parse):
        """Test empty list pattern."""
        parser = parse.from_str("line1\nline2\n")
        assert [] in parser.lines()  # Empty list always matches

    def test_lines_single_pattern_in_list(self, parse):
        """Test single pattern in list."""
        parser = parse.from_str("line1\nline2\n")
        assert ["line1"] in parser.lines()
        assert ["missing"] not in parser.lines()

    def test_lines_invalid_pattern_type(self, parse):
        """Test that invalid pattern types raise TypeError."""
        parser = parse.from_str("line1\nline2\n")
        with pytest.raises(TypeError, match="Unsupported pattern type"):
            _ = 123 in parser.lines()  # type: ignore

    def test_lines_empty_content(self, parse):
        """Test lines() with empty content."""
        parser = parse.from_str("")
        assert "anything" not in parser.lines()
        assert [] in parser.lines()  # Empty list should match empty content
        pattern = re.compile(r".*")
        assert pattern in parser.lines()  # Regex should match empty

    def test_lines_only_comments(self, parse):
        """Test lines() with content containing only comments."""
        parser = parse.from_str("# Comment 1\n# Comment 2\n")
        assert "Comment" not in parser.lines()
        assert [] in parser.lines()  # Empty list should match

    def test_lines_explicit_comment_char(self, parse):
        """Test lines() with explicit comment_char parameter."""
        parser = parse.from_str("; Custom comment\nkey = value\n")
        # Test with explicit comment_char
        assert "key = value" in parser.lines(comment_char=";")
        assert "Custom comment" not in parser.lines(comment_char=";")

        # Test with list of comment chars
        parser2 = parse.from_str("; Comment 1\n# Comment 2\nkey = value\n")
        assert "key = value" in parser2.lines(comment_char=[";", "#"])
        assert "Comment 1" not in parser2.lines(comment_char=[";", "#"])
        assert "Comment 2" not in parser2.lines(comment_char=[";", "#"])

    def test_lines_whitespace_normalization(self, parse):
        """Test lines() normalizes whitespace correctly."""
        parser = parse.from_str("key    =    value\nkey\t=\tvalue\n")
        assert "key = value" in parser.lines()  # Multiple spaces normalized
        assert "key = value" in parser.lines()  # Tabs normalized


class TestParseLinesOrdered:
    """Tests for Parse.lines() method with ordered pattern matching."""

    def test_sorted_lines_in_order(self, parse):
        """Test finding lines in order."""
        parser = parse.from_str("line1\nline2\nline3\n")
        assert ["line1", "line2"] in parser.lines(ordered=True)
        assert ["line2", "line3"] in parser.lines(ordered=True)
        assert ["line3", "line1"] not in parser.lines(ordered=True)  # Wrong order

    def test_sorted_lines_with_comments(self, parse):
        """Test sorted_lines filters comments."""
        parser = parse.from_str("# Comment\nline1\n# Another\nline2\n")
        assert ["line1", "line2"] in parser.lines(ordered=True)
        assert ["Comment", "line1"] not in parser.lines(ordered=True)

    def test_sorted_lines_empty_list(self, parse):
        """Test sorted_lines with empty patterns list."""
        parser = parse.from_str("line1\nline2\n")
        assert [] in parser.lines(ordered=True)  # Empty list always matches

    def test_sorted_lines_single_pattern(self, parse):
        """Test sorted_lines with single pattern."""
        parser = parse.from_str("line1\nline2\n")
        assert ["line1"] in parser.lines(ordered=True)
        assert ["missing"] not in parser.lines(ordered=True)

    def test_sorted_lines_ordered_with_gaps(self, parse):
        """Test ordered patterns with gaps between them."""
        parser = parse.from_str("line1\nother_line\nline2\n")
        assert ["line1", "line2"] in parser.lines(ordered=True)  # Should work with gaps
        assert ["line2", "line1"] not in parser.lines(ordered=True)  # Wrong order


class TestParseParse:
    """Tests for Parse.parse() method."""

    def test_parse_json(self, parse):
        """Test parse() with JSON format."""
        parser = parse.from_str('{"database": {"host": "localhost", "port": 5432}}')
        config = parser.parse(format="json")
        assert config["database"]["host"] == "localhost"
        assert config["database"]["port"] == 5432
        assert "missing" not in config["database"]

    def test_parse_json_direct_access(self, parse):
        """Test parse() allows direct dictionary access."""
        parser = parse.from_str('{"key": "value", "nested": {"key": "nested_value"}}')
        config = parser.parse(format="json")
        assert config["key"] == "value"
        assert config["nested"]["key"] == "nested_value"
        assert "key" in config
        assert "missing" not in config

    def test_parse_yaml(self, parse):
        """Test parse() with YAML format."""
        parser = parse.from_str("database:\n  host: localhost\n  port: 5432\n")
        config = parser.parse(format="yaml")
        assert config["database"]["host"] == "localhost"
        assert config["database"]["port"] == 5432

    def test_parse_toml(self, parse):
        """Test parse() with TOML format."""
        parser = parse.from_str('[database]\nhost = "localhost"\nport = 5432\n')
        config = parser.parse(format="toml")
        assert config["database"]["host"] == "localhost"
        assert config["database"]["port"] == 5432

    def test_parse_ini(self, parse):
        """Test parse() with INI format."""
        parser = parse.from_str("[database]\nhost = localhost\nport = 5432\n")
        config = parser.parse(format="ini")
        assert config["database"]["host"] == "localhost"
        assert config["database"]["port"] == "5432"

    def test_parse_keyval(self, parse):
        """Test parse() with keyval format."""
        parser = parse.from_str("DATABASE_HOST=localhost\nDATABASE_PORT=5432\n")
        config = parser.parse(format="keyval")
        assert config["DATABASE_HOST"] == "localhost"
        assert config["DATABASE_PORT"] == "5432"
        assert "MISSING_KEY" not in config

    def test_parse_with_lists(self, parse):
        """Test parse() with lists in data."""
        parser = parse.from_str('{"items": ["item1", "item2"], "count": 2}')
        config = parser.parse(format="json")
        assert config["items"] == ["item1", "item2"]
        assert "item1" in config["items"]
        assert "item3" not in config["items"]
        assert config["count"] == 2

    def test_parse_invalid_format(self, parse):
        """Test parse() raises error for invalid format."""
        parser = parse.from_str("some content")
        with pytest.raises(ValueError, match="Unsupported format"):
            parser.parse(format="invalid")

    def test_parse_ignore_comments(self, parse):
        """Test parse() with ignore_comments parameter."""
        parser = parse.from_str("# Comment\nkey: value\n")
        config = parser.parse(format="yaml", ignore_comments=True)
        assert config["key"] == "value"

    def test_parse_empty_json(self, parse):
        """Test parse() with empty JSON."""
        parser = parse.from_str("{}")
        config = parser.parse(format="json")
        assert config == {}

    def test_parse_empty_list(self, parse):
        """Test parse() with empty list."""
        parser = parse.from_str("[]")
        config = parser.parse(format="json")
        assert config == []

    def test_parse_deeply_nested(self, parse):
        """Test parse() with deeply nested structures."""
        parser = parse.from_str(
            '{"level1": {"level2": {"level3": {"level4": "value"}}}}'
        )
        config = parser.parse(format="json")
        assert config["level1"]["level2"]["level3"]["level4"] == "value"

    def test_parse_ignore_comments_false_toml(self, parse):
        """Test parse() with ignore_comments=False for TOML."""
        parser = parse.from_str('# Comment\nkey = "value"\n')
        config = parser.parse(format="toml", ignore_comments=False)
        assert config["key"] == "value"

    def test_parse_ignore_comments_false_ini(self, parse):
        """Test parse() with ignore_comments=False for INI."""
        parser = parse.from_str("; Comment\n[section]\nkey = value\n")
        config = parser.parse(format="ini", ignore_comments=False)
        assert config["section"]["key"] == "value"

    def test_parse_ignore_comments_false_keyval(self, parse):
        """Test parse() with ignore_comments=False for keyval."""
        parser = parse.from_str("# Comment\nKEY=value\n")
        config = parser.parse(format="keyval", ignore_comments=False)
        assert config["KEY"] == "value"

    def test_parse_empty_string_json(self, parse):
        """Test parse() with empty string for JSON."""
        parser = parse.from_str("")
        with pytest.raises(Exception):  # json.JSONDecodeError
            parser.parse(format="json")

    def test_parse_malformed_yaml(self, parse):
        """Test parse() with malformed YAML."""
        parser = parse.from_str("key: value\n  invalid_indent: value\n")
        with pytest.raises(Exception):  # yaml.YAMLError
            parser.parse(format="yaml")

    def test_parse_malformed_toml(self, parse):
        """Test parse() with malformed TOML."""
        parser = parse.from_str('key = "unclosed string\n')
        with pytest.raises(Exception):  # tomllib.TOMLDecodeError
            parser.parse(format="toml")

    def test_parse_malformed_ini(self, parse):
        """Test parse() with malformed INI."""
        parser = parse.from_str("[section\nkey = value\n")  # Missing closing bracket
        with pytest.raises(Exception):  # configparser.Error
            parser.parse(format="ini")


# ============================================================================
# Comment Handling Tests
# ============================================================================


class TestCommentHandling:
    """Tests for comment filtering across different formats."""

    def test_comments_json_no_filtering(self, parse):
        """Test that JSON doesn't filter comments (JSON has no comment support)."""
        parser = parse.from_str('{"key": "value"}\n# This is not a comment\n')
        # In JSON, # is part of the content, not a comment
        # Need to specify format="json" to get no comment filtering
        assert "# This is not a comment" in parser.lines(format="json")

    def test_comments_yaml_hash(self, parse):
        """Test YAML comment filtering with #."""
        parser = parse.from_str("# Comment\nkey: value\n")
        assert "key: value" in parser.lines()
        assert "Comment" not in parser.lines()

    def test_comments_ini_semicolon_and_hash(self, parse):
        """Test INI comment filtering with both ; and #."""
        parser = parse.from_str("; Semicolon comment\nkey = value\n# Hash comment\n")
        # Need to specify format="ini" to get both ; and # comment filtering
        assert "key = value" in parser.lines(format="ini")
        assert "Semicolon comment" not in parser.lines(format="ini")
        assert "Hash comment" not in parser.lines(format="ini")

    def test_comments_toml_hash(self, parse):
        """Test TOML comment filtering with #."""
        parser = parse.from_str('# Comment\nkey = "value"\n')
        assert "key =" in parser.lines()
        assert "Comment" not in parser.lines()

    def test_comments_keyval_hash(self, parse):
        """Test keyval comment filtering with #."""
        parser = parse.from_str("# Comment\nKEY=value\n")
        assert "KEY=value" in parser.lines()
        assert "Comment" not in parser.lines()

    def test_comments_with_ignore_comments_false(self, parse):
        """Test that ignore_comments=False preserves comments in YAML/TOML."""
        yaml_content = "# Comment\nkey: value\n"
        parser = parse.from_str(yaml_content)
        # When ignore_comments=False, comments are not stripped before parsing
        # But YAML parser itself may handle comments
        config = parser.parse(format="yaml", ignore_comments=False)
        assert config["key"] == "value"

    def test_lines_tuple_pattern_not_supported(self, parse):
        """Test that tuple patterns are not supported (only list)."""
        parser = parse.from_str("line1\nline2\nline3\n")
        # Tuple should raise TypeError since only list is supported
        with pytest.raises(TypeError, match="Unsupported pattern type"):
            _ = ("line1", "line2") in parser.lines()  # type: ignore
