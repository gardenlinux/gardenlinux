SHELL := /usr/bin/env bash
.SHELLFLAGS := -euo pipefail -c

# ---------------------------------------------------------------------------
# Configuration — all variables can be overridden from the environment
# ---------------------------------------------------------------------------

# docs-ng repository to clone
DOCS_NG_REPO    ?= https://github.com/gardenlinux/docs-ng.git
# Branch / tag of docs-ng to use
DOCS_NG_REF     ?= main
# This repo's name as it appears in docs-ng's repos-config.json
REPO_NAME       ?= gardenlinux
# Absolute path to the root of THIS repository (parent of docs/)
LOCAL_DOCS_PATH ?= $(abspath $(CURDIR)/..)

# Build directory: cloned docs-ng lives at the repo root (NOT inside docs/,
# to avoid the aggregator picking it up when copying the docs/ tree)
BUILD_DIR := $(abspath $(CURDIR)/../.docs-ng-build)

# Sentinel file that marks a completed setup
SETUP_SENTINEL := $(BUILD_DIR)/.setup-done

# ---------------------------------------------------------------------------

.PHONY: help setup aggregate aggregate-repo check linkcheck spelling woke clean

.DEFAULT_GOAL := help

help:
	@echo "Garden Linux Documentation CI"
	@echo ""
	@echo "Usage:  make [TARGET] [VAR=value ...]"
	@echo ""
	@echo "Targets:"
	@echo "  aggregate      Clone docs-ng and aggregate documentation from local repo"
	@echo "  aggregate-repo Aggregate documentation from local repo only"
	@echo "  check          Run all quality checks  (aggregate + linkcheck + spelling + woke)"
	@echo "  linkcheck      Check links with lychee"
	@echo "  spelling       Check spelling with codespell"
	@echo "  woke           Check inclusive language with woke"
	@echo "  setup          Clone docs-ng and install dependencies (runs automatically)"
	@echo "  clean          Remove the build directory"
	@echo ""
	@echo "Configuration variables (override via environment or make VAR=value):"
	@printf "  %-20s %s\n" "DOCS_NG_REPO"    "$(DOCS_NG_REPO)"
	@printf "  %-20s %s\n" "DOCS_NG_REF"     "$(DOCS_NG_REF)"
	@printf "  %-20s %s\n" "REPO_NAME"       "$(REPO_NAME)"
	@printf "  %-20s %s\n" "LOCAL_DOCS_PATH" "$(LOCAL_DOCS_PATH)"
	@echo ""
	@echo "Examples:"
	@echo "  make check"
	@echo "  make check DOCS_NG_REF=feature/my-branch"
	@echo "  make linkcheck"
	@echo "  make clean && make check"

# ---------------------------------------------------------------------------
# Setup: clone docs-ng and install all dependencies
# ---------------------------------------------------------------------------

setup: $(SETUP_SENTINEL)

$(SETUP_SENTINEL):
	@echo "==> Cloning docs-ng ($(DOCS_NG_REPO)@$(DOCS_NG_REF)) into $(BUILD_DIR)..."
	rm -rf "$(BUILD_DIR)"
	git clone --depth 1 --branch "$(DOCS_NG_REF)" "$(DOCS_NG_REPO)" "$(BUILD_DIR)"
	@echo "==> Installing Node.js dependencies..."
	cd "$(BUILD_DIR)" && pnpm install
	@echo "==> Installing Python dependencies..."
	cd "$(BUILD_DIR)" && pip install -r requirements.txt
	cd "$(BUILD_DIR)" && pip install git+https://github.com/gardenlinux/glrd.git@v4.1.0
	cd "$(BUILD_DIR)" && pip install git+https://github.com/gardenlinux/python-gardenlinux-lib.git@0.10.20
	touch "$@"
	@echo "==> Setup complete."

# ---------------------------------------------------------------------------
# Aggregate: patch repos-config.json to point at local repo, then aggregate
# ---------------------------------------------------------------------------

aggregate: setup
	@echo "==> Patching repos-config.json for repo '$(REPO_NAME)' -> file://$(LOCAL_DOCS_PATH)"
	@python3 -c "\
import json, sys; \
config_path = '$(BUILD_DIR)/repos-config.json'; \
config = json.load(open(config_path)); \
repos = [r for r in config['repos'] if r['name'] == '$(REPO_NAME)']; \
(sys.exit('ERROR: repo $(REPO_NAME) not found in repos-config.json')) if not repos else None; \
repos[0].update({'url': 'file://$(LOCAL_DOCS_PATH)', 'ref': 'HEAD'}); \
repos[0].pop('commit', None); \
json.dump(config, open(config_path, 'w'), indent=2); \
print('Patched $(REPO_NAME): url=file://$(LOCAL_DOCS_PATH), ref=HEAD'); \
"
	@echo "==> Running aggregation..."
	cd "$(BUILD_DIR)" && python3 src/aggregate.py
	@echo "==> Aggregation complete."

aggregate-repo: setup
	@echo "==> Aggregating documentation for local repositroy '$(REPO_NAME)'"
	cd "$(BUILD_DIR)" && python3 src/aggregate.py --repo $(REPO_NAME)

# ---------------------------------------------------------------------------
# Quality checks
# ---------------------------------------------------------------------------

check: linkcheck spelling woke
	@echo "==> All quality checks passed."

linkcheck:
	@echo "==> Running link check..."
	cd "$(BUILD_DIR)" && pnpm run docs:linkcheck

spelling:
	@echo "==> Running spelling check..."
	cd "$(BUILD_DIR)" && pnpm run docs:spelling

woke:
	@echo "==> Running inclusive language check..."
	cd "$(BUILD_DIR)" && pnpm run docs:woke

# ---------------------------------------------------------------------------
# Run a development server
# ---------------------------------------------------------------------------

dev:
	@echo "==> Running link check..."
	cd "$(BUILD_DIR)" && pnpm run docs:dev

# ---------------------------------------------------------------------------
# Building the complete documenation
# ---------------------------------------------------------------------------

build: aggregate
	@echo "==> Running link check..."
	cd "$(BUILD_DIR)" && pnpm run docs:build

# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

clean:
	@echo "==> Removing build directory $(BUILD_DIR)..."
	rm -rf "$(BUILD_DIR)"
	@echo "==> Clean complete."
