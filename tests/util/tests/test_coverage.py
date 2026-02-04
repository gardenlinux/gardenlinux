#!/usr/bin/env python3
"""
Unit tests for tests/util/coverage.py

Tests static coverage analysis functionality including:
- Configuration management
- Path matching and normalization
- YAML loading and parsing
- Setting ID extraction from various sources
- Duplicate detection
- Report generation
- Test file searching
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Import the module under test - must import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from util import coverage as cov_module

# Alias for easier reference in tests
coverage = cov_module


class TestConfig:
    """Tests for Config dataclass."""

    def test_config_is_immutable(self):
        """Config should be frozen and immutable."""
        with pytest.raises(AttributeError):
            coverage.CONFIG.setting_id_prefix = "NEW-PREFIX"  # type: ignore[misc]

    def test_config_default_values(self):
        """Config should have correct default values."""
        assert coverage.CONFIG.setting_id_prefix == "GL-SET-"
        assert coverage.CONFIG.setting_id_pattern == r"GL-SET-[a-zA-Z0-9_-]+"
        assert coverage.CONFIG.test_file_pattern == "test_*.py"
        assert coverage.CONFIG.setting_ids_yaml == "setting_ids.yaml"
        assert coverage.CONFIG.report_schema_version == "1.0"
        assert coverage.CONFIG.include_types == ("file.include", "initrd.include")

    def test_config_instance_creation(self):
        """Should be able to create custom Config instances."""
        custom_config = coverage.Config(
            setting_id_prefix="TEST-",
            setting_id_pattern=r"TEST-[0-9]+",
        )
        assert custom_config.setting_id_prefix == "TEST-"
        assert custom_config.setting_id_pattern == r"TEST-[0-9]+"


class TestPathMatcher:
    """Tests for PathMatcher class."""

    def test_normalize_removes_quotes_and_slashes(self):
        """normalize should strip quotes and slashes."""
        assert coverage.PathMatcher.normalize('"/etc/config"') == "etc/config"
        assert coverage.PathMatcher.normalize("'/path/to/file'") == "path/to/file"
        assert coverage.PathMatcher.normalize("/etc/config/") == "etc/config"
        assert coverage.PathMatcher.normalize("etc/config") == "etc/config"

    def test_matches_with_exact_paths(self):
        """matches should recognize exact path matches."""
        assert coverage.PathMatcher.matches("/etc/config", "/etc/config")
        assert coverage.PathMatcher.matches("etc/config", "etc/config")

    def test_matches_with_leading_slash_variants(self):
        """matches should handle paths with/without leading slash."""
        assert coverage.PathMatcher.matches("/etc/config", "etc/config")
        assert coverage.PathMatcher.matches("etc/config", "/etc/config")

    def test_matches_with_quotes(self):
        """matches should handle quoted paths."""
        assert coverage.PathMatcher.matches('"/etc/config"', "/etc/config")
        assert coverage.PathMatcher.matches("/etc/config", '"etc/config"')

    def test_find_in_list_with_exact_match(self):
        """find_in_list should find exact path matches."""
        file_list = [
            {"file": "/etc/config", "ids": ["GL-SET-001", "GL-SET-002"]},
            {"file": "/etc/other", "ids": ["GL-SET-003"]},
        ]
        result = coverage.PathMatcher.find_in_list(file_list, "/etc/config")
        assert result == ["GL-SET-001", "GL-SET-002"]

    def test_find_in_list_with_normalized_match(self):
        """find_in_list should match normalized paths."""
        file_list = [
            {"file": '"/etc/config"', "ids": ["GL-SET-001"]},
        ]
        result = coverage.PathMatcher.find_in_list(file_list, "etc/config")
        assert result == ["GL-SET-001"]

    def test_find_in_list_returns_none_for_no_match(self):
        """find_in_list should return None when no match found."""
        file_list = [{"file": "/etc/config", "ids": ["GL-SET-001"]}]
        result = coverage.PathMatcher.find_in_list(file_list, "/nonexistent")
        assert result is None

    def test_find_in_list_handles_invalid_input(self):
        """find_in_list should handle invalid input gracefully."""
        assert coverage.PathMatcher.find_in_list(None, "/etc/config") is None  # type: ignore[arg-type]
        assert coverage.PathMatcher.find_in_list("not a list", "/etc/config") is None  # type: ignore[arg-type]
        assert (
            coverage.PathMatcher.find_in_list([{"not_file": "value"}], "/etc/config")
            is None
        )

    def test_find_in_dict_with_exact_match(self):
        """find_in_dict should find exact key matches."""
        mappings = {
            "/etc/config": ["GL-SET-001", "GL-SET-002"],
            "/etc/other": ["GL-SET-003"],
        }
        result = coverage.PathMatcher.find_in_dict(mappings, "/etc/config")
        assert result == ["GL-SET-001", "GL-SET-002"]

    def test_find_in_dict_with_variant_match(self):
        """find_in_dict should match path variants."""
        mappings = {"/etc/config": ["GL-SET-001"]}
        result = coverage.PathMatcher.find_in_dict(mappings, "etc/config")
        assert result == ["GL-SET-001"]

    def test_find_in_dict_returns_none_for_no_match(self):
        """find_in_dict should return None when no match found."""
        mappings = {"/etc/config": ["GL-SET-001"]}
        result = coverage.PathMatcher.find_in_dict(mappings, "/nonexistent")
        assert result is None

    def test_find_in_dict_handles_invalid_input(self):
        """find_in_dict should handle invalid input gracefully."""
        assert coverage.PathMatcher.find_in_dict(None, "/etc/config") is None  # type: ignore[arg-type]
        assert coverage.PathMatcher.find_in_dict("not a dict", "/etc/config") is None  # type: ignore[arg-type]


class TestSettingIDExtraction:
    """Tests for setting ID extraction functions."""

    def test_extract_setting_ids_from_yaml_mapping_with_string(self):
        """Should extract setting ID from string value."""
        mapping = "GL-SET-001"
        result = coverage.extract_setting_ids_from_yaml_mapping(mapping)
        assert result == ["GL-SET-001"]

    def test_extract_setting_ids_from_yaml_mapping_with_non_setting_id_string(self):
        """Should not extract non-setting-id strings."""
        mapping = "some-other-value"
        result = coverage.extract_setting_ids_from_yaml_mapping(mapping)
        assert result == []

    def test_extract_setting_ids_from_yaml_mapping_with_dict(self):
        """Should recursively extract setting IDs from dict."""
        mapping = {
            "key1": "GL-SET-001",
            "key2": {"nested": "GL-SET-002"},
        }
        result = coverage.extract_setting_ids_from_yaml_mapping(mapping)
        assert "GL-SET-001" in result
        assert "GL-SET-002" in result

    def test_extract_setting_ids_from_yaml_mapping_with_list(self):
        """Should extract setting IDs from list."""
        mapping = ["GL-SET-001", "GL-SET-002", "other-value"]
        result = coverage.extract_setting_ids_from_yaml_mapping(mapping)
        assert "GL-SET-001" in result
        assert "GL-SET-002" in result
        assert "other-value" not in result

    def test_extract_setting_ids_from_yaml_mapping_with_nested_structure(self):
        """Should handle deeply nested structures."""
        mapping = {
            "level1": {
                "level2": [
                    {"level3": "GL-SET-001"},
                    "GL-SET-002",
                ]
            }
        }
        result = coverage.extract_setting_ids_from_yaml_mapping(mapping)
        assert "GL-SET-001" in result
        assert "GL-SET-002" in result

    def test_extract_setting_ids_from_yaml_mapping_with_empty_input(self):
        """Should handle empty inputs."""
        assert coverage.extract_setting_ids_from_yaml_mapping({}) == []
        assert coverage.extract_setting_ids_from_yaml_mapping([]) == []
        assert coverage.extract_setting_ids_from_yaml_mapping("") == []

    @patch("pathlib.Path.relative_to")
    @patch("pathlib.Path.read_text")
    def test_extract_setting_ids_from_include_file_with_new_structure(
        self, mock_read_text, mock_relative_to
    ):
        """Should extract IDs from file.include using new list structure."""
        mock_relative_to.return_value = Path("file.include/etc/config")

        setting_ids_mapping = {
            "file": {
                "include": [
                    {"file": "/etc/config", "ids": ["GL-SET-001", "GL-SET-002"]},
                ]
            }
        }

        config_file = Path("/feature/file.include/etc/config")
        feature_dir = Path("/feature")

        result = coverage.extract_setting_ids_from_include_file(
            config_file, feature_dir, setting_ids_mapping, "file.include"
        )

        assert result == ["GL-SET-001", "GL-SET-002"]

    @patch("pathlib.Path.relative_to")
    def test_extract_setting_ids_from_include_file_with_old_structure(
        self, mock_relative_to
    ):
        """Should extract IDs from file.include using old dict structure."""
        mock_relative_to.return_value = Path("file.include/etc/config")

        setting_ids_mapping = {
            "file.include": {
                "/etc/config": ["GL-SET-001", "GL-SET-002"],
            }
        }

        config_file = Path("/feature/file.include/etc/config")
        feature_dir = Path("/feature")

        result = coverage.extract_setting_ids_from_include_file(
            config_file, feature_dir, setting_ids_mapping, "file.include"
        )

        assert result == ["GL-SET-001", "GL-SET-002"]

    @patch("pathlib.Path.relative_to")
    def test_extract_setting_ids_from_include_file_with_initrd_include(
        self, mock_relative_to
    ):
        """Should extract IDs from initrd.include files."""
        mock_relative_to.return_value = Path("initrd.include/etc/config")

        setting_ids_mapping = {
            "initrd": {
                "include": [
                    {"file": "/etc/config", "ids": ["GL-SET-003"]},
                ]
            }
        }

        config_file = Path("/feature/initrd.include/etc/config")
        feature_dir = Path("/feature")

        result = coverage.extract_setting_ids_from_include_file(
            config_file, feature_dir, setting_ids_mapping, "initrd.include"
        )

        assert result == ["GL-SET-003"]

    @patch("pathlib.Path.relative_to")
    def test_extract_setting_ids_from_include_file_no_mapping(self, mock_relative_to):
        """Should return empty list when no mapping found."""
        mock_relative_to.return_value = Path("file.include/etc/config")

        setting_ids_mapping = {}

        config_file = Path("/feature/file.include/etc/config")
        feature_dir = Path("/feature")

        result = coverage.extract_setting_ids_from_include_file(
            config_file, feature_dir, setting_ids_mapping, "file.include"
        )

        assert result == []

    @patch("pathlib.Path.relative_to")
    def test_extract_setting_ids_from_include_file_not_include_dir(
        self, mock_relative_to
    ):
        """Should return empty list for files not in include directories."""
        mock_relative_to.return_value = Path("exec.config")

        setting_ids_mapping = {"file": {"include": []}}

        config_file = Path("/feature/exec.config")
        feature_dir = Path("/feature")

        result = coverage.extract_setting_ids_from_include_file(
            config_file, feature_dir, setting_ids_mapping, "file.include"
        )

        assert result == []


class TestFeatureProcessing:
    """Tests for feature processing functions."""

    def test_load_feature_excludes_with_valid_file(self):
        """Should load excluded features from file."""
        exclude_content = """# Comment line
