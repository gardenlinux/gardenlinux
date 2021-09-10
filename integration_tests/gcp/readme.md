### GCP Integration Tests

This directory contains two files:
1. `gcp_test.py`: contains the test-cases for `GCP`
2. `conftest.py`: contains the `GCP`-specific pytest-fixtures

### Usage

The integration tests can be started by running

> pytest .

from within this directory. By default, this will use our central credentials management to obtain the credentials to use to authenticate against `GCP`. You can use pre-existing local credentials by calling

> pytest . --local

instead. __Note__: This requires a __successful__ login to the `Google Cloud SDK` using `gcloud auth application-default login` before running the tests.