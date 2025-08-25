# 6. Garden Linux versioning

Date: 2025-08-25

## Status

Accepted

## Context

The Gardenlinux version scheme is based on a 2 segment version identifier scheme under the format DDDD.P where:
- DDDD represents the number of days since 31st of March 2020
- P minor/patch version

The format is not extremely strict - no padding is being used e.g. 0934.01 doesn't exist, rather 934.1 was released.
The Gardenlinux version identifier is very similar to what the CalVer[^1] convention is proposing, except the 3 numeric 
segments and the modifier.

Because of different limitations from our main customer (Gardener) and as most OSS is using SemVer[^2] as the go-to 
versioning system, it was proposed that Gardenlinux should also switch to SemVer.

## Decision

Unfortunately SemVer is not really suitable for a such a project.
In order to align more with the requests, the decision has been made to:
- keep the current system we use - similar to what CalVer is proposing, even if you can't easily derive a lot of information from the version itself
- switch to a 3 numberical segments identifier for the version - major/minor/micro(patch)
  <p>this would also make the version identifier be semver compliant</p>
  <p>this would make Gardener happy and we'd have a 1:1 correlation between Gardener and our releases</p>

### Actual changes proposed for Gardenlinux:
- go from a 2 segment numerical version to a 3 semver compliant version by
  - appending ".0" to the currently used versions - how Gardener does it internally
    <p>based on how we released historically, we won't have a release with a x.y.1 version</p>
- use this system starting with the next major release (current version at time of writing 1973.0)
- use this with the nightly as soon as possible

## Consequences

- 1:1 mapping between the Gardener OS versions and the actual GL release
- No more special version handling in GLCI for Gardener
- IronCore will need to adjust their workflows when creating their custom images
- The CCloud GL version will need adjusting but it will benefit SCI overall as their custom images are used in Gardener/IronCore environments

## Notes

[^1]: https://calver.org
[^2]: https://semver.org
