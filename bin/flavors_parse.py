#!/usr/bin/env python
import yaml
import sys
import subprocess
import os
import argparse
import fnmatch
import json
from jsonschema import validate, ValidationError


# Define the schema for validation
SCHEMA = {
    "type": "object",
    "properties": {
        "targets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "category": {"type": "string"},
                    "flavors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "features": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "arch": {"type": "string"},
                                "build": {"type": "boolean"},
                                "test": {"type": "boolean"},
                                "test-platform": {"type": "boolean"},
                                "publish": {"type": "boolean"},
                            },
                            "required": ["features", "arch", "build", "test", "test-platform", "publish"],
                        },
                    },
                },
                "required": ["name", "category", "flavors"],
            },
        },
    },
    "required": ["targets"],
}


def find_repo_root():
    """Finds the root directory of the Git repository."""
    try:
        root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
        return root
    except subprocess.CalledProcessError:
        sys.exit("Error: Unable to determine Git repository root.")


def validate_flavors(data):
    """Validate the flavors.yaml data against the schema."""
    try:
        validate(instance=data, schema=SCHEMA)
    except ValidationError as e:
        sys.exit(f"Validation Error: {e.message}")


def should_exclude(combination, excludes, wildcard_excludes):
    """
    Checks if a combination should be excluded based on exact match or wildcard patterns.
    """
    # Exclude if in explicit excludes
    if combination in excludes:
        return True
    # Exclude if matches any wildcard pattern
    return any(fnmatch.fnmatch(combination, pattern) for pattern in wildcard_excludes)


def should_include_only(combination, include_only_patterns):
    """
    Checks if a combination should be included based on `--include-only` wildcard patterns.
    If no patterns are provided, all combinations are included by default.
    """
    if not include_only_patterns:
        return True
    return any(fnmatch.fnmatch(combination, pattern) for pattern in include_only_patterns)


def parse_flavors(
    data,
    include_only_patterns=[],
    wildcard_excludes=[],
    only_build=False,
    only_test=False,
    only_test_platform=False,
    only_publish=False,
    filter_categories=[],
    exclude_categories=[]
):
    """Parses the flavors.yaml file and generates combinations."""
    combinations = []  # Use a list for consistent order

    for target in data['targets']:
        name = target['name']
        category = target.get('category', '')

        # Apply category filters
        if filter_categories and category not in filter_categories:
            continue
        if exclude_categories and category in exclude_categories:
            continue

        for flavor in target['flavors']:
            features = flavor.get('features', [])
            arch = flavor.get('arch', 'amd64')
            build = flavor.get('build', False)
            test = flavor.get('test', False)
            test_platform = flavor.get('test-platform', False)
            publish = flavor.get('publish', False)

            # Apply flag-specific filters in the order: build, test, test-platform, publish
            if only_build and not build:
                continue
            if only_test and not test:
                continue
            if only_test_platform and not test_platform:
                continue
            if only_publish and not publish:
                continue

            # Process features
            formatted_features = f"-{'-'.join(features)}" if features else ""

            # Construct the combination
            combination = f"{name}-{formatted_features}-{arch}"

            # Format the combination to clean up "--" and "-_"
            combination = combination.replace("--", "-").replace("-_", "_")

            # Exclude combinations explicitly
            if should_exclude(combination, [], wildcard_excludes):
                continue

            # Apply include-only filters
            if not should_include_only(combination, include_only_patterns):
                continue

            combinations.append((arch, combination))

    return sorted(combinations, key=lambda x: x[1].split("-")[0])  # Sort by platform name


def group_by_arch(combinations):
    """Groups combinations by architecture into a JSON dictionary."""
    arch_dict = {}
    for arch, combination in combinations:
        arch_dict.setdefault(arch, []).append(combination)
    for arch in arch_dict:
        arch_dict[arch] = sorted(set(arch_dict[arch]))  # Deduplicate and sort
    return arch_dict


def remove_arch(combinations):
    """Removes the architecture from combinations."""
    return [combination.replace(f"-{arch}", "") for arch, combination in combinations]


def generate_markdown_table(combinations, no_arch):
    """Generate a markdown table of platforms and their flavors."""
    table = "| Platform   | Architecture       | Flavor                                  |\n"
    table += "|------------|--------------------|------------------------------------------|\n"

    for arch, combination in combinations:
        platform = combination.split("-")[0]
        table += f"| {platform:<10} | {arch:<18} | `{combination}`                   |\n"

    return table


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse flavors.yaml and generate combinations.")
    parser.add_argument("--no-arch", action="store_true", help="Exclude architecture from the flavor output.")
    parser.add_argument(
        "--include-only",
        action="append",
        help="Restrict combinations to those matching wildcard patterns (can be specified multiple times)."
    )
    parser.add_argument(
        "--exclude",
        action="append",
        help="Exclude combinations based on wildcard patterns (can be specified multiple times)."
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Filter combinations to include only those with build enabled."
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Filter combinations to include only those with test enabled."
    )
    parser.add_argument(
        "--test-platform",
        action="store_true",
        help="Filter combinations to include only platforms with test-platform: true."
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Filter combinations to include only those with publish enabled."
    )
    parser.add_argument(
        "--category",
        action="append",
        help="Filter combinations to include only platforms belonging to the specified categories (can be specified multiple times)."
    )
    parser.add_argument(
        "--exclude-category",
        action="append",
        help="Exclude platforms belonging to the specified categories (can be specified multiple times)."
    )
    parser.add_argument(
        "--json-by-arch",
        action="store_true",
        help="Output a JSON dictionary where keys are architectures and values are lists of flavors."
    )
    parser.add_argument(
        "--markdown-table-by-platform",
        action="store_true",
        help="Generate a markdown table by platform."
    )
    args = parser.parse_args()

    repo_root = find_repo_root()
    flavors_file = os.path.join(repo_root, 'flavors.yaml')
    if not os.path.isfile(flavors_file):
        sys.exit(f"Error: {flavors_file} does not exist.")
    
    # Load and validate the flavors.yaml
    with open(flavors_file, 'r') as file:
        flavors_data = yaml.safe_load(file)
    validate_flavors(flavors_data)

    combinations = parse_flavors(
        flavors_data,
        include_only_patterns=args.include_only or [],
        wildcard_excludes=args.exclude or [],
        only_build=args.build,
        only_test=args.test,
        only_test_platform=args.test_platform,
        only_publish=args.publish,
        filter_categories=args.category or [],
        exclude_categories=args.exclude_category or []
    )

    if args.json_by_arch:
        grouped_combinations = group_by_arch(combinations)
        # If --no-arch, strip architectures from the grouped output
        if args.no_arch:
            grouped_combinations = {
                arch: sorted(set(item.replace(f"-{arch}", "") for item in items))
                for arch, items in grouped_combinations.items()
            }
        print(json.dumps(grouped_combinations, indent=2))
    elif args.markdown_table_by_platform:
        markdown_table = generate_markdown_table(combinations, args.no_arch)
        print(markdown_table)
    else:
        if args.no_arch:
            no_arch_combinations = remove_arch(combinations)
            print("\n".join(sorted(set(no_arch_combinations))))
        else:
            print("\n".join(sorted(set(comb[1] for comb in combinations))))
