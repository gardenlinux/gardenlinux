#!/usr/bin/env python3
"""
Generate static coverage reports by matching test IDs from features with test files.

This script:
1. Extracts all test IDs directly from features/*/ directories (info.yaml, exec.config, etc.)
2. Searches for those test IDs in tests-ng/test_*.py files
3. Generates a coverage report showing which test IDs are covered/uncovered

This works without running tests and doesn't require pytest-cov or coverage.py.
"""
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Any

# Add util to path
script_dir = Path(__file__).parent
repo_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    import yaml
except ImportError:
    yaml = None


def load_info_yaml(feature_dir: Path) -> Dict[str, Any]:
    """Load and parse info.yaml for a feature."""
    info_file = feature_dir / "info.yaml"
    if not info_file.exists() or yaml is None:
        return {}

    try:
        content = info_file.read_text()
        return yaml.safe_load(content) or {}
    except Exception:
        return {}


def extract_test_ids_from_yaml_mapping(mapping: Any) -> List[str]:
    """
    Recursively extract all test IDs from a YAML mapping structure.

    Handles nested dicts, lists, and string values.
    Returns a flat list of all GL-TEST-* strings found.
    """
    test_ids = []

    if isinstance(mapping, str):
        # Check if it's a test ID
        if mapping.startswith("GL-TEST-"):
            test_ids.append(mapping)
    elif isinstance(mapping, dict):
        # Recursively process dictionary values
        for value in mapping.values():
            test_ids.extend(extract_test_ids_from_yaml_mapping(value))
    elif isinstance(mapping, list):
        # Recursively process list items
        for item in mapping:
            test_ids.extend(extract_test_ids_from_yaml_mapping(item))

    return test_ids


def extract_test_ids_from_file_include(
    config_file: Path,
    feature_dir: Path,
    test_ids_mapping: Dict[str, Any]
) -> List[str]:
    """Extract test IDs from file.include files using info.yaml mappings."""
    rel_path = str(config_file.relative_to(feature_dir))
    if not rel_path.startswith("file.include/"):
        return []

    # Handle nested structure: test_ids.file.include["/etc/..."]
    file_mappings = None

    if "file.include" in test_ids_mapping:
        file_include_mappings = test_ids_mapping["file.include"]
        path_part = rel_path.replace("file.include/", "", 1)
        # Try various path formats
        for path_variant in [path_part, "/" + path_part, path_part.strip("/"), f'"{path_part}"', f'"/{path_part}"']:
            if path_variant in file_include_mappings:
                file_mappings = file_include_mappings[path_variant]
                break
            path_variant_unquoted = path_variant.strip('"\'')
            if path_variant_unquoted in file_include_mappings:
                file_mappings = file_include_mappings[path_variant_unquoted]
                break

    # Fallback to flat structure
    if not file_mappings:
        file_key_quoted = rel_path
        file_key_unquoted = rel_path.strip('"\'')
        file_mappings = test_ids_mapping.get(file_key_quoted) or test_ids_mapping.get(file_key_unquoted)

    if not file_mappings:
        return []

    # Extract test IDs from the mapping (handles nested structures)
    return extract_test_ids_from_yaml_mapping(file_mappings)


def extract_test_ids_from_features(repo_root: Path) -> Dict[str, List[str]]:
    """
    Extract all test IDs directly from features directory.

    Scans:
    - features/*/info.yaml for test_ids mappings
    - features/*/exec.config, pkg.include, file.exclude for inline # GL-TEST-... comments
    - features/*/file.include/* files using info.yaml mappings

    Returns a dict mapping feature name to list of test IDs.
    """
    features_dir = repo_root / "features"
    test_ids_by_feature = {}

    if not features_dir.exists():
        return test_ids_by_feature

    for feature_dir in features_dir.iterdir():
        if not feature_dir.is_dir():
            continue

        feature = feature_dir.name
        test_ids = []

        # Load info.yaml for test_ids mappings
        info_data = load_info_yaml(feature_dir)
        test_ids_mapping = {}
        if info_data and "test_ids" in info_data:
            test_ids_mapping = info_data["test_ids"]
            # Extract test IDs from the mapping structure
            test_ids.extend(extract_test_ids_from_yaml_mapping(test_ids_mapping))

        # Scan all config files
        for config_file in feature_dir.rglob("*"):
            if not config_file.is_file():
                continue

            rel_path = str(config_file.relative_to(feature_dir))

            # Check if this is a file.include file (use info.yaml mappings)
            if rel_path.startswith("file.include/"):
                file_test_ids = extract_test_ids_from_file_include(
                    config_file, feature_dir, test_ids_mapping
                )
                test_ids.extend(file_test_ids)
            else:
                # For other files (pkg.include, exec.config, file.exclude), use inline comments
                # Only check files in the root of the feature directory (not subdirectories)
                if config_file.parent == feature_dir:
                    try:
                        content = config_file.read_text()
                        # Find inline comments with test IDs
                        found = re.findall(r'#\s*(GL-TEST-[^\s]+)', content)
                        test_ids.extend(found)
                    except (UnicodeDecodeError, PermissionError, Exception):
                        continue

        # Deduplicate and sort
        if test_ids:
            test_ids_by_feature[feature] = sorted(set(test_ids))

    return test_ids_by_feature


