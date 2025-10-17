# 14. Allowed Merge Types for Garden Linux

Date: 2025-10-17

## Status

Accepted

## Context

Maintaining traceability between pull requests (PRs) and the commits they introduce is essential for the integrity and auditability of Garden Linux's development process.

When using **rebase** merges, individual commits are applied directly to the target branch without referencing the originating PR, making it difficult to track the source and rationale behind changes.

**Example Commit History: Rebase Merge**
```
* 12af822 Next unrelated commit
* 9f8e7c1 Fix typo in docs
* 8a7b6d2 Add new feature
* 7c6d5e3 Refactor module
* 5d4e3f2 Previous commit
```
_No indication of PR number or context._

In contrast, both **merge commits** and **squash merges** create a single commit that explicitly references the PR, preserving a clear link between code changes and their review history.

**Example Commit History: Merge Commit**
```
* 1a2b3c4 Merge pull request #42 from feature-branch
|\
| * 9f8e7c1 Fix typo in docs
| * 8a7b6d2 Add new feature
| * 7c6d5e3 Refactor module
* | 5d4e3f2 Previous commit
```
_The merge commit references the PR and groups related changes._

**Example: Squash Merge**
```
* 2b3c4d5 Add new feature and fix typo (#42)
* 5d4e3f2 Previous commit
```
_All changes from the PR are combined into a single commit, referencing the PR._

Often, the pull request contains useful context such as discussions, or a link to an issue that this change resolves.
Being able to trace this from a given change is critical for compliance.

## Decision

We will only **allow merge commits and squash merges** when integrating PRs into the main branches of Garden Linux. **Rebase merges are disallowed**, as they do not provide sufficient traceability between commits and their originating PRs.

## Consequences
By restricting merge types to merge commits and squash merges, every change merged into Garden Linux will be traceable to its PR, facilitating easier audits, reviews, and historical analysis. Contributors must ensure that their PRs are merged using one of the allowed methods to maintain this standard.

While some contributors may prefer rebase merges for aesthetic reasons—such as a linear commit history without merge commits—the need for traceability and accountability takes precedence in this project. The chosen merge strategies ensure that the origin and context of each change are preserved, even if this results in a less linear commit graph.
