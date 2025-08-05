#!/usr/bin/env python3
import os
import yaml

# This script takes the differ_files results from the reproducibility check and generates a Result.md
# The differ_files contain paths of files which were different when building the flavor two times 

flavors = os.listdir("diffs")

all = set()
successful = []
failed = {} # {flavor: [files...]}

for flavor in flavors:
    if flavor.endswith("-diff"):
        with open(f"diffs/{flavor}", "r") as f:
            content = f.read()
        
        all.add(flavor[:-5])
        if content == "\n":
            successful.append(flavor[:-5])
        else:
            failed[flavor[:-5]] = content.split("\n")[:-1]

# Map files to flavors
affected = {} # {file: {flavors...}}
for flavor in failed:
    for file in failed[flavor]:
        if file not in affected:
            affected[file] = set()
        affected[file].add(flavor)

# Merge files affected by the same flavors by mapping flavor sets to files
bundled = {} # {{flavors...}: {files...}}
for file in affected:
    if frozenset(affected[file]) not in bundled:
        bundled[frozenset(affected[file])] = set()
    bundled[frozenset(affected[file])].add(file)

## Analyze the origin of the file change by intersecting the features of the affected flavors

# Helper for build_feature_tree() to recursively build the tree
def dependencies(feature, excludes):
    with open(f"features/{feature}/info.yaml") as f:
        data = yaml.safe_load(f)
    includes = {}
    if "features" in data and "include" in data["features"]:
        for include in data["features"]["include"]:
            if include not in excludes:
                excludes.add(include)
                deps, ex = dependencies(include, excludes)
                includes[include] = deps
                excludes.update(ex)
    return includes, excludes

# Returns a hierarchical order and a flat set 
def buildFeatureTree(flavor):
    sperated = flavor.split("-")
    if len(sperated) != 3:
        return {}, set()
    platform = sperated[0]
    features = {}
    excludes = set()
    for feature in sperated[1].split("_"):
        if len(features) > 0:
            feature = "_" + feature
        excludes.add(feature)
        deps, ex = dependencies(feature, excludes)
        features[feature] = deps
        excludes.update(ex)

    return features, excludes

# Filter a tree to only contain the features from the intersect set
def intersectionTree(tree, intersect):
    for feature in tree:
        subtree = intersectionTree(tree[feature], intersect)
        if feature not in intersect:
            del tree[feature]
            return intersectionTree(tree | subtree, intersect)
        else:
            tree[feature] = subtree
    return tree

# Format a tree for string outputs
def treeStr(tree):
    s = ""
    for feature in tree:
        if tree[feature] == {}:
            s += f"{feature}\n"
        else:
            s += f"{feature}:\n"
            s += "  " + treeStr(tree[feature]).replace("\n", "\n  ") + "\n"
    # Remove last linebreak as the last line can contain spaces
    return "\n".join(s.split("\n")[:-1])

trees = {} # {{files...}: ({flavors...}, FeatureTree)}
for flavors in bundled:
    # Only keep features active in every flavor
    features = set()
    first = True
    for flavor in flavors:
        tree, flat = buildFeatureTree(flavor)
        if first:
            features = flat
            first = False
        else:
            features = features.intersection(flat)

    # Remove features active in unaffected flavors
    unaffected = all - flavors
    for flavor in unaffected:
        _, flat = buildFeatureTree(flavor)
        features = features - flat

    # As all features must be contained in all trees, they are also in the last tree
    trees[frozenset(bundled[flavors])] = (flavors, intersectionTree(tree, features))

result = """# Reproducibility Test Results

{emoji} **{successrate}%** of **{total_count}** tested flavors were reproducible.{problem_count}

## Detailed Result{explanation}

<!-- multiline -->
| Affected Files | Flavors | Features Causing the Problem |
|----------------|---------|------------------------------|
{rows}
"""

successrate = round(100 * (len(successful) / len(all)), 1)

emoji = "✅" if len(all) == len(successful) else ("⚠️" if successrate >= 50.0 else "❌")

total_count = len(all)

problem_count = "" if len(trees) == 0 else ("\n**1** Problem detected." if len(trees) == 1 else f"\n**{len(trees)}** Problems detected.")

explanation = "" if len(all) == len(successful) else "\n\n*The mentioned features are included in every affected flavor and not included in every unaffected flavor.*"

rows = ""

def dropdown(items):
    if len(items) <= 10:
        return "<br>".join([f"`{item}`" for item in items])
    else:
        for first in items:
            return f"<details><summary>{first}...</summary>" + "<br>".join([f"`{item}`" for item in items]) + "</summary>"

for files in trees:
    flavors, tree = trees[files]
    row = "|"
    row += dropdown(files)
    row += "|"
    row += f"**{round(100 * (len(flavors) / len(all)), 1)}%** affected<br>"
    row += dropdown(flavors)
    row += "|"
    if tree == {}:
        row += "No analysis available"
    else:
        row += "`" + treeStr(tree).replace("\n", "`<br>`") + "`"
    row += "|\n"
    rows += row

if len(successful) > 0:
    # Success row
    row = "|"
    row += "✅ No problems found"
    row += "|"
    row += f"**{round(100 * (len(successful) / len(all)), 1)}%**<br>"
    row += dropdown(successful)
    row += "|"
    row += "-"
    row += "|\n"
    rows += row

if len(successful) != len(all):
    rows += "\n*To add affected files to the whitelist, edit the `whitelist` variable in `.github/workflows/generate_diff.sh`*"

with open("Result.md", "w") as f:
    f.write(result.format(emoji=emoji, successrate=successrate, total_count=total_count, 
                          problem_count=problem_count, explanation=explanation, rows=rows))
    
os.environ["EXITCODE"] = "1" if len(successful) != len(all) else "0"
