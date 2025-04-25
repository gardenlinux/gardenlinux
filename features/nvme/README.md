## Feature: aide
### Description
<website-feature>
This feature installs nvme cli
</website-feature>

### Features
This feature installs nvm-cli as well as a systemd unit that creates /etc/nvme/hostnqn and /etc/nvme/hostid just as apt would after installing the package.

### Unit testing
The related unit tests ensure that the needed packages are installed and the cron job will run nightly.

### Meta
|||
|---|---|
|type|element|
|artifact|None|
|included_features|server|
|excluded_features|None|