feature1
feature2
# Another comment

feature3
"""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value=exclude_content):
                result = coverage.load_feature_excludes(Path("/repo"))

        assert result == {"feature1", "feature2", "feature3"}

    def test_load_feature_excludes_ignores_comments(self):
        """Should ignore comment lines."""
        exclude_content = "# Just a comment\nfeature1\n## Another comment"
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value=exclude_content):
                result = coverage.load_feature_excludes(Path("/repo"))

        assert result == {"feature1"}

    def test_load_feature_excludes_nonexistent_file(self):
        """Should return empty set if exclude file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            result = coverage.load_feature_excludes(Path("/repo"))
        assert result == set()

    def test_load_feature_excludes_handles_exceptions(self):
        """Should return empty set on file read errors."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", side_effect=Exception("Read error")):
                result = coverage.load_feature_excludes(Path("/repo"))
        assert result == set()


class TestDuplicateDetection:
    """Tests for duplicate setting ID detection."""

    def test_detect_duplicate_setting_ids_within_feature(self):
        """Should detect duplicates within single feature."""
        setting_ids_by_feature = {
            "feature1": ["GL-SET-001", "GL-SET-002", "GL-SET-001"],
        }

        within, across = coverage.detect_duplicate_setting_ids(setting_ids_by_feature)

        assert "feature1" in within
        assert "GL-SET-001" in within["feature1"]
        assert len(across) == 0

    def test_detect_duplicate_setting_ids_across_features(self):
        """Should detect duplicates across multiple features."""
        setting_ids_by_feature = {
            "feature1": ["GL-SET-001", "GL-SET-002"],
            "feature2": ["GL-SET-001", "GL-SET-003"],
        }

        within, across = coverage.detect_duplicate_setting_ids(setting_ids_by_feature)

        assert len(within) == 0
        assert "GL-SET-001" in across
        assert set(across["GL-SET-001"]) == {"feature1", "feature2"}

    def test_detect_duplicate_setting_ids_no_duplicates(self):
        """Should return empty dicts when no duplicates exist."""
        setting_ids_by_feature = {
            "feature1": ["GL-SET-001", "GL-SET-002"],
            "feature2": ["GL-SET-003", "GL-SET-004"],
        }

        within, across = coverage.detect_duplicate_setting_ids(setting_ids_by_feature)

        assert len(within) == 0
        assert len(across) == 0

    def test_detect_duplicate_setting_ids_empty_input(self):
        """Should handle empty input."""
        within, across = coverage.detect_duplicate_setting_ids({})
        assert len(within) == 0
        assert len(across) == 0


class TestTestFileSearching:
    """Tests for test file searching functionality."""

    @patch("pathlib.Path.glob")
    def test_find_setting_ids_in_test_files(self, mock_glob):
        """Should find setting IDs in test files."""
        mock_test_file = Mock()
        mock_test_file.read_text.return_value = """
