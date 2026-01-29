#!/usr/bin/env python3
"""
Generate static coverage reports by matching test IDs from features with test files.

This script:
1. Extracts all test IDs directly from features/*/ directories (setting_ids.yaml, exec.config, etc.)
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


def load_setting_ids_yaml(feature_dir: Path) -> Dict[str, Any]:
    """Load and parse setting_ids.yaml for a feature."""
    setting_ids_file = feature_dir / "setting_ids.yaml"
    if not setting_ids_file.exists() or yaml is None:
        return {}

    try:
        content = setting_ids_file.read_text()
        return yaml.safe_load(content) or {}
    except Exception:
        return {}


def extract_setting_ids_from_yaml_mapping(mapping: Any) -> List[str]:
    """
    Recursively extract all setting IDs from a YAML mapping structure.

    Handles nested dicts, lists, and string values.
    Returns a flat list of all GL-SET-* strings found.
    """
    setting_ids = []

    if isinstance(mapping, str):
        # Check if it's a setting ID
        if mapping.startswith("GL-SET-"):
            setting_ids.append(mapping)
    elif isinstance(mapping, dict):
        # Recursively process dictionary values
        for value in mapping.values():
            setting_ids.extend(extract_setting_ids_from_yaml_mapping(value))
    elif isinstance(mapping, list):
        # Recursively process list items
        for item in mapping:
            setting_ids.extend(extract_setting_ids_from_yaml_mapping(item))

    return setting_ids


def extract_setting_ids_from_include_file(
    config_file: Path,
    feature_dir: Path,
    setting_ids_mapping: Dict[str, Any],
    include_type: str = "file.include"
) -> List[str]:
    """
    Extract setting IDs from file.include or initrd.include files using setting_ids.yaml mappings.

    Args:
        config_file: Path to the config file
        feature_dir: Path to the feature directory
        setting_ids_mapping: The setting_ids mapping from YAML
        include_type: Either "file.include" or "initrd.include"
    """
    rel_path = str(config_file.relative_to(feature_dir))
    if not rel_path.startswith(f"{include_type}/"):
        return []

    # Handle nested structure: setting_ids.file.include[{"file": "/etc/...", "ids": [...]}]
    file_mappings = None
    path_part = rel_path.replace(f"{include_type}/", "", 1)
    absolute_path = "/" + path_part

    # Try to access setting_ids.file.include (list of dicts)
    if "file" in setting_ids_mapping and isinstance(setting_ids_mapping["file"], dict):
        if "include" in setting_ids_mapping["file"]:
            file_include_list = setting_ids_mapping["file"]["include"]
            if isinstance(file_include_list, list):
                # Search through the list for matching file path
                for entry in file_include_list:
                    if isinstance(entry, dict):
                        # Try various path formats
                        file_path = entry.get("file", "")
                        # Normalize paths for comparison (remove leading/trailing slashes, quotes)
                        normalized_file_path = file_path.strip('"\'/')
                        normalized_path_part = path_part.strip('/')
                        normalized_absolute_path = absolute_path.strip('/')

                        if (file_path == path_part or file_path == absolute_path or
                            normalized_file_path == normalized_path_part or
                            normalized_file_path == normalized_absolute_path):
                            # Found matching entry - extract ids
                            if "ids" in entry:
                                file_mappings = entry["ids"]
                            break

    # Fallback: try old structure format (dict keyed by file paths)
    if not file_mappings:
        if "file.include" in setting_ids_mapping:
            file_include_mappings = setting_ids_mapping["file.include"]
            # Try various path formats
            for path_variant in [path_part, absolute_path, path_part.strip("/"), f'"{path_part}"', f'"{absolute_path}"']:
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
        file_mappings = setting_ids_mapping.get(file_key_quoted) or setting_ids_mapping.get(file_key_unquoted)

    if not file_mappings:
        return []

    # Extract setting IDs from the mapping (handles nested structures and lists)
    return extract_setting_ids_from_yaml_mapping(file_mappings)


def extract_setting_ids_from_features(repo_root: Path) -> Dict[str, List[str]]:
    """
    Extract all setting IDs directly from features directory.

    Scans:
    - features/*/setting_ids.yaml for setting_ids mappings
    - features/*/file.include/* files using setting_ids.yaml mappings
    - features/*/initrd.include/* files using setting_ids.yaml mappings

    Returns a dict mapping feature name to list of setting IDs.
    """
    features_dir = repo_root / "features"
    setting_ids_by_feature = {}

    if not features_dir.exists():
        return setting_ids_by_feature

    for feature_dir in features_dir.iterdir():
        if not feature_dir.is_dir():
            continue

        feature = feature_dir.name
        setting_ids = []

        # Load setting_ids.yaml for setting_ids mappings
        setting_ids_data = load_setting_ids_yaml(feature_dir)
        setting_ids_mapping = {}
        if setting_ids_data and "setting_ids" in setting_ids_data:
            setting_ids_mapping = setting_ids_data["setting_ids"]
            # Extract setting IDs from the mapping structure
            setting_ids.extend(extract_setting_ids_from_yaml_mapping(setting_ids_mapping))

        # Scan all config files
        for config_file in feature_dir.rglob("*"):
            if not config_file.is_file():
                continue

            rel_path = str(config_file.relative_to(feature_dir))

            # Check if this is a file.include or initrd.include file (use setting_ids.yaml mappings)
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
                        # Find inline comments with test IDs
                        found = re.findall(r'#\s*(GL-TEST-[^\s]+)', content)
                        setting_ids.extend(found)
                    except (UnicodeDecodeError, PermissionError, Exception):
                        continue

        # Deduplicate and sort
        if setting_ids:
            setting_ids_by_feature[feature] = sorted(set(setting_ids))

    return setting_ids_by_feature


def find_setting_ids_in_test_files(repo_root: Path) -> Set[str]:
    """
    Search for setting IDs in test files (tests-ng/test_*.py).

    Returns a set of setting IDs that are referenced in test files.
    """
    found_setting_ids = set()
    tests_dir = repo_root / "tests-ng"

    # Search all test files
    for test_file in tests_dir.glob("test_*.py"):
        try:
            content = test_file.read_text()
            # Find all GL-TEST-* strings in the file
            setting_id_pattern = r'GL-SET-[a-zA-Z0-9-]+'
            found = re.findall(setting_id_pattern, content)
            found_setting_ids.update(found)
        except Exception:
            continue

    return found_setting_ids


def generate_untested_setting_ids_report(
    setting_ids_by_feature: Dict[str, List[str]],
    found_setting_ids: Set[str],
    all_features: Set[str]
) -> None:
    """
    Generate a human-readable coverage report showing which setting IDs are covered/uncovered.

    Calculates coverage percentages and shows per-feature breakdown.
    """
    print("\n" + "=" * 80)
    print("SETTING ID COVERAGE REPORT")
    print("=" * 80)

    total_setting_ids = sum(len(ids) for ids in setting_ids_by_feature.values())
    total_found = len([tid for ids in setting_ids_by_feature.values() for tid in ids if tid in found_setting_ids])
    total_untested = total_setting_ids - total_found

    # Calculate overall coverage percentage
    coverage_percent = (total_found / total_setting_ids * 100) if total_setting_ids > 0 else 0.0

    print(f"\nSummary:")
    print(f"  Total setting IDs defined: {total_setting_ids}")
    print(f"  Setting IDs found in test files: {total_found}")
    print(f"  Setting IDs not found (untested): {total_untested}")
    print(f"  Coverage: {coverage_percent:.1f}%")

    if total_untested == 0 and total_setting_ids > 0:
        print("\n✓ All setting IDs are found in test files!")
    elif total_setting_ids == 0:
        print("\n⚠ No setting IDs defined in any features.")
    else:
        # Find untested setting IDs by feature
        untested_by_feature = {}
        covered_by_feature = {}
        for feature, feature_setting_ids in setting_ids_by_feature.items():
            untested = [tid for tid in feature_setting_ids if tid not in found_setting_ids]
            covered = [tid for tid in feature_setting_ids if tid in found_setting_ids]
            if untested:
                untested_by_feature[feature] = untested
            if covered:
                covered_by_feature[feature] = covered

        # Show coverage by feature (including features with no test IDs)
        print(f"\nCoverage by feature:")
        print("-" * 80)
        # Show features with setting IDs first
        for feature in sorted(setting_ids_by_feature.keys()):
            feature_setting_ids = setting_ids_by_feature[feature]
            feature_found = len([tid for tid in feature_setting_ids if tid in found_setting_ids])
            feature_coverage = (feature_found / len(feature_setting_ids) * 100) if feature_setting_ids else 0.0
            status = "✓" if feature_found == len(feature_setting_ids) else "⚠"
            print(f"{status} {feature}: {feature_found}/{len(feature_setting_ids)} ({feature_coverage:.1f}%)")

        # Show features with no setting IDs defined
        features_without_ids = all_features - set(setting_ids_by_feature.keys())
        if features_without_ids:
            for feature in sorted(features_without_ids):
                print(f"○ {feature}: 0/0 (N/A - no setting IDs defined)")

        # Show untested test IDs by feature
        if untested_by_feature:
            print(f"\nUntested setting IDs by feature:")
            print("-" * 80)
            for feature in sorted(untested_by_feature.keys()):
                untested = untested_by_feature[feature]
                print(f"\n{feature}:")
                print(f"  Total setting IDs: {len(setting_ids_by_feature[feature])}")
                print(f"  Covered: {len(setting_ids_by_feature[feature]) - len(untested)}")
                print(f"  Untested: {len(untested)}")
                print(f"  Untested setting IDs:")
                for tid in untested:
                    print(f"    - {tid}")

    print("\n" + "=" * 80)


def main():
    """Generate static coverage report by matching setting IDs from features with test files."""
    features_dir = repo_root / "features"
    tests_dir = repo_root / "tests-ng"

    if not features_dir.exists():
        print(f"Error: Features directory not found: {features_dir}")
        return 1

    if not tests_dir.exists():
        print(f"Error: Tests directory not found: {tests_dir}")
        return 1

    print("Extracting setting IDs from features...")
    setting_ids_by_feature = extract_setting_ids_from_features(repo_root)

    # Get all feature names (including those without setting IDs)
    all_features = set()
    if features_dir.exists():
        for feature_dir in features_dir.iterdir():
            if feature_dir.is_dir():
                all_features.add(feature_dir.name)

    total_features_with_ids = len(setting_ids_by_feature)
    total_setting_ids = sum(len(ids) for ids in setting_ids_by_feature.values())

    print(f"✓ Found {total_setting_ids} setting IDs across {total_features_with_ids} features\n")

    print("Searching for setting IDs in test files...")
    found_setting_ids = find_setting_ids_in_test_files(repo_root)
    print(f"✓ Found {len(found_setting_ids)} setting ID references in test files\n")

    # Generate coverage report
    generate_untested_setting_ids_report(setting_ids_by_feature, found_setting_ids, all_features)

    return 0


if __name__ == "__main__":
    sys.exit(main())
