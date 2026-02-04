#!/usr/bin/env python3
"""
Generate static coverage reports by matching setting IDs from features with test files.

This script performs comprehensive coverage analysis without running tests:

1. Extracts setting IDs from features/*/ directories:
   - file.include.ids.yaml and initrd.include.ids.yaml files
   - file.include/* files (using file.include.ids.yaml mappings)
   - initrd.include/* files (using initrd.include.ids.yaml mappings)
   - exec.config, pkg.include, file.exclude (inline comments)

2. Validates setting ID uniqueness:
   - Detects duplicate IDs within individual features
   - Detects duplicate IDs across different features
   - Exits with error if duplicates found

3. Searches for setting IDs in tests/test_*.py files:
   - Finds all GL-SET-* references in test code
   - Identifies which setting IDs are covered by tests

4. Detects orphaned setting IDs:
   - Finds IDs referenced in tests but not defined in features
   - Helps identify typos or outdated test references

5. Generates multiple report formats:
   - Console: Human-readable coverage summary with color coding
   - JSON: Programmatic access with versioned schema
   - JUnit XML: CI/CD integration for test result tracking

This works without running tests and doesn't require pytest-cov or coverage.py.
"""

import ast
import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml


# Configuration
@dataclass(frozen=True)
class Config:
    """Central configuration for the coverage script."""

    setting_id_prefix: str = "GL-SET-"
    setting_id_pattern: str = r"GL-SET-[a-zA-Z0-9_-]+"
    inline_comment_pattern: str = r"^#\s+(GL-SET-[^\s]+)"
    test_file_pattern: str = "test_*.py"
    file_include_ids_yaml: str = "file.include.ids.yaml"
    initrd_include_ids_yaml: str = "initrd.include.ids.yaml"
    feature_excludes_file: str = "coverage.feature.excludes"
    report_file: str = "coverage_report.json"
    report_schema_version: str = "1.0"
    include_types: Tuple[str, ...] = ("file.include", "initrd.include")


CONFIG = Config()

# Repository paths
script_dir = Path(__file__).parent
repo_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))


# Pre-compiled regex patterns for performance
class RegexPatterns:
    """Pre-compiled regex patterns used throughout the script."""

    def __init__(self, config: Config):
        self.setting_id = re.compile(config.setting_id_pattern)
        self.inline_comment = re.compile(config.inline_comment_pattern, re.MULTILINE)


REGEX = RegexPatterns(CONFIG)


class PathMatcher:
    """Handles path normalization and matching for include files."""

    @staticmethod
    def normalize(path: str) -> str:
        """Normalize a file path by stripping quotes and slashes."""
        return path.strip("\"'/")

    @staticmethod
    def matches(path1: str, path2: str) -> bool:
        """Check if two paths match after normalization."""
        norm1 = PathMatcher.normalize(path1)
        norm2 = PathMatcher.normalize(path2)

        # Try exact match, with/without leading slash
        return (
            norm1 == norm2 or norm1 == norm2.lstrip("/") or norm1.lstrip("/") == norm2
        )

    @staticmethod
    def find_in_list(file_list: List[Dict[str, Any]], path: str) -> Optional[Any]:
        """Search list of dicts for matching file path."""
        if not isinstance(file_list, list):
            return None

        for entry in file_list:
            if isinstance(entry, dict) and PathMatcher.matches(
                entry.get("file", ""), path
            ):
                return entry.get("ids")
        return None

    @staticmethod
    def find_in_dict(mappings: Dict[str, Any], path: str) -> Optional[Any]:
        """Search dict for matching file path key."""
        if not isinstance(mappings, dict):
            return None

        for key in mappings:
            if PathMatcher.matches(key, path):
                return mappings[key]
        return None


def extract_setting_ids_from_yaml_mapping(mapping: Any) -> List[str]:
    """
    Recursively extract all setting IDs from a YAML mapping structure.

    Args:
        mapping: YAML structure (dict, list, or string)

    Returns:
        List of all GL-SET-* identifiers found
    """
    setting_ids = []

    if isinstance(mapping, str):
        if mapping.startswith(CONFIG.setting_id_prefix):
            setting_ids.append(mapping)
    elif isinstance(mapping, dict):
        for value in mapping.values():
            setting_ids.extend(extract_setting_ids_from_yaml_mapping(value))
    elif isinstance(mapping, list):
        for item in mapping:
            setting_ids.extend(extract_setting_ids_from_yaml_mapping(item))

    return setting_ids


