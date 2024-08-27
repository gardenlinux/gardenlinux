# Shellcheck Tests

Shellcheck tests must be executed explicitly via `pytest shellcheck` (see [Running the Tests](#running-the-tests)),
and will **not** be executed as part of other pytests (e.g. the platform tests).
The tests **do not** require a running Garden Linux instance. 
Neither do the test require the repository to be in a buildable state. 

## Prerequisites

The `gardenlinux/platform-test` container has all dependencies installed that are required to run the shellcheck tests.
Build the container image from the base directory of this repository by running: 
```
make --directory=container build-platform-test
```

## Configuration Options

<details>

**Severity Level**  
determines for what kind of findings the shellcheck tests should fail.  
Starting from the most sensitive, to least sensitive, the available levels are: `error`, `warning`, `info`, `style`

```
pytest shellcheck --severity=error
```

**Ignoring Shellcheck errors/warnings**  
The text file `tests/shellcheck/error.ignore` is a line separated list of errors that must be ignored by the shellcheck pytests.

```
# Comments start with '#' and will be ignored

SC1090
```

**Ignoring files**  
The text file `tests/shellcheck/file.ignore` is a line-separated list of paths starting from the Garden Linux repo root, that must be ignored in the shellcheck pytests.

```
# Comments start with '#' and will be ignored

# All files must be specified relative to the root dir of this repository
bin/
ci/

# Explicitly ignore single file
docker/build/install-cfssl.sh
```
</details>

## Running the Tests

Start the container
- mount Garden Linux repository to /gardenlinux
```
docker run -it --rm -v `pwd`:/gardenlinux gardenlinux/platform-test:`bin/garden-version` /bin/bash
```

Run the rests
```
pytest shellcheck
```

## Running Shellcheck manually

`shellcheck <path-to-file>` to run shellcheck manually and get output for a single file.
You can also integrate shellcheck in your editor. 
Checkout the github readme from the [koalaman/shellcheck](https://github.com/koalaman/shellcheck#in-your-editor) repo for more information.

