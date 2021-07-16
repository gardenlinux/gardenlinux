# Tests

## Prerequisites

Python 3.8

to install on debian buster:
```
apt-get update && apt install python3 -t bullseye
```

install pipenv and install dependencies:
```
apt-get update && apt-get install pipenv
pipenv install --dev
```

## auto-format using black

in order to auto format the source code run

```
pipenv run black .
```

## run static checks

```
pipenv run flake8 .
```

## Run tests

on GCP:

```
pipenv run pytest --iaas gcp integration/
```

on AWS:

```
pipenv run pytest --iaas aws integration/
```

The test configuration is read from `test_config.yaml`

# Run Full tests including image upload (AWS)

1. Start docker container

```
docker run -it --rm  -v $HOME/src/gardenlinux:/gardenlinux -v $HOME/.aws:/root/.aws -v $HOME/.ssh:/root/.ssh gardenlinux/integration-test:463.0 bash
cd /gardenlinux/tests
pipenv install --dev
pipenv shell

```