def extract_setting_ids_from_include_file(
    config_file: Path,
    feature_dir: Path,
    setting_ids_mapping: Dict[str, Any],
    include_type: str = "file.include",
) -> List[str]:
    """
    Extract setting IDs from file.include or initrd.include files using file.include.ids.yaml and initrd.include.ids.yaml mappings.

    Args:
        config_file: Path to the config file
        feature_dir: Path to the feature directory
        setting_ids_mapping: The setting_ids mapping from YAML
        include_type: Either "file.include" or "initrd.include"

    Returns:
        List of setting IDs for this file, or empty list if no mapping found
    """
    rel_path = str(config_file.relative_to(feature_dir))
    if not rel_path.startswith(f"{include_type}/"):
        return []

    # Extract the actual file path (remove include_type prefix)
    file_path = rel_path.replace(f"{include_type}/", "", 1)

    # Determine mapping key based on include type
    mapping_key = "file" if include_type == "file.include" else "initrd"

    # Try new structure: setting_ids.file.include = [{"file": "...", "ids": [...]}]
    if mapping_key in setting_ids_mapping:
        mapping_section = setting_ids_mapping[mapping_key]
        if isinstance(mapping_section, dict) and "include" in mapping_section:
            file_list = mapping_section["include"]
            if isinstance(file_list, list):
                result = PathMatcher.find_in_list(file_list, file_path)
                if result:
                    return extract_setting_ids_from_yaml_mapping(result)

    # Try old structure: setting_ids.file.include = {"/path": [...]}
    fallback_key = f"{mapping_key}.include"
    if fallback_key in setting_ids_mapping:
        mappings = setting_ids_mapping[fallback_key]
        if isinstance(mappings, dict):
            result = PathMatcher.find_in_dict(mappings, file_path)
            if result:
                return extract_setting_ids_from_yaml_mapping(result)

    return []


def load_feature_excludes(repo_root: Path) -> Set[str]:
    """
    Load feature excludes from tests/util/coverage.feature.excludes.

    Returns a set of feature names that should be excluded from coverage analysis.
    """
    excludes_file = repo_root / "tests" / "util" / CONFIG.feature_excludes_file
    if not excludes_file.exists():
        return set()

    try:
        content = excludes_file.read_text()
        # Parse lines, ignoring comments and empty lines
        return {
            line.strip()
            for line in content.splitlines()
            if line.strip() and not line.strip().startswith("#")
        }
    except Exception:
        return set()


def load_ids_files(feature_dir: Path) -> Dict[str, Any]:
    """
    Load setting IDs from file.include.ids.yaml and initrd.include.ids.yaml.

    Args:
        feature_dir: Path to the feature directory

    Returns:
        Combined setting_ids mapping compatible with old structure
    """
    combined_mapping = {}

    # Load file.include.ids.yaml
    file_ids_path = feature_dir / CONFIG.file_include_ids_yaml
    if file_ids_path.exists():
        try:
            file_data = yaml.safe_load(file_ids_path.read_text()) or {}
            if "setting_ids" in file_data and isinstance(
                file_data["setting_ids"], dict
            ):
                # Convert new format to old format for compatibility
                file_includes = []
                for path, ids in file_data["setting_ids"].items():
                    file_includes.append({"file": path, "ids": ids})
                combined_mapping["file"] = {"include": file_includes}
        except Exception:
            pass

    # Load initrd.include.ids.yaml
    initrd_ids_path = feature_dir / CONFIG.initrd_include_ids_yaml
    if initrd_ids_path.exists():
        try:
            initrd_data = yaml.safe_load(initrd_ids_path.read_text()) or {}
            if "setting_ids" in initrd_data and isinstance(
                initrd_data["setting_ids"], dict
            ):
                # Convert new format to old format for compatibility
                initrd_includes = []
                for path, ids in initrd_data["setting_ids"].items():
                    initrd_includes.append({"file": path, "ids": ids})
                combined_mapping["initrd"] = {"include": initrd_includes}
        except Exception:
            pass

    return combined_mapping


