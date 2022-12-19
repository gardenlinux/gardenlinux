## Feature: fedramp
### Description
<website-feature>
This features adjusts Garden Linux to be complaint to the requirements of Fedramp.
</website-feature>

### Features
This `fedramp` feature represents a meta feature that includes multiple sub features like `aide` or `firewall`. Working with sub features provides an easy overview, adjustment and administration for each sub feature. While only including all sub features full fills the needed requirements for FedRAMP, it is in an operators decision to adjust sub features to his needs. This allows changes to be as near as possible to FedRAMP, even it may not fit the FedRAMP requirements. This feature includes further subfeatures.

### Unit testing
The FedRAMP unit test is based on a simple [simple shell script](tests/test.sh) and is executed by a `PyTest` wrapper. This tests will be proceeded for artifacts that are built with the `fedramp` feature and will validate all options, whether a sub feature is included or not.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|aide,clamav,firewall|
|excluded_features|None|
