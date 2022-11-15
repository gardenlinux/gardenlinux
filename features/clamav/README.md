## Feature: clamav
### Description
<website-feature>
This feature installs and configures clamAV antivirus.
</website-feature>

### Features
Virus definitions will be updated by freshclam. A nightly virus scan is triggered by a cronjob which can be modified by editing:

```
file.include/var/spool/cron/crontabs/root
```

### Unit testing
Unit tests will ensure that the needed packages are present as well as a configured cronjob to run daily.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|None|
|excluded_features|None|