def extract_setting_ids_from_features(
    repo_root: Path, excluded_features: Optional[Set[str]] = None
) -> Dict[str, List[str]]:
    """
    Extract all setting IDs directly from features directory.

    Scans:
    - features/*/file.include.ids.yaml and features/*/initrd.include.ids.yaml
    - features/*/file.include/* files using setting_ids mappings
    - features/*/initrd.include/* files using setting_ids mappings

    Args:
        repo_root: Root directory of the repository
        excluded_features: Set of feature names to exclude from analysis

    Returns a dict mapping feature name to list of setting IDs.
    """
    features_dir = repo_root / "features"
    setting_ids_by_feature = {}
    excluded_features = excluded_features or set()

    if not features_dir.exists():
        return setting_ids_by_feature

    for feature_dir in features_dir.iterdir():
        if not feature_dir.is_dir():
            continue

        feature = feature_dir.name

        # Skip excluded features
        if feature in excluded_features:
            continue
        setting_ids = []

        # Load new split format files
        setting_ids_mapping = load_ids_files(feature_dir)

        # Scan all config files
        for config_file in feature_dir.rglob("*"):
            try:
                if not config_file.is_file():
                    continue
            except (PermissionError, OSError):
                # Skip files/directories we can't access
                continue

            rel_path = str(config_file.relative_to(feature_dir))

            # Check if this is a file.include or initrd.include file (use setting_ids mappings)
            if rel_path.startswith("file.include/"):
                file_setting_ids = extract_setting_ids_from_include_file(
                    config_file, feature_dir, setting_ids_mapping, "file.include"
                )
                setting_ids.extend(file_setting_ids)
            elif rel_path.startswith("initrd.include/"):
                initrd_setting_ids = extract_setting_ids_from_include_file(
                    config_file, feature_dir, setting_ids_mapping, "initrd.include"
                )
                setting_ids.extend(initrd_setting_ids)
            else:
                # For other files (pkg.include, exec.config, file.exclude), use inline comments
                # Only check files in the root of the feature directory (not subdirectories)
                if config_file.parent == feature_dir:
                    try:
                        content = config_file.read_text()
                        # Find inline comments with test IDs (match # GL-SET- but not ## GL-SET-)
                        found = re.findall(
                            r"^#\s+(GL-SET-[^\s]+)", content, re.MULTILINE
                        )
                        setting_ids.extend(found)
                    except (UnicodeDecodeError, PermissionError, Exception):
                        continue

        # Keep all setting IDs (including duplicates) for duplicate detection
        # We'll deduplicate later after checking for duplicates
        if setting_ids:
            setting_ids_by_feature[feature] = setting_ids

    return setting_ids_by_feature


