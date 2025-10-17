GIT_DIR := $(shell git rev-parse --show-toplevel --show-superproject-working-tree | tail -n1)
ROOT_DIR := "$(GIT_DIR)/tests-ng"

.PHONY: install install-dev format-black format-isort format lint-black lint-isort lint-pyright lint help

# help: Show this help message
help:
	@echo "Available targets:"
	@grep -E '^# [a-zA-Z0-9_-]+:' $(MAKEFILE_LIST) | sed 's/^# \([a-zA-Z0-9_-]*\): \(.*\)/  \1 - \2/' | sort

# install: Install the package dependencies
install:
	pip install -r $(ROOT_DIR)/util/requirements.txt

# install-dev: Install the package and dev dependencies
install-dev:
	pip install -r $(ROOT_DIR)/util/requirements-dev.txt

# lint-black: Check code formatting with black
lint-black: install-dev
	black --check --diff --color $(ROOT_DIR)

# lint-isort: Check import sorting with isort
lint-isort: install-dev
	isort --check --diff --color $(ROOT_DIR)

# lint-pyright: Run type checking with pyright
lint-pyright: install install-dev
	pyright --warnings $(ROOT_DIR)

# lint: Run all linting checks (black, isort, pyright)
lint: install-dev lint-black lint-isort lint-pyright

# format-black: Format code with black
format-black: install-dev
	black $(ROOT_DIR)

# format-isort: Sort imports with isort
format-isort: install-dev
	isort $(ROOT_DIR)

# format: Format code with black and sort imports with isort
format: install-dev format-black format-isort
