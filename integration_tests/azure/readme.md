### Azure Integration Tests

This directory contains two files:
1. `azure_test.py`: contains the test-cases for `Azure`
2. `conftest.py`: contains the `Azure`-specific pytest-fixtures

### Usage

The integration tests can be started by running

> pytest .

from within this directory. By default, this will use our central credentials management to obtain the credentials to use to authenticate against `Azure`. You can use pre-existing local Credentials by calling

> pytest . --local

instead. __Note__: This requires a __successful__ login to the `Azure CLI` (e.g. using `az login`) before running the tests.