# =============================================================================
# VARIABLES
# =============================================================================

# Use python3 by default. Can be overridden, e.g., make PYTHON=python3.11 install
PYTHON ?= python3
VENV_DIR ?= .venv
VENV_BIN = $(VENV_DIR)/bin
PIP = $(VENV_BIN)/pip

# =============================================================================
# CONFIGURATION
# =============================================================================

# Default target, executed when you just run "make"
.DEFAULT_GOAL := help

# Declare targets that are not files
.PHONY: help install install-dev test clean clean-venv venv build

# =============================================================================
# CORE TARGETS
# =============================================================================

help: ## ✨ Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: venv ## 📦 Install the library in editable mode
	@echo "--- Installing project dependencies ---"
	@$(PIP) install -e .

install-dev: venv ## 🛠️ Install development tools (like pytest)
	@echo "--- Installing development dependencies ---"
	@$(PIP) install -e ".[dev]"

test: install-dev ## 🔬 Run tests with pytest
	@echo "--- Running tests ---"
	@$(VENV_BIN)/pytest -v

build: install ## 🏗️ Build the package
	@echo "--- Building package ---"
	@$(PIP) install --upgrade build
	@$(VENV_BIN)/python -m build

clean: ## 🧹 Clean up cache files
	@echo "--- Cleaning Python cache files ---"
	@find . -type f -name "*.py[co]" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@find . -type d -name "*.egg-info" -exec rm -rf {} +

clean-venv: ## 🗑️ Remove the virtual environment
	@echo "--- Removing virtual environment ---"
	@rm -rf $(VENV_DIR)

# =============================================================================
# UTILITY TARGETS (Internal)
# =============================================================================

venv: pyproject.toml
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "--- Creating virtual environment ---"; \
		$(PYTHON) -m venv $(VENV_DIR); \
		echo "--- Updating pip ---"; \
		$(PIP) install --upgrade pip; \
	fi