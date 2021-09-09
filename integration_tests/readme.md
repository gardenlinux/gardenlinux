### Integration Tests

This directory contains the files that make up the integration test suites for the various providers.

### Usage

All existing integration tests can be started by simply running

> pytest

from within this directory. By default, this will use our central credentials management to obtain the necessary credentials to authenticate against the individual cloud providers. You can use pre-existing local credentials (where supported) by calling

> pytest --local

instead. __Note__: This requires a __successful__ login to the respective cloud provider's CLI (e.g. `Google Cloud SDK`) before running the tests.
Instead of running all tests at once, they can also be run individually by provider by simply passing the directory as argument to pytest, e.g.:

> pytest azure --local