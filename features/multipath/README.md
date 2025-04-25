## Feature: aide
### Description
<website-feature>
This feature installs multipath 
</website-feature>

### Features
This feature installs multipath and creates a config file for it. Multipath is needed by iscsi as well as nvme over tcp .

### Unit testing
The related unit tests ensure that the needed packages are installed and the cron job will run nightly.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|server|
|excluded_features|None|
