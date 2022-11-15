## Feature: _prod
### Description
<website-feature>
This feature flag creates an explicit declared production artifact of Garden Linux.
</website-feature>

### Features
This Feature is used to build a productive Image with /usr Read-Only and without apt, dpkg, etc.

### Unit testing
This feature does not support unit tests.

### Meta
|||
|---|---|
|type|flag|
|artifact|None|
|included_features|_nopkg,_readonly|
|excluded_features|None|
