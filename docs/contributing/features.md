---
title: "Contributing Features"
description: "How to write a feature README and info.yaml for Garden Linux features"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: docs/contributing/features.md
github_target_path: docs/contributing/features.md
---

# Contributing Features

Every feature under `features/` must have a `README.md` that describes what the
feature does, which files it provides, and how it relates to other features. This
page defines the authoring standard for those READMEs.

It does not talk in-depth about the builder feature `info.yaml`, read the
[`info.yaml` file structure](/reference/features/#info-yaml-file-structure) to get
familiar.
For the file-type semantics of `pkg.include`, `exec.config`, `file.include` and
the other builder file types, see the [feature file reference](/reference/features/)
To get to know feature types (`platform`, `element`, `flag`), the dependency graph and
composition rules, see [Features](/explanation/features).

## Scaffolding the Files table

Run the scaffold script to generate a `### Files` table and a `### Related features`
skeleton for a given feature:

```bash
bin/gl-feature-readme-scaffold features/<name>
```

Paste the output into the README, then fill in the Purpose stubs and the prose
sections. The script reads `info.yaml` for `type` and dependency lists, walks the
feature directory for files (excluding `README.md`), and prints stub Purpose entries
pre-linked to the [feature file reference](/reference/features/).

## Standard README structure

Each feature README must follow this template. Each file in the `### Files` table
links to the file on GitHub (latest `main`); the builder file-type reference, if
applicable, follows as `([ref](…))`.

```markdown
---
title: "Feature: <name>"
related_topics:
  - /how-to/custom-feature
  - /reference/features/
  - /explanation/features
github_org: gardenlinux
github_repo: gardenlinux
github_source_path: features/<name>/README.md
github_target_path: docs/reference/features/<name>.md
---

## Feature: <name>

### Description
One or two sentences on what this feature does, in user-facing terms.
Link glossary terms on first use, e.g.
[platform](/reference/glossary.html#platform),
[flavor](/reference/glossary.html#flavor).

### What it does
Expanded description of the capability or configuration this feature adds to
the image. Reference related docs where useful.

### How it works
<!-- Optional. Include only when behavior is non-trivial — boot flow, systemd
     units, partition changes, ordering constraints, etc. Omit for features
     that only install packages or drop config files. -->

### Files
Files present in this feature and their purpose.
See the [feature file reference](/reference/features/) for the semantics of
each file type.

| File | Purpose |
|---|---|
| [`info.yaml`](/reference/features/#info-yaml-file-structure) | Declares `type: <type>`. |
| [`pkg.include`](/reference/features/#pkg-include) | Installs `<package list>`. |
| [`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/<name>/exec.config) ([ref](/reference/features/#exec-config-exec-early-exec-late-exec-post)) | <what this script does> |
| [`file.include/etc/example.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/<name>/file.include/etc/example.conf) ([`file.include`](/reference/features/#file-include)) | <what this file configures> |
| ... | ... |

### Related features
<!-- Mandatory when this feature includes, excludes, or closely pairs with
     others. Derived from info.yaml; prose for human readers. -->
- [`<feature>`](/reference/features/<feature>) — <relationship / why included or excluded>

<!-- If no relationships: state "This feature has no include or exclude
     relationships." -->

### Further reading
<!-- Add platform how-to, ADR, explanation, or compliance reference as relevant -->

## Related topics

<RelatedTopics />
```

## Section rules

| Section | Mandatory | Notes |
|---|---|---|
| Frontmatter | yes | Never change `github_target_path` |
| `### Description` | yes | Plain prose; no `<website-feature>` tag |
| `### What it does` | yes | Replaces old `### Features` |
| `### How it works` | no | Only for non-trivial behavior |
| `### Files` | yes | Files only (no directory rows); link file types |
| `### Related features` | yes | State "none" if feature has no relationships |
| `### Further reading` | no | Recommended; always include if there are relevant docs |

## Inline linking rules

Every backtick-quoted feature name or file name in prose must be a hyperlink.

**Other features:** link to the rendered reference page.

```markdown
[`cloud`](/reference/features/cloud)
[`_prod`](/reference/features/_prod)
```

Do not link a feature's own name when it refers to itself — a self-link is circular.

**Top-level feature files** (e.g. `exec.config`, `convert.qcow2`, `fstab`): link to the
file on GitHub.

```markdown
[`exec.config`](https://github.com/gardenlinux/gardenlinux/blob/main/features/<name>/exec.config)
[`convert.qcow2`](https://github.com/gardenlinux/gardenlinux/blob/main/features/<name>/convert.qcow2)
```

**`file.include` as a concept** (no path component): link to the builder file-type reference.

```markdown
[`file.include`](/reference/features/#file-include)
```

**`initrd.include` directory**: link to the directory tree on GitHub.

```markdown
[`initrd.include`](https://github.com/gardenlinux/gardenlinux/tree/main/features/<name>/initrd.include)
```

**Subtree paths** (e.g. `file.include/etc/example.conf` in prose): link directly to
the file on GitHub.

```markdown
[`file.include/etc/example.conf`](https://github.com/gardenlinux/gardenlinux/blob/main/features/<name>/file.include/etc/example.conf)
```

## Related topics

<RelatedTopics />