def find_test_ids_in_test_files(repo_root: Path) -> Set[str]:
    """
    Search for test IDs in test files (tests-ng/test_*.py).

    Returns a set of test IDs that are referenced in test files.
    """
    found_test_ids = set()
    tests_dir = repo_root / "tests-ng"

    # Search all test files
    for test_file in tests_dir.glob("test_*.py"):
        try:
            content = test_file.read_text()
            # Find all GL-TEST-* strings in the file
            test_id_pattern = r'GL-TEST-[a-zA-Z0-9-]+'
            found = re.findall(test_id_pattern, content)
            found_test_ids.update(found)
        except Exception:
            continue

    return found_test_ids


def generate_untested_test_ids_report(
    test_ids_by_feature: Dict[str, List[str]],
    found_test_ids: Set[str],
    all_features: Set[str]
) -> None:
    """
    Generate a human-readable coverage report showing which test IDs are covered/uncovered.

    Calculates coverage percentages and shows per-feature breakdown.
    """
    print("\n" + "=" * 80)
    print("TEST ID COVERAGE REPORT")
    print("=" * 80)

    total_test_ids = sum(len(ids) for ids in test_ids_by_feature.values())
    total_found = len([tid for ids in test_ids_by_feature.values() for tid in ids if tid in found_test_ids])
    total_untested = total_test_ids - total_found

    # Calculate overall coverage percentage
    coverage_percent = (total_found / total_test_ids * 100) if total_test_ids > 0 else 0.0

    print(f"\nSummary:")
    print(f"  Total test IDs defined: {total_test_ids}")
    print(f"  Test IDs found in test files: {total_found}")
    print(f"  Test IDs not found (untested): {total_untested}")
    print(f"  Coverage: {coverage_percent:.1f}%")

    if total_untested == 0 and total_test_ids > 0:
        print("\n✓ All test IDs are found in test files!")
    elif total_test_ids == 0:
        print("\n⚠ No test IDs defined in any features.")
    else:
        # Find untested test IDs by feature
        untested_by_feature = {}
        covered_by_feature = {}
        for feature, feature_test_ids in test_ids_by_feature.items():
            untested = [tid for tid in feature_test_ids if tid not in found_test_ids]
            covered = [tid for tid in feature_test_ids if tid in found_test_ids]
            if untested:
                untested_by_feature[feature] = untested
            if covered:
                covered_by_feature[feature] = covered

        # Show coverage by feature (including features with no test IDs)
        print(f"\nCoverage by feature:")
        print("-" * 80)
        # Show features with test IDs first
        for feature in sorted(test_ids_by_feature.keys()):
            feature_test_ids = test_ids_by_feature[feature]
            feature_found = len([tid for tid in feature_test_ids if tid in found_test_ids])
            feature_coverage = (feature_found / len(feature_test_ids) * 100) if feature_test_ids else 0.0
            status = "✓" if feature_found == len(feature_test_ids) else "⚠"
            print(f"{status} {feature}: {feature_found}/{len(feature_test_ids)} ({feature_coverage:.1f}%)")

        # Show features with no test IDs defined
        features_without_ids = all_features - set(test_ids_by_feature.keys())
        if features_without_ids:
            for feature in sorted(features_without_ids):
                print(f"○ {feature}: 0/0 (N/A - no test IDs defined)")

        # Show untested test IDs by feature
        if untested_by_feature:
            print(f"\nUntested test IDs by feature:")
            print("-" * 80)
            for feature in sorted(untested_by_feature.keys()):
                untested = untested_by_feature[feature]
                print(f"\n{feature}:")
                print(f"  Total test IDs: {len(test_ids_by_feature[feature])}")
                print(f"  Covered: {len(test_ids_by_feature[feature]) - len(untested)}")
                print(f"  Untested: {len(untested)}")
                print(f"  Untested test IDs:")
                for tid in untested:
                    print(f"    - {tid}")

    print("\n" + "=" * 80)


def main():
    """Generate static coverage report by matching test IDs from features with test files."""
    features_dir = repo_root / "features"
    tests_dir = repo_root / "tests-ng"

    if not features_dir.exists():
        print(f"Error: Features directory not found: {features_dir}")
        return 1

    if not tests_dir.exists():
        print(f"Error: Tests directory not found: {tests_dir}")
        return 1

    print("Extracting test IDs from features...")
    test_ids_by_feature = extract_test_ids_from_features(repo_root)

    # Get all feature names (including those without test IDs)
    all_features = set()
    if features_dir.exists():
        for feature_dir in features_dir.iterdir():
            if feature_dir.is_dir():
                all_features.add(feature_dir.name)

    total_features_with_ids = len(test_ids_by_feature)
    total_test_ids = sum(len(ids) for ids in test_ids_by_feature.values())

    print(f"✓ Found {total_test_ids} test IDs across {total_features_with_ids} features\n")

    print("Searching for test IDs in test files...")
    found_test_ids = find_test_ids_in_test_files(repo_root)
    print(f"✓ Found {len(found_test_ids)} test ID references in test files\n")

    # Generate coverage report
    generate_untested_test_ids_report(test_ids_by_feature, found_test_ids, all_features)

    return 0


if __name__ == "__main__":
    sys.exit(main())