def detect_duplicate_setting_ids(
    setting_ids_by_feature: Dict[str, List[str]],
) -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Detect duplicate setting IDs within features and across features using Counter for efficiency.

    Args:
        setting_ids_by_feature: Dict mapping feature names to their setting IDs (may contain duplicates)

    Returns:
        Tuple of (within_feature_duplicates, across_features_duplicates) where:
        - within_feature_duplicates: Dict mapping feature names to list of duplicate IDs within that feature
        - across_features_duplicates: Dict mapping setting IDs to list of features where they appear
    """
    within_feature_duplicates = {}
    setting_id_to_features: Dict[str, List[str]] = {}

    # Check for duplicates within each feature using Counter
    for feature, setting_ids in setting_ids_by_feature.items():
        counter = Counter(setting_ids)
        duplicates = [sid for sid, count in counter.items() if count > 1]
        if duplicates:
            within_feature_duplicates[feature] = sorted(duplicates)

        # Track unique setting IDs for cross-feature duplicate detection
        for sid in counter.keys():
            if sid not in setting_id_to_features:
                setting_id_to_features[sid] = []
            setting_id_to_features[sid].append(feature)

    # Check for duplicates across features
    across_features_duplicates = {
        sid: sorted(features)
        for sid, features in setting_id_to_features.items()
        if len(features) > 1
    }

    return within_feature_duplicates, across_features_duplicates


def find_setting_ids_in_test_files(repo_root: Path) -> Set[str]:
    """
    Search for setting IDs in test files (tests/**/test_*.py).

    Excludes tests/util/tests and tests/plugins/tests which are unit tests
    for the test infrastructure itself.

    Returns a set of setting IDs that are referenced in test files.
    """
    found_setting_ids = set()
    tests_dir = repo_root / "tests"

    # Directories to exclude (unit tests for test infrastructure)
    exclude_dirs = {"util/tests", "plugins/tests"}

    # Search all test files recursively (including subdirectories)
    for test_file in tests_dir.rglob("test_*.py"):
        # Skip files in excluded directories
        try:
            rel_path = test_file.relative_to(tests_dir)
            if any(str(rel_path).startswith(excl) for excl in exclude_dirs):
                continue
        except ValueError:
            continue

        try:
            content = test_file.read_text()
            # Find all GL-SET-* strings in the file
            setting_id_pattern = r"GL-SET-[a-zA-Z0-9_-]+"
            found = re.findall(setting_id_pattern, content)
            found_setting_ids.update(found)
        except Exception:
            continue

    return found_setting_ids


def count_test_functions(repo_root: Path) -> Dict[str, int]:
    """
    Count test functions in test files and identify which have setting_ids markers.

    Excludes tests/util/tests and tests/plugins/tests which are unit tests
    for the test infrastructure itself.

    Returns:
        Dict with counts:
        - total_tests: Total number of test functions found
        - tests_with_setting_ids: Number of tests with @pytest.mark.setting_ids decorator
        - tests_without_setting_ids: Number of tests without setting_ids decorator
    """
    tests_dir = repo_root / "tests"

    # Directories to exclude (unit tests for test infrastructure)
    exclude_dirs = {"util/tests", "plugins/tests"}

    total_tests = 0
    tests_with_setting_ids = 0

    # Search all test files recursively
    for test_file in tests_dir.rglob("test_*.py"):
        # Skip files in excluded directories
        try:
            rel_path = test_file.relative_to(tests_dir)
            if any(str(rel_path).startswith(excl) for excl in exclude_dirs):
                continue
        except ValueError:
            continue

        try:
            content = test_file.read_text()
            tree = ast.parse(content, filename=str(test_file))

            # Walk through all function definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if it's a test function (starts with 'test_')
                    if node.name.startswith("test_"):
                        total_tests += 1

                        # Check if it has @pytest.mark.setting_ids decorator
                        has_setting_ids = False
                        for decorator in node.decorator_list:
                            # Handle both attribute access (pytest.mark.setting_ids)
                            # and direct name (setting_ids) decorators
                            if isinstance(decorator, ast.Call):
                                # @pytest.mark.setting_ids(...)
                                if isinstance(decorator.func, ast.Attribute):
                                    if (
                                        isinstance(decorator.func.value, ast.Attribute)
                                        and isinstance(
                                            decorator.func.value.value, ast.Name
                                        )
                                        and decorator.func.value.value.id == "pytest"
                                        and decorator.func.value.attr == "mark"
                                        and decorator.func.attr == "setting_ids"
                                    ):
                                        has_setting_ids = True
                                        break

                        if has_setting_ids:
                            tests_with_setting_ids += 1

        except (SyntaxError, UnicodeDecodeError, Exception):
            # Skip files that can't be parsed
            continue

    tests_without_setting_ids = total_tests - tests_with_setting_ids

    return {
        "total_tests": total_tests,
        "tests_with_setting_ids": tests_with_setting_ids,
        "tests_without_setting_ids": tests_without_setting_ids,
    }


def calculate_coverage_stats(
    setting_ids_by_feature: Dict[str, List[str]],
    found_setting_ids: Set[str],
) -> Dict[str, Any]:
    """
    Calculate coverage statistics for features and setting IDs.

    Args:
        setting_ids_by_feature: Dict mapping feature names to their setting IDs
        found_setting_ids: Set of setting IDs found in test files

    Returns:
        Dict with statistics:
        - total_setting_ids: Total number of setting IDs
        - covered_count: Number of setting IDs found in tests
        - untested_count: Number of setting IDs not found in tests
        - coverage_percentage: Coverage percentage
        - covered_by_feature: Dict mapping features to lists of covered IDs
        - untested_by_feature: Dict mapping features to lists of untested IDs
        - orphaned_ids: Set of setting IDs in tests but not in features
    """
    total_setting_ids = sum(len(ids) for ids in setting_ids_by_feature.values())

    # Get all feature setting IDs
    all_feature_setting_ids = set()
    for ids in setting_ids_by_feature.values():
        all_feature_setting_ids.update(ids)

    # Calculate covered and untested IDs
    covered_by_feature = {}
    untested_by_feature = {}
    covered_count = 0

    for feature, feature_ids in setting_ids_by_feature.items():
        covered = [tid for tid in feature_ids if tid in found_setting_ids]
        untested = [tid for tid in feature_ids if tid not in found_setting_ids]

        if covered:
            covered_by_feature[feature] = covered
        if untested:
            untested_by_feature[feature] = untested

        covered_count += len(covered)

    untested_count = total_setting_ids - covered_count
    coverage_percentage = (
        (covered_count / total_setting_ids * 100) if total_setting_ids > 0 else 0.0
    )

    # Calculate orphaned IDs (in tests but not in features)
    orphaned_ids = found_setting_ids - all_feature_setting_ids

    return {
        "total_setting_ids": total_setting_ids,
        "covered_count": covered_count,
        "untested_count": untested_count,
        "coverage_percentage": coverage_percentage,
        "covered_by_feature": covered_by_feature,
        "untested_by_feature": untested_by_feature,
        "orphaned_ids": orphaned_ids,
    }


def build_report_v1_0(
    setting_ids_by_feature: Dict[str, List[str]],
    found_setting_ids: Set[str],
    all_features: Set[str],
    excluded_features: Set[str],
    test_counts: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """
    Build a JSON report following schema version 1.0.

    Args:
        setting_ids_by_feature: Dict mapping feature names to their setting IDs
        found_setting_ids: Set of setting IDs found in test files
        all_features: Set of all feature names
        excluded_features: Set of excluded feature names
        test_counts: Optional dict with test function counts

    Returns:
        Report dict following schema v1.0
    """
    # Calculate coverage statistics
    stats = calculate_coverage_stats(setting_ids_by_feature, found_setting_ids)

    features_without_ids = sorted(
        all_features - set(setting_ids_by_feature.keys()) - excluded_features
    )

    # Build feature details
    features_list = []
    for feature in sorted(set(setting_ids_by_feature.keys()) | all_features):
        if feature in excluded_features:
            continue

        if feature in setting_ids_by_feature:
            feature_setting_ids = setting_ids_by_feature[feature]
            covered = [tid for tid in feature_setting_ids if tid in found_setting_ids]
            untested = [
                tid for tid in feature_setting_ids if tid not in found_setting_ids
            ]
            feature_coverage = (
                (len(covered) / len(feature_setting_ids) * 100)
                if feature_setting_ids
                else 0.0
            )

            features_list.append(
                {
                    "name": feature,
                    "has_setting_ids": True,
                    "total_setting_ids": len(feature_setting_ids),
                    "covered_setting_ids": len(covered),
                    "untested_setting_ids": len(untested),
                    "coverage_percentage": round(feature_coverage, 2),
                    "setting_ids": {
                        "all": sorted(feature_setting_ids),
                        "covered": sorted(covered),
                        "untested": sorted(untested),
                    },
                }
            )
        else:
            features_list.append(
                {
                    "name": feature,
                    "has_setting_ids": False,
                    "total_setting_ids": 0,
                    "covered_setting_ids": 0,
                    "untested_setting_ids": 0,
                    "coverage_percentage": None,
                    "setting_ids": {"all": [], "covered": [], "untested": []},
                }
            )

    summary = {
        "total_features": len(all_features),
        "features_with_setting_ids": len(setting_ids_by_feature),
        "features_without_setting_ids": len(features_without_ids),
        "excluded_features": len(excluded_features),
        "total_setting_ids": stats["total_setting_ids"],
        "covered_setting_ids": stats["covered_count"],
        "untested_setting_ids": stats["untested_count"],
        "coverage_percentage": round(stats["coverage_percentage"], 2),
    }

    # Add test counts if provided
    if test_counts:
        summary["total_test_functions"] = test_counts["total_tests"]
        summary["tests_with_setting_ids"] = test_counts["tests_with_setting_ids"]
        summary["tests_without_setting_ids"] = test_counts["tests_without_setting_ids"]

    return {
        "version": "1.0",
        "summary": summary,
        "features": features_list,
        "excluded_features": sorted(excluded_features),
        "features_without_setting_ids": features_without_ids,
    }


# Registry of schema builders - maps version to builder function
# This must be defined AFTER the builder functions
REPORT_SCHEMA_BUILDERS = {
    "1.0": build_report_v1_0,
    # Future versions can be added here:
    # "2.0": build_report_v2_0,
}


def report_duplicate_errors(
    setting_ids_by_feature_raw: Dict[str, List[str]],
    within_feature_dupes: Dict[str, List[str]],
    across_feature_dupes: Dict[str, List[str]],
) -> None:
    """
    Report duplicate setting ID errors to the console.

    Args:
        setting_ids_by_feature_raw: Dict mapping feature names to their setting IDs (including duplicates)
        within_feature_dupes: Dict of duplicate IDs within features
        across_feature_dupes: Dict of duplicate IDs across features
    """
    print("\n" + "=" * 80)
    print("❌ ERROR: DUPLICATE SETTING IDs DETECTED")
    print("=" * 80)

    if within_feature_dupes:
        print("\n🔴 Duplicates within features:")
        print("-" * 80)
        print(
            "The following setting IDs appear multiple times within the same feature."
        )
        print("Each setting ID should only be defined once per feature.\n")
        for feature in sorted(within_feature_dupes.keys()):
            dupes = within_feature_dupes[feature]
            print(f"\nFeature '{feature}' has {len(dupes)} duplicate setting ID(s):")
            for sid in dupes:
                count = setting_ids_by_feature_raw[feature].count(sid)
                print(f"  - {sid} (appears {count} times)")

    if across_feature_dupes:
        print("\n🔴 Duplicates across features:")
        print("-" * 80)
        print("The following setting IDs appear in multiple features.")
        print("Each setting ID should only be defined once across all features.\n")
        for sid in sorted(across_feature_dupes.keys()):
            features = across_feature_dupes[sid]
            print(f"\n  {sid}")
            print(f"  appears in {len(features)} features:")
            for feature in features:
                print(f"    - {feature}")

    print("\n" + "=" * 80)
    print("Please fix these duplicate setting IDs before proceeding.")
    print("=" * 80 + "\n")


def generate_cli_report(
    setting_ids_by_feature: Dict[str, List[str]],
    found_setting_ids: Set[str],
    all_features: Set[str],
    test_counts: Dict[str, int],
) -> tuple[int, int]:
    """
    Generate a human-readable CLI coverage report showing which setting IDs are covered/uncovered.

    Args:
        setting_ids_by_feature: Dict mapping feature names to their setting IDs
        found_setting_ids: Set of setting IDs found in test files
        all_features: Set of all feature names
        test_counts: Dict with test function counts

    Returns:
        Tuple of (untested_count, orphaned_count) for exit code determination
    """
    print("\n" + "=" * 80)
    print("SETTING ID COVERAGE REPORT")
    print("=" * 80)

    # Calculate coverage statistics using the shared function
    stats = calculate_coverage_stats(setting_ids_by_feature, found_setting_ids)

    # Display summary
    print(f"\nSummary:")
    print(f"  Total setting IDs defined: {stats['total_setting_ids']}")
    print(f"  Setting IDs found in test files: {stats['covered_count']}")
    print(f"  Setting IDs not found (untested): {stats['untested_count']}")
    print(
        f"  Orphaned setting IDs (in tests but not features): {len(stats['orphaned_ids'])}"
    )
    print(f"  Coverage: {stats['coverage_percentage']:.1f}%")
    print()
    print(f"  Total test functions: {test_counts['total_tests']}")
    print(f"  Tests with setting IDs: {test_counts['tests_with_setting_ids']}")
    print(f"  Tests without setting IDs: {test_counts['tests_without_setting_ids']}")

    if stats["untested_count"] == 0 and stats["total_setting_ids"] > 0:
        print("\n✓ All setting IDs are found in test files!")
    elif stats["total_setting_ids"] == 0:
        print("\n⚠ No setting IDs defined in any features.")
    else:
        # Show coverage by feature
        print(f"\nCoverage by feature:")
        print("-" * 80)
        for feature in sorted(setting_ids_by_feature.keys()):
            feature_setting_ids = setting_ids_by_feature[feature]
            feature_covered = len(
                [tid for tid in feature_setting_ids if tid in found_setting_ids]
            )
            feature_coverage = (
                (feature_covered / len(feature_setting_ids) * 100)
                if feature_setting_ids
                else 0.0
            )
            status = "✓" if feature_covered == len(feature_setting_ids) else "⚠"
            print(
                f"{status} {feature}: {feature_covered}/{len(feature_setting_ids)} ({feature_coverage:.1f}%)"
            )

        # Show features with no setting IDs defined
        features_without_ids = all_features - set(setting_ids_by_feature.keys())
        if features_without_ids:
            print(f"\nFeatures without setting IDs ({len(features_without_ids)}):")
            print("-" * 80)
            for feature in sorted(features_without_ids):
                print(f"○ {feature}: 0/0 (N/A - no setting IDs defined)")

        # Show untested setting IDs by feature
        if stats["untested_by_feature"]:
            print(f"\nUntested setting IDs by feature:")
            print("-" * 80)
            for feature in sorted(stats["untested_by_feature"].keys()):
                untested = stats["untested_by_feature"][feature]
                print(f"\n{feature}:")
                print(f"  Total setting IDs: {len(setting_ids_by_feature[feature])}")
                print(
                    f"  Covered: {len(setting_ids_by_feature[feature]) - len(untested)}"
                )
                print(f"  Untested: {len(untested)}")
                print(f"  Untested setting IDs:")
                for tid in untested:
                    print(f"    - {tid}")

    # Show orphaned setting IDs (in tests but not in features)
    if stats["orphaned_ids"]:
        print(f"\n⚠ WARNING: Orphaned Setting IDs (in tests but not in features):")
        print("-" * 80)
        print(
            f"These setting IDs are referenced in test files but not defined in any feature."
        )
        print(
            f"This may indicate typos, missing feature definitions, or outdated tests.\n"
        )
        for tid in sorted(stats["orphaned_ids"]):
            print(f"    - {tid}")

    print("\n" + "=" * 80)

    return (stats["untested_count"], len(stats["orphaned_ids"]))


def generate_junit_xml_report(
    setting_ids_by_feature: Dict[str, List[str]],
    found_setting_ids: Set[str],
    all_features: Set[str],
    within_feature_dupes: Dict[str, List[str]],
    across_feature_dupes: Dict[str, List[str]],
    output_file: Optional[Path] = None,
) -> ET.Element:
    """
    Generate a JUnit XML report compatible with pytest and CI/CD systems.

    Args:
        setting_ids_by_feature: Dict mapping feature names to their setting IDs
        found_setting_ids: Set of setting IDs found in test files
        all_features: Set of all feature names
        within_feature_dupes: Dict of duplicate IDs within features
        across_feature_dupes: Dict of duplicate IDs across features
        output_file: Optional path to write XML report

    Returns:
        XML Element tree root
    """
    stats = calculate_coverage_stats(setting_ids_by_feature, found_setting_ids)

    # Create root testsuites element
    testsuites = ET.Element("testsuites")
    testsuites.set("name", "Setting ID Coverage")
    timestamp = datetime.now().isoformat()
    testsuites.set("timestamp", timestamp)

    # Testsuite 1: Feature Coverage
    total_tests = len(setting_ids_by_feature) + len(
        all_features - set(setting_ids_by_feature.keys())
    )
    failures = len(stats["untested_by_feature"])
    skipped = len(all_features - set(setting_ids_by_feature.keys()))

    suite1 = ET.SubElement(testsuites, "testsuite")
    suite1.set("name", "Feature Coverage")
    suite1.set("tests", str(total_tests))
    suite1.set("failures", str(failures))
    suite1.set("errors", "0")
    suite1.set("skipped", str(skipped))
    suite1.set("timestamp", timestamp)

    # Add test cases for each feature
    for feature in sorted(all_features):
        testcase = ET.SubElement(suite1, "testcase")
        testcase.set("name", feature)
        testcase.set("classname", "coverage.features")

        if feature not in setting_ids_by_feature:
            # Feature has no setting IDs - skip
            skipped_elem = ET.SubElement(testcase, "skipped")
            skipped_elem.set("message", "No setting IDs defined")
        elif feature in stats["untested_by_feature"]:
            # Feature has untested IDs - failure
            untested = stats["untested_by_feature"][feature]
            failure = ET.SubElement(testcase, "failure")
            failure.set("message", f"{len(untested)} untested setting ID(s)")
            failure.set("type", "UntestedSettingIDs")
            failure.text = f"Untested IDs:\n" + "\n".join(
                f"  - {sid}" for sid in untested
            )

    # Testsuite 2: Duplicate Detection
    dup_failures = len(within_feature_dupes) + (1 if across_feature_dupes else 0)
    suite2 = ET.SubElement(testsuites, "testsuite")
    suite2.set("name", "Duplicate Detection")
    suite2.set("tests", "1")
    suite2.set("failures", str(dup_failures))
    suite2.set("errors", "0")
    suite2.set("skipped", "0")
    suite2.set("timestamp", timestamp)

    # Test for within-feature duplicates
    if within_feature_dupes:
        for feature, dupes in within_feature_dupes.items():
            testcase = ET.SubElement(suite2, "testcase")
            testcase.set("name", f"no_duplicate_ids_within_{feature}")
            testcase.set("classname", "coverage.validation")
            failure = ET.SubElement(testcase, "failure")
            failure.set("message", f"{len(dupes)} duplicate setting ID(s) in {feature}")
            failure.set("type", "DuplicateSettingIDs")
            failure.text = "Duplicate IDs:\n" + "\n".join(f"  - {sid}" for sid in dupes)

    # Test for across-feature duplicates
    if across_feature_dupes:
        testcase = ET.SubElement(suite2, "testcase")
        testcase.set("name", "no_duplicate_ids_across_features")
        testcase.set("classname", "coverage.validation")
        failure = ET.SubElement(testcase, "failure")
        failure.set(
            "message",
            f"{len(across_feature_dupes)} setting ID(s) duplicated across features",
        )
        failure.set("type", "DuplicateSettingIDs")
        dup_details = []
        for sid, features in sorted(across_feature_dupes.items()):
            dup_details.append(f"  - {sid}: {', '.join(features)}")
        failure.text = "Duplicated across features:\n" + "\n".join(dup_details)

    if not within_feature_dupes and not across_feature_dupes:
        testcase = ET.SubElement(suite2, "testcase")
        testcase.set("name", "no_duplicate_setting_ids")
        testcase.set("classname", "coverage.validation")

    # Testsuite 3: Orphaned IDs Detection
    orphaned_count = len(stats["orphaned_ids"])
    suite3 = ET.SubElement(testsuites, "testsuite")
    suite3.set("name", "Orphaned IDs Detection")
    suite3.set("tests", "1")
    suite3.set("failures", "1" if orphaned_count > 0 else "0")
    suite3.set("errors", "0")
    suite3.set("skipped", "0")
    suite3.set("timestamp", timestamp)

    testcase = ET.SubElement(suite3, "testcase")
    testcase.set("name", "no_orphaned_setting_ids")
    testcase.set("classname", "coverage.validation")

    if orphaned_count > 0:
        failure = ET.SubElement(testcase, "failure")
        failure.set("message", f"{orphaned_count} orphaned setting ID(s)")
        failure.set("type", "OrphanedSettingIDs")
        failure.text = "IDs in tests but not in features:\n" + "\n".join(
            f"  - {sid}" for sid in sorted(stats["orphaned_ids"])
        )

    # Write to file if specified
    if output_file:
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            tree = ET.ElementTree(testsuites)
            ET.indent(tree, space="  ")
            tree.write(output_file, encoding="utf-8", xml_declaration=True)
            print(f"✓ JUnit XML report written to: {output_file}")
        except Exception as e:
            print(f"⚠ Warning: Could not write JUnit XML report to {output_file}: {e}")

    return testsuites


def generate_json_report(
    setting_ids_by_feature: Dict[str, List[str]],
    found_setting_ids: Set[str],
    all_features: Set[str],
    excluded_features: Set[str],
    test_counts: Optional[Dict[str, int]] = None,
    output_file: Optional[Path] = None,
    schema_version: str = CONFIG.report_schema_version,
) -> Dict[str, Any]:
    """
    Generate a JSON coverage report with a versioned schema.

    Args:
        setting_ids_by_feature: Dict mapping feature names to their setting IDs
        found_setting_ids: Set of setting IDs found in test files
        all_features: Set of all feature names
        excluded_features: Set of excluded feature names
        test_counts: Optional dict with test function counts
        output_file: Optional path to write JSON report
        schema_version: Schema version to use (default: current version)

    Returns:
        Generated report dict following the specified schema version

    Raises:
        ValueError: If unsupported schema version is specified
    """
    if schema_version not in REPORT_SCHEMA_BUILDERS:
        raise ValueError(
            f"Unsupported schema version: {schema_version}. "
            f"Available versions: {', '.join(REPORT_SCHEMA_BUILDERS.keys())}"
        )

    # Get the builder function for this schema version
    builder = REPORT_SCHEMA_BUILDERS[schema_version]

    # Build the report using the version-specific builder
    report = builder(
        setting_ids_by_feature,
        found_setting_ids,
        all_features,
        excluded_features,
        test_counts,
    )

    # Write to file if specified
    if output_file:
        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with output_file.open("w") as f:
                json.dump(report, f, indent=2)
            print(f"\n✓ JSON report written to: {output_file}")
        except Exception as e:
            print(f"\n⚠ Warning: Could not write JSON report to {output_file}: {e}")

    return report


def main():
    """Generate static coverage report by matching setting IDs from features with test files."""
    features_dir = repo_root / "features"
    tests_dir = repo_root / "tests"

    if not features_dir.exists():
        print(f"Error: Features directory not found: {features_dir}")
        return 1

    if not tests_dir.exists():
        print(f"Error: Tests directory not found: {tests_dir}")
        return 1

    # Load excluded features
    excluded_features = load_feature_excludes(repo_root)
    if excluded_features:
        print(f"Loading feature excludes...")
        print(
            f"✓ Excluding {len(excluded_features)} features: {', '.join(sorted(excluded_features))}\n"
        )

    print("Extracting setting IDs from features...")
    setting_ids_by_feature_raw = extract_setting_ids_from_features(
        repo_root, excluded_features
    )

    # Detect duplicate setting IDs before deduplication
    print("Checking for duplicate setting IDs...")
    within_feature_dupes, across_feature_dupes = detect_duplicate_setting_ids(
        setting_ids_by_feature_raw
    )

    # Report duplicate errors
    if within_feature_dupes or across_feature_dupes:
        report_duplicate_errors(
            setting_ids_by_feature_raw, within_feature_dupes, across_feature_dupes
        )
        return 1

    # Deduplicate setting IDs for coverage analysis (after duplicate check)
    setting_ids_by_feature = {}
    for feature, setting_ids in setting_ids_by_feature_raw.items():
        setting_ids_by_feature[feature] = sorted(set(setting_ids))

    # Get all feature names (including those without setting IDs)
    all_features = set()
    if features_dir.exists():
        for feature_dir in features_dir.iterdir():
            if feature_dir.is_dir():
                all_features.add(feature_dir.name)

    # Remove excluded features from all_features for reporting
    all_features = all_features - excluded_features

    total_features_with_ids = len(setting_ids_by_feature)
    total_setting_ids = sum(len(ids) for ids in setting_ids_by_feature.values())

    print(
        f"✓ Found {total_setting_ids} unique setting IDs across {total_features_with_ids} features\n"
    )

    print("Searching for setting IDs in test files...")
    found_setting_ids = find_setting_ids_in_test_files(repo_root)
    print(f"✓ Found {len(found_setting_ids)} setting ID references in test files\n")

    print("Counting test functions...")
    test_counts = count_test_functions(repo_root)
    print(
        f"✓ Found {test_counts['total_tests']} test functions ({test_counts['tests_with_setting_ids']} with setting IDs)\n"
    )

    # Generate human-readable CLI coverage report
    untested_count, orphaned_count = generate_cli_report(
        setting_ids_by_feature, found_setting_ids, all_features, test_counts
    )

    # Generate JSON report
    json_output = repo_root / "tests" / "coverage_report.json"
    generate_json_report(
        setting_ids_by_feature,
        found_setting_ids,
        all_features,
        excluded_features,
        test_counts,
        json_output,
    )

    # Generate JUnit XML report
    junit_output = repo_root / "tests" / "coverage_report.xml"
    generate_junit_xml_report(
        setting_ids_by_feature,
        found_setting_ids,
        all_features,
        within_feature_dupes,
        across_feature_dupes,
        junit_output,
    )

    # Determine exit code based on results
    # Exit 0: Success - all setting IDs properly covered, no orphans
    # Exit 2: Warning - Has untested setting IDs (features not covered by tests)
    # Exit 3: Warning - Has orphaned setting IDs (tests reference non-existent features)
    # Exit 4: Warning - Both untested AND orphaned setting IDs exist
    if untested_count > 0 and orphaned_count > 0:
        return 4
    elif orphaned_count > 0:
        return 3
    elif untested_count > 0:
        return 2
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
