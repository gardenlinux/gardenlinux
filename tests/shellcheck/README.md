# Shellcheck Tests

Shellcheck tests must be executed explicitly via `pytest shellcheck` (see [Running the Tests](#running-the-tests)),
and will **not** be executed as part of other pytests (e.g. the integration tests).

## Prerequisites

The tests **do not** require a running Garden Linux instance. Neither do the test require the repository to be in a buildable state.  
[Shellcheck](https://github.com/koalaman/shellcheck) is a requirement. 
It must be installed on the test system on which the shellcheck tests should run.  


**tl;dr** snippet to install the requirements for the shellcheck tests:
```
python3 -m venv env
source env/bin/activate
pip install pytest

# A shellcheck package can be installed via debian apt repos (e.g. bookworm)
sudo apt-get install shellcheck
``` 

## Running the Tests
Shellcheck tests are executed from the `gardenlinux-repo/tests` folder.

```
pytest shellcheck
```

## Running Shellcheck manually

`shellcheck <path-to-file>` to run shellcheck manually and get output for a single file.
You can also integrate shellcheck in your editor. 
Checkout the github readme from the [koalaman/shellcheck](https://github.com/koalaman/shellcheck#in-your-editor) repo for more information.

## Configuration

### Ignoring Shellcheck errors/warnings
The text file `tests/shellcheck/error.ignore` is a line separated list of errors that must be ignored by the shellcheck pytests.

```
# Comments start with '#' and will be ignored

SC1090

```

### Ignoring files

The text file `tests/shellcheck/file.ignore` is a line-separated list of paths starting from the Garden Linux repo root, that must be ignored in the shellcheck pytests.

```
# Comments start with '#' and will be ignored

# All files must be specified relative to the root dir of this repository
bin/
ci/

# Explicitly ignore single file
docker/build/install-cfssl.sh
```



