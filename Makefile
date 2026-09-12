# ========================
# Environment config
# ========================
SHELL := /bin/bash

APP_ENV_FILES :=
DOCKER_ENV_FILES :=

ifneq ($(wildcard .env),)
  APP_ENV_FILES += .env
endif

ifneq ($(wildcard .env.local),)
  APP_ENV_FILES += .env.local
endif

ifneq ($(wildcard .env.kc),)
  APP_ENV_FILES +=  .env.kc
endif

UV_RUN := make set-python-version;\
	PYTHONPATH=src:examples uv run

DC := docker compose
PYTHON_VERSION_FILE := .python-version
PYTHON_VER := $(shell [ -f $(PYTHON_VERSION_FILE) ] && tr -d '\n' < $(PYTHON_VERSION_FILE))
CURRENT_VER := $(shell python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')

define load_env
	set -a; \
	for f in $(APP_ENV_FILES); do \
		[ -f "$$f" ] && . "$$f"; \
	done; \
	set +a
endef


# ========================
# PHONY Targets
# ========================
.PHONY: default help install clean run tests mcp-smoke verify \
        pre-commit pre-commit-install pre-commit-update \
        script-% set-python-version format format-check lint lint-fix \
        typecheck lock-check audit build \
        release-bump release-bump-tag

UV := uv
RUFF := $(UV) run ruff
TY := $(UV) run ty



default: help


# ========================
# Help
# ========================
help:
	@echo ""
	@echo "📦 Project Makefile Commands:"
	@echo "---------------------------------------------"
	@awk 'BEGIN {FS = ":.*?#"} /^[a-zA-Z_-]+:.*?#/ { printf "  \033[36m%-30s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ========================
# Project Setup
# ========================
install: ## Install dependencies and pre-commit hooks
	@make set-python-version
	@uv sync
	@uv run pre-commit install

clean: ## Remove .pyc files and pre-commit cache
	@find . -type f -name '*.pyc' -delete
	@find . -type d -name '__pycache__' -exec rm -r {} +
	@uv run pre-commit clean

# ========================
# Run App
# ========================
run: ## Run MCP server for local development
	@$(load_env); $(UV_RUN) pykeycloak-mcp

script-%:
	$(load_env); $(UV_RUN) $*

scripte:
	$(load_env); $(UV_RUN) ${SCRIPT}

scriptea:
	@find ./examples -maxdepth 1 -type f -name "[!_]*.py" -print0 | while IFS= read -r -d '' file; do \
		echo "Running $$file..."; \
		$(load_env); $(UV_RUN) "$$file"; \
	done


# ========================
# Formatting & Linting
# ========================
format: ## Format code using Ruff
	@$(RUFF) format .

format-check: ## Check Ruff formatting without changing files
	@$(RUFF) format --check .

lint: ## Lint code using Ruff
	@$(RUFF) check .

lint-fix: ## Fix lint issues using Ruff
	@$(RUFF) check . --fix

typecheck: ## Check source types using ty
	@$(TY) check src

lock-check: ## Verify uv.lock matches project metadata
	@$(UV) lock --check

audit: ## Audit locked dependencies for known vulnerabilities
	@$(UV) export --frozen --format requirements.txt --all-groups --no-emit-project -o /tmp/requirements-audit.txt
	@$(UV) run pip-audit --strict --requirement /tmp/requirements-audit.txt --no-deps

build: ## Build wheel and source distribution
	@$(UV) build

verify: ## Run deterministic local verification checks
	@$(MAKE) lock-check
	@$(MAKE) lint
	@$(MAKE) format-check
	@$(MAKE) typecheck
	@$(MAKE) tests
	@$(MAKE) test-with-coverage
	@$(MAKE) mcp-smoke
	@$(MAKE) build


# ========================
# Pre-commit
# ========================
pre-commit: ## Run all pre-commit hooks
	@uv run pre-commit run --all-files

pre-commit-install: ## Install pre-commit hooks
	@uv run pre-commit install

pre-commit-update: ## Update pre-commit hooks
	@uv run pre-commit autoupdate

# ========================
# Tests
# ========================
tests: ## Run all tests
	@$(load_env); $(UV_RUN) pytest tests -vv -s

test-unit: ## Run unit tests
	@$(load_env); $(UV_RUN) pytest tests/unit -vv -s

test-integration: ## Run integration tests
	@$(load_env); $(UV_RUN) pytest tests/integration -vv -s

test-functional: ## Run functional tests
	@$(load_env); $(UV_RUN) pytest tests/functional -vv -s

test-with-coverage: ## Run all tests with the configured coverage threshold
	@$(load_env); $(UV_RUN) pytest tests --cov --cov-report=term-missing -vv -s

mcp-smoke: ## Smoke test for the packaged MCP server
	@make set-python-version
	@export KEYCLOAK_BASE_URL=http://localhost; $(UV_RUN) python -m py_compile src/pykeycloak_client/mcp_server.py
	@export KEYCLOAK_BASE_URL=http://localhost; $(UV_RUN) python -c "from pykeycloak_client import mcp_server; print('server:', mcp_server.mcp.name); mcp_server.keycloak_register(key='smoke', realm_name='smoke-realm', client_uuid='00000000-0000-0000-0000-000000000000', client_id='smoke-client', client_secret='smoke-secret'); keys = mcp_server.keycloak_list_keys()['keys']; assert 'smoke' in keys, f\"Expected 'smoke' in keys, got {keys}\"; methods = mcp_server.keycloak_list_methods('smoke')['methods']; assert 'auth' in methods and 'users' in methods, 'Expected core services in methods'; print('services:', ', '.join(sorted(methods.keys()))); print('mcp-smoke: ok')"

release-bump: ## Sync pyproject version from GITHUB_REF_NAME (vX.Y.Z)
	@python3 bin/sync_version_from_tag.py

release-bump-tag: ## Sync pyproject version from TAG=vX.Y.Z
	@if [ -z "$(TAG)" ]; then \
		echo "TAG is required. Example: make release-bump-tag TAG=v0.7.4"; \
		exit 1; \
	fi
	@python3 bin/sync_version_from_tag.py --tag "$(TAG)"


# =========
# Helpers
# ==========

set-python-version:
	@if [ ! -f "$(PYTHON_VERSION_FILE)" ]; then \
		echo "Missing $(PYTHON_VERSION_FILE); create it with a supported Python version."; \
		exit 1; \
	fi
	@if [ "$(CURRENT_VER)" != "$(PYTHON_VER)" ]; then \
		uv python pin "$(PYTHON_VER)"; \
	fi
