# Contributing to Garden Linux

## Code of conduct

All members of the Garden Linux community must abide by the [CNCF Code of Conduct](https://github.com/cncf/foundation/blob/master/code-of-conduct.md). Only by respecting each other can we develop a productive, collaborative community. Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by contacting gardenlinux.opensource@sap.com and/or a Garden Linux project maintainer.

## Contributing

Garden Linux uses GitHub to manage reviews of pull requests.

If you are a new contributor see: [Steps to Contribute](#Steps-to-Contribute)

If you have a trivial fix or improvement, go ahead and create a pull request.

If you plan to do something more involved, first discuss your ideas on our [mailing list](#Mailing-List). This will avoid unnecessary work and surely give you and us a good deal of inspiration.

## Steps to Contribute

Should you wish to work on an issue, please claim it first by commenting on the GitHub issue that you want to work on it. This is to prevent duplicated efforts from contributors on the same issue.

If you have questions about one of the issues, with or without the tag, please comment on them and one of the maintainers will clarify it.

We kindly ask you to follow the [Pull Request Checklist](#Pull-Request-Checklist) to ensure reviews can happen accordingly.

## Contributing Code

You are welcome to contribute code to Garden Linux in order to fix a bug or to implement a new feature.

The following rules govern code contributions:

1. Contributions must be licensed under the MIT License.
1. You need to sign the Developer Certificate of Origin.

## Contributing Documentation

You are welcome to contribute documentation and code to Garden Linux.

The following rules govern documentation contributions:

1. Contributions must be licensed under the Creative Commons Attribution 4.0 International License.
1. You need to sign the Developer Certificate of Origin.

## Developer Certificate of Origin

Due to legal reasons, contributors will be asked to accept a Developer Certificate of Origin (DCO) before they submit the first pull request to this projects, this happens in an automated fashion during the submission process. We use the standard DCO text of the Linux Foundation.

## GIT Branch Naming Convention

By contributing to Garden Linux please make sure to take care of our git branch naming convention. All new branches should provide a prefix (mostly `feature/`) followed by a reference to an issue and a summary.

**Example**:

`feature/<issue-id>-<summary>`

which could look like:

`feature/1337-add-fancy-stuff`

This example represents the prefix `feature`, followed by the referenced GitHub issue `1337` with a summary.

Next to this, more specific prefixes (unlike only `feature/`) may be used.

| Prefix | Usage |
|---|---|
| feature/ | Adding new feature(s) (in code) to Garden Linux (generic) |
| doc/ | Adding/Changing documentation in Garden Linux |
| enhancement/ | Enhancements in Garden Linux that may change code, doc, features, etc. |
| cleanup/ | Code cleanup (e.g. remove legacy/deprecated content |
| ci/ | Changes related to our internal CI/CD pipeline (only used by Garden Linux members) |
| archive/ | Stale branches that are need to keep (not used for new branches) |
| release/ | Only used by Garden Linux members. By newer release used as a tag instead of branch |


## Pull Request Checklist

1. Branch from the master branch and, if needed, rebase to the current master branch before submitting your pull request. If it doesn’t merge cleanly with master you may be asked to rebase your changes.

1. Commits should be as small as possible, while ensuring that each commit is correct independently (i.e., each commit should compile and pass tests).

1. Commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification so that we automatically produce meaningful release notes.

1. Test your changes as thoroughly as possible before you commit them. Preferably, automate your test by unit and/or platform tests. If tested manually, provide information about the test scope in the PR description.

1. Create Work In Progress [WIP] pull requests only if you need a clarification or an explicit review before you can continue your work item.

1. If your patch is not getting reviewed or you need a specific person to review it, you can @-reply a reviewer asking for a review in the pull request or a comment, or you can ask for a review on our [mailing list](#Mailing-List).

1. Post review:

    1. If a review requires you to change your commit(s), please test the changes again.
    1. Amend the affected commit(s) and force push onto your branch.
    1. Set respective comments in your GitHub review to resolved.
    1. Create a general PR comment to notify the reviewers that your amendments are ready for another round of review.

1. When merging into main, make sure that all commits belonging to a pull-request get squashed into one single commit that gets merged.

## Issues and Planning

We use GitHub issues to track bugs and enhancement requests. Please provide as much context as possible when you open an issue. The information you provide must be comprehensive enough to reproduce that issue for the assignee. Therefore, contributors may use but aren’t restricted to the issue template provided by the Garden Linux maintainers.

## Mailing List

gardenlinux@googlegroups.com

The mailing list is hosted through Google Groups. To receive the lists' emails, join the group, as you would any other Google Groups at https://groups.google.com/g/gardenlinux.