def test_something():
    # Test for GL-SET-001
    assert check_setting("GL-SET-002")
    verify_config("GL-SET-003")
"""
        mock_glob.return_value = [mock_test_file]

        result = coverage.find_setting_ids_in_test_files(Path("/repo"))

        assert "GL-SET-001" in result
        assert "GL-SET-002" in result
        assert "GL-SET-003" in result

    @patch("pathlib.Path.glob")
    def test_find_setting_ids_handles_file_errors(self, mock_glob):
        """Should handle file read errors gracefully."""
        mock_test_file = Mock()
        mock_test_file.read_text.side_effect = Exception("Read error")
        mock_glob.return_value = [mock_test_file]

        result = coverage.find_setting_ids_in_test_files(Path("/repo"))

        assert len(result) == 0

    @patch("pathlib.Path.glob")
    def test_find_setting_ids_multiple_occurrences(self, mock_glob):
        """Should deduplicate setting IDs found multiple times."""
        mock_test_file = Mock()
        mock_test_file.read_text.return_value = "GL-SET-001 GL-SET-001 GL-SET-002"
        mock_glob.return_value = [mock_test_file]

        result = coverage.find_setting_ids_in_test_files(Path("/repo"))

        assert len(result) == 2
        assert "GL-SET-001" in result
        assert "GL-SET-002" in result


class TestReportGeneration:
    """Tests for report generation functions."""

    def test_build_report_v1_0_complete_structure(self):
        """Should build complete report with correct structure."""
        setting_ids_by_feature = {
            "feature1": ["GL-SET-001", "GL-SET-002"],
            "feature2": ["GL-SET-003"],
        }
        found_setting_ids = {"GL-SET-001", "GL-SET-003"}
        all_features = {"feature1", "feature2", "feature3"}
        excluded_features = set()

        report = coverage.build_report_v1_0(
            setting_ids_by_feature, found_setting_ids, all_features, excluded_features
        )

        assert report["version"] == "1.0"
        assert "summary" in report
        assert "features" in report
        assert report["summary"]["total_features"] == 3
        assert report["summary"]["coverage_percentage"] == 66.67

    def test_build_report_v1_0_with_excluded_features(self):
        """Should exclude specified features from report."""
        setting_ids_by_feature = {"feature1": ["GL-SET-001"]}
        found_setting_ids = set()
        all_features = {"feature1", "feature2"}
        excluded_features = {"feature2"}

        report = coverage.build_report_v1_0(
            setting_ids_by_feature, found_setting_ids, all_features, excluded_features
        )

        assert "feature2" in report["excluded_features"]
        assert report["summary"]["excluded_features"] == 1

    def test_build_report_v1_0_100_percent_coverage(self):
        """Should calculate 100% coverage correctly."""
        setting_ids_by_feature = {"feature1": ["GL-SET-001", "GL-SET-002"]}
        found_setting_ids = {"GL-SET-001", "GL-SET-002"}
        all_features = {"feature1"}
        excluded_features = set()

        report = coverage.build_report_v1_0(
            setting_ids_by_feature, found_setting_ids, all_features, excluded_features
        )

        assert report["summary"]["coverage_percentage"] == 100.0

    def test_build_report_v1_0_zero_coverage(self):
        """Should handle zero coverage."""
        setting_ids_by_feature = {"feature1": ["GL-SET-001"]}
        found_setting_ids = set()
        all_features = {"feature1"}
        excluded_features = set()

        report = coverage.build_report_v1_0(
            setting_ids_by_feature, found_setting_ids, all_features, excluded_features
        )

        assert report["summary"]["coverage_percentage"] == 0.0

    def test_generate_json_report_writes_file(self):
        """Should write JSON report to file."""
        setting_ids_by_feature = {"feature1": ["GL-SET-001"]}
        found_setting_ids = {"GL-SET-001"}
        all_features = {"feature1"}
        excluded_features = set()

        mock_open_func = mock_open()
        with patch("pathlib.Path.open", mock_open_func):
            with patch("pathlib.Path.mkdir"):
                report = coverage.generate_json_report(
                    setting_ids_by_feature,
                    found_setting_ids,
                    all_features,
                    excluded_features,
                    Path("/output/report.json"),
                )

        assert report["version"] == "1.0"
        mock_open_func.assert_called_once()

    def test_generate_json_report_invalid_schema_version(self):
        """Should raise ValueError for invalid schema version."""
        with pytest.raises(ValueError, match="Unsupported schema version"):
            coverage.generate_json_report(
                {}, set(), set(), set(), None, schema_version="99.0"
            )

    def test_generate_json_report_handles_file_errors(self):
        """Should handle file write errors gracefully."""
        setting_ids_by_feature = {"feature1": ["GL-SET-001"]}
        found_setting_ids = set()
        all_features = {"feature1"}
        excluded_features = set()

        with patch("pathlib.Path.open", side_effect=PermissionError()):
            with patch("pathlib.Path.mkdir"):
                # Should not raise, just print warning
                report = coverage.generate_json_report(
                    setting_ids_by_feature,
                    found_setting_ids,
                    all_features,
                    excluded_features,
                    Path("/output/report.json"),
                )

        assert report is not None


class TestCalculateCoverageStats:
    """Tests for calculate_coverage_stats function."""

    def test_calculates_correct_totals(self):
        """Should calculate correct total and covered counts."""
        setting_ids_by_feature = {
            "feature1": ["GL-SET-001", "GL-SET-002"],
            "feature2": ["GL-SET-003"],
        }
        found_setting_ids = {"GL-SET-001", "GL-SET-003"}

        stats = coverage.calculate_coverage_stats(
            setting_ids_by_feature, found_setting_ids
        )

        assert stats["total_setting_ids"] == 3
        assert stats["covered_count"] == 2
        assert stats["untested_count"] == 1
        assert stats["coverage_percentage"] == pytest.approx(66.67, rel=0.01)

    def test_identifies_orphaned_ids(self):
        """Should identify setting IDs in tests but not in features."""
        setting_ids_by_feature = {"feature1": ["GL-SET-001"]}
        found_setting_ids = {"GL-SET-001", "GL-SET-999", "GL-SET-888"}

        stats = coverage.calculate_coverage_stats(
            setting_ids_by_feature, found_setting_ids
        )

        assert len(stats["orphaned_ids"]) == 2
        assert "GL-SET-999" in stats["orphaned_ids"]
        assert "GL-SET-888" in stats["orphaned_ids"]

    def test_handles_empty_inputs(self):
        """Should handle empty feature and test data."""
        stats = coverage.calculate_coverage_stats({}, set())

        assert stats["total_setting_ids"] == 0
        assert stats["covered_count"] == 0
        assert stats["untested_count"] == 0
        assert stats["coverage_percentage"] == 0.0
        assert len(stats["orphaned_ids"]) == 0

    def test_coverage_percentage_calculation(self):
        """Should calculate coverage percentage correctly."""
        # 100% coverage
        setting_ids_by_feature = {"f1": ["GL-SET-001", "GL-SET-002"]}
        found_setting_ids = {"GL-SET-001", "GL-SET-002"}
        stats = coverage.calculate_coverage_stats(
            setting_ids_by_feature, found_setting_ids
        )
        assert stats["coverage_percentage"] == 100.0

        # 0% coverage
        found_setting_ids = set()
        stats = coverage.calculate_coverage_stats(
            setting_ids_by_feature, found_setting_ids
        )
        assert stats["coverage_percentage"] == 0.0

        # 50% coverage
        found_setting_ids = {"GL-SET-001"}
        stats = coverage.calculate_coverage_stats(
            setting_ids_by_feature, found_setting_ids
        )
        assert stats["coverage_percentage"] == 50.0

    def test_groups_by_feature_correctly(self):
        """Should group covered and untested IDs by feature."""
        setting_ids_by_feature = {
            "feature1": ["GL-SET-001", "GL-SET-002"],
            "feature2": ["GL-SET-003", "GL-SET-004"],
        }
        found_setting_ids = {"GL-SET-001", "GL-SET-003"}

        stats = coverage.calculate_coverage_stats(
            setting_ids_by_feature, found_setting_ids
        )

        assert "feature1" in stats["covered_by_feature"]
        assert "GL-SET-001" in stats["covered_by_feature"]["feature1"]
        assert "feature1" in stats["untested_by_feature"]
        assert "GL-SET-002" in stats["untested_by_feature"]["feature1"]


class TestJunitXmlReport:
    """Tests for generate_junit_xml_report function."""

    def test_xml_structure_is_valid(self):
        """Should generate valid XML structure."""
        setting_ids_by_feature = {"feature1": ["GL-SET-001"]}
        found_setting_ids = {"GL-SET-001"}
        all_features = {"feature1"}

        xml_root = coverage.generate_junit_xml_report(
            setting_ids_by_feature, found_setting_ids, all_features, {}, {}
        )

        assert xml_root.tag == "testsuites"
        assert xml_root.get("name") == "Setting ID Coverage"
        assert xml_root.get("timestamp") is not None

    def test_includes_all_test_suites(self):
        """Should include Feature Coverage, Duplicate Detection, and Orphaned IDs suites."""
        setting_ids_by_feature = {"feature1": ["GL-SET-001"]}
        found_setting_ids = {"GL-SET-001"}
        all_features = {"feature1"}

        xml_root = coverage.generate_junit_xml_report(
            setting_ids_by_feature, found_setting_ids, all_features, {}, {}
        )

        suites = list(xml_root)
        assert len(suites) == 3
        assert suites[0].get("name") == "Feature Coverage"
        assert suites[1].get("name") == "Duplicate Detection"
        assert suites[2].get("name") == "Orphaned IDs Detection"

    def test_handles_failures_correctly(self):
        """Should mark failures for untested and duplicate IDs."""
        setting_ids_by_feature = {"feature1": ["GL-SET-001", "GL-SET-002"]}
        found_setting_ids = {"GL-SET-001"}  # GL-SET-002 is untested
        all_features = {"feature1"}

        xml_root = coverage.generate_junit_xml_report(
            setting_ids_by_feature, found_setting_ids, all_features, {}, {}
        )

        # Check Feature Coverage suite has failures
        feature_suite = list(xml_root)[0]
        assert int(feature_suite.get("failures", "0")) > 0

    def test_reports_duplicates_in_xml(self):
        """Should include duplicate detection failures in XML."""
        setting_ids_by_feature = {"feature1": ["GL-SET-001"]}
        found_setting_ids = set()
        all_features = {"feature1"}
        within_dupes = {"feature1": ["GL-SET-001"]}
        across_dupes = {}

        xml_root = coverage.generate_junit_xml_report(
            setting_ids_by_feature,
            found_setting_ids,
            all_features,
            within_dupes,
            across_dupes,
        )

        dup_suite = list(xml_root)[1]
        assert int(dup_suite.get("failures", "0")) > 0

    def test_reports_orphaned_ids(self):
        """Should report orphaned IDs as failures."""
        setting_ids_by_feature = {"feature1": ["GL-SET-001"]}
        found_setting_ids = {"GL-SET-001", "GL-SET-999"}  # 999 is orphaned
        all_features = {"feature1"}

        xml_root = coverage.generate_junit_xml_report(
            setting_ids_by_feature, found_setting_ids, all_features, {}, {}
        )

        orphaned_suite = list(xml_root)[2]
        assert int(orphaned_suite.get("failures", "0")) == 1

    @patch("pathlib.Path.mkdir")
    @patch("xml.etree.ElementTree.ElementTree.write")
    def test_writes_to_file(self, mock_write, mock_mkdir):
        """Should write XML report to file."""
        setting_ids_by_feature = {"feature1": ["GL-SET-001"]}
        found_setting_ids = {"GL-SET-001"}
        all_features = {"feature1"}
        output_path = Path("/output/report.xml")

        coverage.generate_junit_xml_report(
            setting_ids_by_feature, found_setting_ids, all_features, {}, {}, output_path
        )

        mock_mkdir.assert_called_once()
        mock_write.assert_called_once()


class TestConsoleReporting:
    """Tests for console report generation."""

    @patch("builtins.print")
    def test_generate_cli_report_returns_correct_counts(self, mock_print):
        """Should return correct untested and orphaned counts."""
        setting_ids_by_feature = {
            "feature1": ["GL-SET-001", "GL-SET-002"],
        }
        found_setting_ids = {"GL-SET-001", "GL-SET-999"}  # 999 is orphaned
        all_features = {"feature1"}

        untested, orphaned = coverage.generate_cli_report(
            setting_ids_by_feature, found_setting_ids, all_features
        )

        assert untested == 1  # GL-SET-002 is untested
        assert orphaned == 1  # GL-SET-999 is orphaned

    @patch("builtins.print")
    def test_generate_cli_report_all_covered(self, mock_print):
        """Should handle 100% coverage correctly."""
        setting_ids_by_feature = {"feature1": ["GL-SET-001"]}
        found_setting_ids = {"GL-SET-001"}
        all_features = {"feature1"}

        untested, orphaned = coverage.generate_cli_report(
            setting_ids_by_feature, found_setting_ids, all_features
        )

        assert untested == 0
        assert orphaned == 0


class TestRegexPatterns:
    """Tests for regex pattern compilation."""

    def test_regex_patterns_initialization(self):
        """Should initialize regex patterns from config."""
        patterns = coverage.RegexPatterns(coverage.CONFIG)
        assert patterns.setting_id is not None
        assert patterns.inline_comment is not None

    def test_setting_id_pattern_matches(self):
        """Setting ID pattern should match valid IDs."""
        pattern = coverage.REGEX.setting_id
        assert pattern.search("GL-SET-001") is not None
        assert pattern.search("GL-SET-ABC-123") is not None
        assert pattern.search("GL-SET-test_name") is not None

    def test_setting_id_pattern_non_matches(self):
        """Setting ID pattern should not match invalid IDs."""
        pattern = coverage.REGEX.setting_id
        assert pattern.search("NOT-SET-001") is None
        assert pattern.search("GL_SET_001") is None

    def test_inline_comment_pattern_matches(self):
        """Inline comment pattern should match comments with setting IDs."""
        pattern = coverage.REGEX.inline_comment
        match = pattern.search("# GL-SET-001")
        assert match is not None
        assert match.group(1) == "GL-SET-001"

    def test_inline_comment_pattern_ignores_double_hash(self):
        """Should not match double hash comments."""
        pattern = coverage.REGEX.inline_comment
        assert pattern.search("## GL-SET-001") is None


class TestMainFunction:
    """Tests for main function and integration."""

    @patch("util.coverage.extract_setting_ids_from_features")
    @patch("util.coverage.find_setting_ids_in_test_files")
    @patch("util.coverage.detect_duplicate_setting_ids")
    @patch("util.coverage.generate_cli_report")
    @patch("util.coverage.generate_json_report")
    @patch("util.coverage.load_feature_excludes")
    @patch("pathlib.Path.exists")
    def test_main_returns_zero_on_success(
        self,
        mock_exists,
        mock_excludes,
        mock_json_report,
        mock_console_report,
        mock_detect_dupes,
        mock_find_in_tests,
        mock_extract,
    ):
        """Should return 0 when all setting IDs are covered."""
        mock_exists.return_value = True
        mock_excludes.return_value = set()
        mock_extract.return_value = {"feature1": ["GL-SET-001"]}
        mock_detect_dupes.return_value = ({}, {})
        mock_find_in_tests.return_value = {"GL-SET-001"}
        mock_console_report.return_value = (0, 0)  # untested=0, orphaned=0

        result = coverage.main()
        assert result == 0

    @patch("util.coverage.extract_setting_ids_from_features")
    @patch("util.coverage.find_setting_ids_in_test_files")
    @patch("util.coverage.detect_duplicate_setting_ids")
    @patch("util.coverage.load_feature_excludes")
    @patch("pathlib.Path.exists")
    def test_main_returns_one_on_duplicates(
        self,
        mock_exists,
        mock_excludes,
        mock_detect_dupes,
        mock_find_in_tests,
        mock_extract,
    ):
        """Should return 1 when duplicates are detected."""
        mock_exists.return_value = True
        mock_excludes.return_value = set()
        mock_extract.return_value = {"feature1": ["GL-SET-001", "GL-SET-001"]}
        mock_detect_dupes.return_value = ({"feature1": ["GL-SET-001"]}, {})

        result = coverage.main()
        assert result == 1

    @patch("util.coverage.extract_setting_ids_from_features")
    @patch("util.coverage.find_setting_ids_in_test_files")
    @patch("util.coverage.detect_duplicate_setting_ids")
    @patch("util.coverage.generate_cli_report")
    @patch("util.coverage.generate_json_report")
    @patch("util.coverage.load_feature_excludes")
    @patch("pathlib.Path.exists")
    def test_main_returns_two_on_untested(
        self,
        mock_exists,
        mock_excludes,
        mock_json_report,
        mock_console_report,
        mock_detect_dupes,
        mock_find_in_tests,
        mock_extract,
    ):
        """Should return 2 when there are untested setting IDs."""
        mock_exists.return_value = True
        mock_excludes.return_value = set()
        mock_extract.return_value = {"feature1": ["GL-SET-001", "GL-SET-002"]}
        mock_detect_dupes.return_value = ({}, {})
        mock_find_in_tests.return_value = {"GL-SET-001"}
        mock_console_report.return_value = (1, 0)  # untested=1, orphaned=0

        result = coverage.main()
        assert result == 2

    @patch("util.coverage.extract_setting_ids_from_features")
    @patch("util.coverage.find_setting_ids_in_test_files")
    @patch("util.coverage.detect_duplicate_setting_ids")
    @patch("util.coverage.generate_cli_report")
    @patch("util.coverage.generate_json_report")
    @patch("util.coverage.load_feature_excludes")
    @patch("pathlib.Path.exists")
    def test_main_returns_three_on_orphaned(
        self,
        mock_exists,
        mock_excludes,
        mock_json_report,
        mock_console_report,
        mock_detect_dupes,
        mock_find_in_tests,
        mock_extract,
    ):
        """Should return 3 when there are orphaned setting IDs."""
        mock_exists.return_value = True
        mock_excludes.return_value = set()
        mock_extract.return_value = {"feature1": ["GL-SET-001"]}
        mock_detect_dupes.return_value = ({}, {})
        mock_find_in_tests.return_value = {"GL-SET-001", "GL-SET-999"}
        mock_console_report.return_value = (0, 1)  # untested=0, orphaned=1

        result = coverage.main()
        assert result == 3

    @patch("util.coverage.extract_setting_ids_from_features")
    @patch("util.coverage.find_setting_ids_in_test_files")
    @patch("util.coverage.detect_duplicate_setting_ids")
    @patch("util.coverage.generate_cli_report")
    @patch("util.coverage.generate_json_report")
    @patch("util.coverage.load_feature_excludes")
    @patch("pathlib.Path.exists")
    def test_main_returns_four_on_both_untested_and_orphaned(
        self,
        mock_exists,
        mock_excludes,
        mock_json_report,
        mock_console_report,
        mock_detect_dupes,
        mock_find_in_tests,
        mock_extract,
    ):
        """Should return 4 when there are both untested and orphaned setting IDs."""
        mock_exists.return_value = True
        mock_excludes.return_value = set()
        mock_extract.return_value = {"feature1": ["GL-SET-001", "GL-SET-002"]}
        mock_detect_dupes.return_value = ({}, {})
        mock_find_in_tests.return_value = {"GL-SET-001", "GL-SET-999"}
        mock_console_report.return_value = (1, 1)  # untested=1, orphaned=1

        result = coverage.main()
        assert result == 4

    @patch("pathlib.Path.exists")
    def test_main_returns_one_when_features_dir_missing(self, mock_exists):
        """Should return 1 when features directory is missing."""
        mock_exists.return_value = False

        result = coverage.main()
        assert result == 1

    @patch("pathlib.Path.exists")
    def test_main_returns_one_when_tests_dir_missing(self, mock_exists):
        """Should return 1 when tests directory is missing."""
        # Mock exists to return True for features dir, False for tests dir
        mock_exists.side_effect = lambda: (
            "features" in str(mock_exists.call_args[0][0])
            if mock_exists.call_count > 0
            else True
        )

        # Simpler approach: just return different values for each call
        mock_exists.side_effect = [True, False]  # features exists, tests doesn't

        result = coverage.main()
        assert result == 1
